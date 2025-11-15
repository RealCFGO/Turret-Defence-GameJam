import pygame
import math
import random
import sys
import os

from constants import *
from entities import Player, Bullet, Enemy, Boss, BossProjectile, Particle
from modules import Module
from upgrades import Upgrade
from dialogue import BossDialogue


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TURRET-DEFENCE")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)
        self.init_sounds()
        self.reset_game()
        
    def init_sounds(self):
        """Initialize sound effects from user-provided files"""
        pygame.mixer.init()
        
        sounds_dir = 'sounds'
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir)
            # Create instructions file
            with open(os.path.join(sounds_dir, 'REQUIRED_SOUNDS.txt'), 'w') as f:
                f.write("Place your sound files in this directory with these exact names:\\n\\n")
                f.write("shoot.wav - Sound when player fires a bullet\\n")
                f.write("hit.wav - Sound when bullet hits an enemy\\n")
                f.write("kill.wav - Sound when an enemy is killed\\n")
                f.write("levelup.wav - Sound when player levels up\\n")
                f.write("backgroundmusic.wav - Background music (will loop)\\n\\n")
                f.write("All files should be in WAV format.\\n")
                f.write("If a file is missing, no sound will play for that action.\\n")
        
        # Try to load sound effects
        try:
            self.shoot_sound = self.load_sound(os.path.join(sounds_dir, 'shoot.wav'))
            self.hit_sound = self.load_sound(os.path.join(sounds_dir, 'hit.wav'))
            self.kill_sound = self.load_sound(os.path.join(sounds_dir, 'kill.wav'))
            self.levelup_sound = self.load_sound(os.path.join(sounds_dir, 'levelup.wav'))
            
            # Load and start background music
            bg_music_path = os.path.join(sounds_dir, 'backgroundmusic.wav')
            if os.path.exists(bg_music_path):
                pygame.mixer.music.load(bg_music_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)  # Loop indefinitely
            else:
                print("Background music not found: sounds/backgroundmusic.wav")
        except Exception as e:
            print(f"Sound initialization: {e}")
    
    def load_sound(self, filepath):
        """Load a sound file if it exists"""
        if os.path.exists(filepath):
            try:
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(0.3)
                return sound
            except Exception as e:
                print(f"Failed to load {filepath}: {e}")
                return None
        return None
    
    def play_sound(self, sound):
        """Play a sound effect if available"""
        if sound:
            try:
                sound.play()
            except:
                pass
    
    def reset_game(self):
        """Reset game state for new game"""
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.boss = None
        self.boss_projectiles = []
        self.boss_pattern_counter = 0
        self.score = 0
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        self.game_over = False
        self.game_won = False
        self.paused = False
        self.upgrade_choices = []
        self.module_choices = []
        self.boss_dialogue = None
        self.boss_dialogue_time = 0
        self.start_time = pygame.time.get_ticks()
        self.last_spawn_time = 0
        self.spawn_interval = 2000
        self.game_time = 0
        self.difficulty_scale = 1.0
        self.mouse_held = False
        self.shield_hp = 0
        self.last_regen_time = 0
        self.last_fire_ring_time = 0
        self.last_shield_regen_time = 0
        self.last_overcharge_damage = 0
        self.last_phase_shift = 0
        self.phase_shift_active = False
        self.show_stats = True  # Always show stats panel, can minimize with TAB
        self.stats_minimized = False  # Stats panel minimized state
        
    def get_spawn_position(self):
        """Get random position on screen edge"""
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            return random.randint(0, SCREEN_WIDTH), -30
        elif edge == 1:  # Right
            return SCREEN_WIDTH + 30, random.randint(0, SCREEN_HEIGHT)
        elif edge == 2:  # Bottom
            return random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
        else:  # Left
            return -30, random.randint(0, SCREEN_HEIGHT)
            
    def spawn_enemy(self):
        """Spawn a random enemy"""
        x, y = self.get_spawn_position()
        enemy_type = random.choice(list(ENEMY_TYPES.keys()))
        self.enemies.append(Enemy(x, y, enemy_type, self.difficulty_scale))
        
    def update_difficulty(self):
        """Increase difficulty over time"""
        time_seconds = self.game_time / 1000
        self.difficulty_scale = 1.0 + (time_seconds / 30) * 0.1
        self.spawn_interval = max(300, 1500 - (time_seconds * 10))
        
    def add_exp(self, amount):
        """Add experience and check for level up"""
        self.exp += int(amount * self.player.exp_multiplier)
        if self.exp >= self.exp_to_next_level:
            self.level_up()
    
    def get_player_stats_text(self):
        """Get formatted player stats for display"""
        return [
            f"Damage: {int(self.player.damage)}",
            f"Fire Rate: {self.player.fire_rate:.1f}/sec",
            f"Bullet Speed: {int(self.player.bullet_speed)}",
            f"Max HP: {int(self.player.max_hp)}",
            f"EXP Multiplier: {self.player.exp_multiplier:.1f}x",
            f"Damage Taken: {int(self.player.damage_taken_multiplier * 100)}%"
        ]
            
    def apply_module_downsides(self):
        """Apply module downsides by reducing current stats"""
        if not self.player.modules:
            return
        
        module_id = self.player.modules[-1]  # Only apply the newly added module
        
        if module_id == 'explosive_rounds':
            self.player.fire_rate *= 0.8
        elif module_id == 'fire_ring':
            self.player.bullet_speed *= 0.85
        elif module_id == 'regeneration':
            self.player.max_hp = int(self.player.max_hp * 0.9)
            self.player.hp = min(self.player.hp, self.player.max_hp)
        elif module_id == 'homing_missiles':
            self.player.bullet_speed *= 0.8
        elif module_id == 'damage_aura':
            self.player.damage_taken_multiplier *= 1.3
        elif module_id == 'time_slow':
            self.player.fire_rate *= 0.7
        elif module_id == 'exp_magnet':
            self.spawn_interval = int(self.spawn_interval * 0.85)
        elif module_id == 'sniper_mode':
            self.player.fire_rate *= 0.5
        elif module_id == 'vampiric':
            self.player.max_hp = int(self.player.max_hp * 0.8)
            self.player.hp = min(self.player.hp, self.player.max_hp)
        elif module_id == 'ricochet':
            self.player.bullet_speed *= 0.6
        elif module_id == 'armor_plating':
            self.player.damage_taken_multiplier *= 0.7
            self.player.bullet_speed *= 0.7
        elif module_id == 'laser_sight':
            self.player.fire_rate *= 0.85
        elif module_id == 'shield_generator':
            self.player.fire_rate *= 0.85
        elif module_id == 'phase_shift':
            self.player.fire_rate *= 0.8
        elif module_id == 'rapid_fire':
            self.player.damage *= 0.75
        elif module_id == 'chain_lightning':
            self.player.damage *= 0.8
    
    def level_up(self):
        """Level up and show upgrade/module choices"""
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.2)
        
        # Boss dialogue every 5 levels
        if self.level % 5 == 0 and self.level < 30:
            dialogue_index = (self.level // 5) - 1
            if dialogue_index < len(BossDialogue.DIALOGUES):
                self.boss_dialogue = BossDialogue.DIALOGUES[dialogue_index]
                self.boss_dialogue_time = pygame.time.get_ticks()
        
        # Boss fight at level 30
        if self.level == 30:
            self.start_boss_fight()
            return
        
        self.paused = True
        
        # Every 3 levels, offer modules instead of upgrades
        if self.level % 3 == 0:
            self.module_choices = Module.get_random_modules(self.player.modules, 3)
            self.upgrade_choices = []
        else:
            self.upgrade_choices = Upgrade.get_random_upgrades(3)
            self.module_choices = []
        
        self.play_sound(self.levelup_sound)
        
    def handle_upgrade_selection(self, mouse_pos):
        """Handle clicking on upgrade/module choices"""
        if not self.paused:
            return
        
        # Handle upgrade selection
        if self.upgrade_choices:
            for i, upgrade in enumerate(self.upgrade_choices):
                button_rect = pygame.Rect(SCREEN_WIDTH/2 - 250, 300 + i * 100, 500, 80)
                if button_rect.collidepoint(mouse_pos):
                    Upgrade.apply_upgrade(self.player, upgrade)
                    self.paused = False
                    self.upgrade_choices = []
                    break
        
        # Handle module selection
        elif self.module_choices:
            # Check skip button
            skip_y = min(700, SCREEN_HEIGHT - 100)
            skip_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 150, skip_y, 300, 60)
            if skip_button_rect.collidepoint(mouse_pos):
                self.paused = False
                self.module_choices = []
                return
            
            # Check module buttons
            for i, module in enumerate(self.module_choices):
                button_rect = pygame.Rect(SCREEN_WIDTH/2 - 300, 250 + i * 120, 600, 100)
                if button_rect.collidepoint(mouse_pos):
                    self.player.modules.append(module['id'])
                    if module['id'] == 'shield_generator':
                        self.shield_hp = 50
                    self.apply_module_downsides()
                    self.paused = False
                    self.module_choices = []
                    break
                
    def update_boss_fight(self, dt, current_time):
        """Update boss fight logic"""
        self.boss.update(dt, self.player, current_time)
        
        taunt = self.boss.get_taunt(current_time)
        if taunt:
            self.boss_dialogue = taunt
            self.boss_dialogue_time = current_time
        
        if self.boss.should_spawn_projectile(dt):
            pattern = self.boss.get_current_pattern()
            self.spawn_boss_projectiles(pattern, current_time)
        
        # Update boss projectiles
        for proj in self.boss_projectiles[:]:
            proj.update(dt)
            if proj.is_off_screen():
                self.boss_projectiles.remove(proj)
            elif proj.collides_with_player(self.player):
                damage = 15
                if self.shield_hp > 0:
                    absorbed = min(self.shield_hp, damage)
                    self.shield_hp -= absorbed
                    damage -= absorbed
                if damage > 0:
                    self.player.take_damage(damage * self.player.damage_taken_multiplier)
                if proj in self.boss_projectiles:
                    self.boss_projectiles.remove(proj)
                if not self.player.is_alive():
                    self.game_over = True
                    self.boss_dialogue = BossDialogue.BOSS_WIN
                    self.boss_dialogue_time = current_time
        
        # Check bullet collisions with boss projectiles
        for bullet in self.bullets[:]:
            hit_projectile = False
            for proj in self.boss_projectiles[:]:
                if proj.collides_with_bullet(bullet):
                    destroyed = proj.take_damage(1)
                    if destroyed:
                        self.create_explosion(proj.x, proj.y, ORANGE, 8)
                        if proj in self.boss_projectiles:
                            self.boss_projectiles.remove(proj)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    hit_projectile = True
                    break
            
            if not hit_projectile:
                dx = bullet.x - self.boss.x
                dy = bullet.y - self.boss.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < self.boss.radius + bullet.radius:
                    damage = bullet.damage
                    if 'damage_aura' in self.player.modules:
                        damage *= 1.25
                    
                    hit = self.boss.take_damage(damage)
                    if hit:
                        self.play_sound(self.hit_sound)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    if not self.boss.is_alive():
                        self.game_won = True
                        self.boss_dialogue = BossDialogue.BOSS_DEFEAT
                        self.boss_dialogue_time = current_time
                        self.play_sound(self.kill_sound)
                        self.create_explosion(self.boss.x, self.boss.y, GOLD, 50)
                        break
    
    def spawn_boss_projectiles(self, pattern, current_time):
        """Spawn projectiles based on attack pattern"""
        boss_x, boss_y = self.boss.x, self.boss.y
        speed = 150
        
        if pattern == 'spiral':
            angle = (current_time * 0.003) + (self.boss_pattern_counter * 0.4)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            self.boss_projectiles.append(BossProjectile(boss_x, boss_y, vel_x, vel_y))
            self.boss_pattern_counter += 1
        elif pattern == 'ring':
            if self.boss_pattern_counter % 30 == 0:
                for i in range(8):
                    angle = (i / 8) * math.pi * 2
                    vel_x = math.cos(angle) * speed
                    vel_y = math.sin(angle) * speed
                    self.boss_projectiles.append(BossProjectile(boss_x, boss_y, vel_x, vel_y))
            self.boss_pattern_counter += 1
        elif pattern == 'aimed':
            if self.boss_pattern_counter % 3 == 0:
                dx = self.player.x - boss_x
                dy = self.player.y - boss_y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    vel_x = (dx / dist) * speed * 0.8
                    vel_y = (dy / dist) * speed * 0.8
                    self.boss_projectiles.append(BossProjectile(boss_x, boss_y, vel_x, vel_y))
            self.boss_pattern_counter += 1
        elif pattern == 'chaos':
            if self.boss_pattern_counter % 2 == 0:
                angle = random.uniform(0, math.pi * 2)
                vel_x = math.cos(angle) * speed
                vel_y = math.sin(angle) * speed
                self.boss_projectiles.append(BossProjectile(boss_x, boss_y, vel_x, vel_y))
            self.boss_pattern_counter += 1
    
    def apply_module_effects(self, dt, current_time):
        """Apply passive module effects"""
        if 'regeneration' in self.player.modules:
            if current_time - self.last_regen_time >= 1000:
                self.player.hp = min(self.player.hp + 2, self.player.max_hp)
                self.last_regen_time = current_time
        
        if 'fire_ring' in self.player.modules:
            if current_time - self.last_fire_ring_time >= 1000:
                for enemy in self.enemies[:]:
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < 150:
                        enemy.take_damage(5)
                        if not enemy.is_alive():
                            exp_reward = enemy.exp_reward
                            if 'exp_magnet' in self.player.modules:
                                exp_reward = int(exp_reward * 1.5)
                            self.score += exp_reward
                            self.add_exp(exp_reward)
                            self.create_explosion(enemy.x, enemy.y, enemy.color)
                            if enemy in self.enemies:
                                self.enemies.remove(enemy)
                self.last_fire_ring_time = current_time
        
        if 'shield_generator' in self.player.modules:
            if current_time - self.last_shield_regen_time >= 2000:
                if self.shield_hp < 50:
                    self.shield_hp = min(self.shield_hp + 5, 50)
                self.last_shield_regen_time = current_time
        
        if 'overcharge' in self.player.modules:
            if current_time - self.last_overcharge_damage >= 1000:
                self.player.hp = max(1, self.player.hp - 1)
                self.last_overcharge_damage = current_time
        
        if 'phase_shift' in self.player.modules:
            elapsed = (current_time - self.last_phase_shift) / 1000.0
            if elapsed >= 8:
                self.last_phase_shift = current_time
                self.phase_shift_active = False
            elif elapsed >= 6:
                self.phase_shift_active = True
            else:
                self.phase_shift_active = False
    
    def create_explosion(self, x, y, color, count=15):
        """Create particle explosion effect"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.game_over:
                        self.reset_game()
                    elif self.paused:
                        self.handle_upgrade_selection(event.pos)
                    else:
                        self.mouse_held = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_held = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_over or self.game_won:
                        self.reset_game()
                    else:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_TAB:
                    self.stats_minimized = not self.stats_minimized
                elif event.key == pygame.K_F8:
                    self.level = 28
                    self.exp = 0
                    self.exp_to_next_level = 100
                    self.player.damage = 100
                    self.player.base_damage = 100
                    self.player.max_hp = 500
                    self.player.hp = 500
        return True
        
    def start_boss_fight(self):
        """Initialize boss fight at level 30"""
        self.boss = Boss(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        self.enemies.clear()
        self.boss_dialogue = "Finally! I was getting bored waiting for you."
        self.boss_dialogue_time = pygame.time.get_ticks()
        self.play_sound(self.levelup_sound)
    
    def update(self, dt):
        """Update game state"""
        if self.game_over or self.game_won or self.paused:
            return
            
        self.game_time = pygame.time.get_ticks() - self.start_time
        current_time = pygame.time.get_ticks()
        
        if not self.boss:
            self.update_difficulty()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.player.aim(mouse_x, mouse_y)
        
        if self.mouse_held:
            bullets = self.player.shoot(current_time)
            if bullets:
                for bullet in bullets:
                    self.bullets.append(bullet)
                self.play_sound(self.shoot_sound)
        
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.is_dead():
                self.particles.remove(particle)
        
        self.apply_module_effects(dt, current_time)
        
        if self.boss:
            self.update_boss_fight(dt, current_time)
        
        if not self.boss:
            if current_time - self.last_spawn_time >= self.spawn_interval:
                self.spawn_enemy()
                self.last_spawn_time = current_time
            
        for bullet in self.bullets[:]:
            bullet.update(dt, self.enemies)
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                
        for enemy in self.enemies[:]:
            enemy_dt = dt
            if 'time_slow' in self.player.modules:
                dx = enemy.x - self.player.x
                dy = enemy.y - self.player.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < 200:
                    enemy_dt *= 0.6
            
            enemy.update(enemy_dt, self.player)
            
            if enemy.collides_with_player(self.player):
                if self.phase_shift_active:
                    self.enemies.remove(enemy)
                    continue
                
                damage = 10 * self.player.damage_taken_multiplier
                if self.shield_hp > 0:
                    absorbed = min(self.shield_hp, damage)
                    self.shield_hp -= absorbed
                    damage -= absorbed
                if damage > 0:
                    self.player.take_damage(damage)
                self.enemies.remove(enemy)
                if not self.player.is_alive():
                    self.game_over = True
                continue
                
            for bullet in self.bullets[:]:
                if enemy.collides_with_bullet(bullet):
                    damage = bullet.damage
                    
                    if 'damage_aura' in self.player.modules:
                        damage *= 1.4
                    if 'sniper_mode' in self.player.modules:
                        damage *= 2.0
                    if 'berserker' in self.player.modules and self.player.hp < self.player.max_hp * 0.5:
                        damage *= 1.75
                    if 'overcharge' in self.player.modules:
                        damage *= 1.15
                    
                    enemy.take_damage(damage)
                    self.play_sound(self.hit_sound)
                    
                    if bullet.explosive:
                        self.create_explosion(bullet.x, bullet.y, ORANGE, 20)
                        for other_enemy in self.enemies:
                            if other_enemy != enemy:
                                dx = other_enemy.x - bullet.x
                                dy = other_enemy.y - bullet.y
                                dist = math.sqrt(dx**2 + dy**2)
                                if dist < 80:
                                    other_enemy.take_damage(damage * 0.5)
                    
                    if bullet.piercing:
                        bullet.hits += 1
                        if bullet.hits >= 3:
                            if bullet in self.bullets:
                                self.bullets.remove(bullet)
                    else:
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                    
                    if not enemy.is_alive():
                        exp_reward = enemy.exp_reward
                        if 'exp_magnet' in self.player.modules:
                            exp_reward = int(exp_reward * 1.5)
                        self.score += exp_reward
                        self.add_exp(exp_reward)
                        self.play_sound(self.kill_sound)
                        self.create_explosion(enemy.x, enemy.y, enemy.color)
                        
                        if 'vampiric' in self.player.modules:
                            self.player.hp = min(self.player.hp + 10, self.player.max_hp)
                        
                        if 'chain_lightning' in self.player.modules:
                            for other_enemy in self.enemies:
                                if other_enemy != enemy:
                                    dx = other_enemy.x - enemy.x
                                    dy = other_enemy.y - enemy.y
                                    dist = math.sqrt(dx**2 + dy**2)
                                    if dist < 100:
                                        other_enemy.take_damage(damage * 0.5)
                                        self.create_explosion(other_enemy.x, other_enemy.y, CYAN, 5)
                        
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    
                    if not bullet.piercing:
                        break
                    
    def draw_ui(self):
        """Draw UI elements"""
        # HP bar
        bar_x, bar_y = 20, 20
        bar_width, bar_height = 300, 30
        hp_ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width * hp_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        hp_text = self.small_font.render(f"HP: {int(self.player.hp)}/{int(self.player.max_hp)}", True, WHITE)
        self.screen.blit(hp_text, (bar_x + 10, bar_y + 5))
        
        # EXP bar
        bar_y = 60
        exp_ratio = self.exp / self.exp_to_next_level
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, MAGENTA, (bar_x, bar_y, bar_width * exp_ratio, bar_height))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        exp_text = self.small_font.render(f"EXP: {self.exp}/{self.exp_to_next_level}", True, WHITE)
        self.screen.blit(exp_text, (bar_x + 10, bar_y + 5))
        
        # Score and level
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 250, 20))
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 250, 60))
        
        # Time
        time_seconds = self.game_time / 1000
        time_text = self.small_font.render(f"Time: {int(time_seconds)}s", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - 250, 100))
        
        # Shield bar
        if 'shield_generator' in self.player.modules and self.shield_hp > 0:
            bar_x, bar_y = 20, 100
            bar_width, bar_height = 300, 20
            shield_ratio = self.shield_hp / 50
            pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, CYAN, (bar_x, bar_y, bar_width * shield_ratio, bar_height))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            shield_text = self.small_font.render(f"Shield: {int(self.shield_hp)}/50", True, WHITE)
            self.screen.blit(shield_text, (bar_x + 10, bar_y + 2))
        
    def draw_upgrade_menu(self):
        """Draw upgrade selection menu"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("LEVEL UP! Choose an Upgrade:", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH/2, 200))
        self.screen.blit(title, title_rect)
        
        for i, upgrade in enumerate(self.upgrade_choices):
            button_rect = pygame.Rect(SCREEN_WIDTH/2 - 250, 300 + i * 100, 500, 80)
            rarity_color = Upgrade.get_rarity_color(upgrade['rarity'])
            
            pygame.draw.rect(self.screen, GRAY, button_rect)
            pygame.draw.rect(self.screen, rarity_color, button_rect, 4)
            
            rarity_text = self.small_font.render(upgrade['rarity'].upper(), True, rarity_color)
            badge_rect = rarity_text.get_rect(topleft=(button_rect.left + 10, button_rect.top + 10))
            self.screen.blit(rarity_text, badge_rect)
            
            upgrade_text = self.font.render(upgrade['name'], True, WHITE)
            text_rect = upgrade_text.get_rect(center=button_rect.center)
            self.screen.blit(upgrade_text, text_rect)
    
    def draw_module_menu(self):
        """Draw module selection menu"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.font.render("MODULE UNLOCKED! Choose Wisely:", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH/2, 100))
        self.screen.blit(title, title_rect)
        
        for i, module in enumerate(self.module_choices):
            button_rect = pygame.Rect(SCREEN_WIDTH/2 - 350, 200 + i * 150, 700, 130)
            
            pygame.draw.rect(self.screen, DARK_GRAY, button_rect)
            pygame.draw.rect(self.screen, module['color'], button_rect, 5)
            
            name_text = self.font.render(module['name'], True, module['color'])
            name_rect = name_text.get_rect(center=(button_rect.centerx, button_rect.top + 25))
            self.screen.blit(name_text, name_rect)
            
            upside_text = self.small_font.render(f"↑ {module['upside']}", True, GREEN)
            upside_rect = upside_text.get_rect(center=(button_rect.centerx, button_rect.top + 60))
            self.screen.blit(upside_text, upside_rect)
            
            downside_text = self.small_font.render(f"↓ {module['downside']}", True, RED)
            downside_rect = downside_text.get_rect(center=(button_rect.centerx, button_rect.top + 90))
            self.screen.blit(downside_text, downside_rect)
        
        skip_y = min(700, SCREEN_HEIGHT - 100)
        skip_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 150, skip_y, 300, 60)
        pygame.draw.rect(self.screen, DARK_GRAY, skip_button_rect)
        pygame.draw.rect(self.screen, GRAY, skip_button_rect, 3)
        skip_text = self.small_font.render("Skip Module Selection", True, WHITE)
        skip_rect = skip_text.get_rect(center=skip_button_rect.center)
        self.screen.blit(skip_text, skip_rect)
        
        # Draw current stats panel
        stats_panel_rect = pygame.Rect(50, SCREEN_HEIGHT - 200, 250, 180)
        pygame.draw.rect(self.screen, DARK_GRAY, stats_panel_rect)
        pygame.draw.rect(self.screen, WHITE, stats_panel_rect, 2)
        
        stats_title = self.small_font.render("Current Stats:", True, YELLOW)
        self.screen.blit(stats_title, (stats_panel_rect.left + 10, stats_panel_rect.top + 10))
        
        stats = self.get_player_stats_text()
        for i, stat in enumerate(stats):
            stat_text = self.tiny_font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (stats_panel_rect.left + 10, stats_panel_rect.top + 40 + i * 22))
            
    def draw_game_over(self):
        """Draw game over or victory screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.game_won:
            game_over_text = self.font.render("VICTORY!", True, GOLD)
        else:
            game_over_text = self.font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, 250))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, 320))
        self.screen.blit(score_text, score_rect)
        
        level_text = self.font.render(f"Level Reached: {self.level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH/2, 370))
        self.screen.blit(level_text, level_rect)
        
        time_seconds = self.game_time / 1000
        time_text = self.font.render(f"Survival Time: {int(time_seconds)}s", True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH/2, 420))
        self.screen.blit(time_text, time_rect)
        
        restart_text = self.small_font.render("Click anywhere or press ESC to restart", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, 500))
        self.screen.blit(restart_text, restart_rect)
        
    def draw_stats_panel(self):
        """Draw detailed stats panel (always visible, can minimize with TAB)"""
        # Panel dimensions
        if self.stats_minimized:
            panel_width = 300
            panel_height = 60
        else:
            panel_width = 300
            base_height = 320
            module_count = len(self.player.modules)
            module_height = module_count * 18 + 40  # Show ALL modules
            panel_height = base_height + module_height
        
        panel_x = SCREEN_WIDTH - panel_width - 20
        panel_y = 150
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        overlay = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        overlay.fill((*BLACK, 220))
        self.screen.blit(overlay, (panel_x, panel_y))
        
        # Title
        title_text = self.font.render("Stats (TAB)", True, CYAN)
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        if self.stats_minimized:
            return
        
        # Stats
        y_offset = panel_y + 50
        stats = [
            ("COMBAT", YELLOW, True),
            (f"Damage: {int(self.player.damage)}", WHITE, False),
            (f"Fire Rate: {self.player.fire_rate:.1f}/sec", WHITE, False),
            (f"Bullet Speed: {int(self.player.bullet_speed)}", WHITE, False),
            ("", WHITE, False),
            ("SURVIVAL", YELLOW, True),
            (f"HP: {int(self.player.hp)}/{int(self.player.max_hp)}", WHITE, False),
            (f"Shield: {int(self.shield_hp)}/50" if 'shield_generator' in self.player.modules else "Shield: None", WHITE, False),
            (f"Damage Taken: {int(self.player.damage_taken_multiplier * 100)}%", WHITE, False),
            ("", WHITE, False),
            ("PROGRESSION", YELLOW, True),
            (f"Level: {self.level}", WHITE, False),
            (f"EXP: {self.exp}/{self.exp_to_next_level}", WHITE, False),
            (f"EXP Multiplier: {self.player.exp_multiplier:.1f}x", WHITE, False),
            ("", WHITE, False),
            ("MODULES", YELLOW, True),
            (f"Active: {len(self.player.modules)}/20", WHITE, False),
        ]
        
        for text, color, is_header in stats:
            if text:
                font = self.small_font if is_header else self.tiny_font
                stat_text = font.render(text, True, color)
                self.screen.blit(stat_text, (panel_x + 15, y_offset))
            y_offset += 25 if is_header else 20
        
        # List ALL active modules
        if self.player.modules:
            y_offset += 5
            for module_id in self.player.modules:
                module = next((m for m in Module.MODULES if m['id'] == module_id), None)
                if module:
                    module_text = self.tiny_font.render(f"• {module['name']}", True, module['color'])
                    self.screen.blit(module_text, (panel_x + 20, y_offset))
                    y_offset += 18
    
    def draw_module_indicators(self):
        """Draw active module indicators and effects"""
        if 'fire_ring' in self.player.modules:
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            alpha = int(50 + 30 * math.sin(pulse * math.pi * 2))
            ring_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, (*RED, alpha), (int(self.player.x), int(self.player.y)), 150, 3)
            self.screen.blit(ring_surface, (0, 0))
        
        if 'time_slow' in self.player.modules:
            pulse = (pygame.time.get_ticks() % 1500) / 1500.0
            alpha = int(30 + 20 * math.sin(pulse * math.pi * 2))
            slow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(slow_surface, (*BLUE, alpha), (int(self.player.x), int(self.player.y)), 200, 2)
            self.screen.blit(slow_surface, (0, 0))
        
        if 'damage_aura' in self.player.modules:
            pulse = (pygame.time.get_ticks() % 800) / 800.0
            alpha = int(40 + 25 * math.sin(pulse * math.pi * 2))
            aura_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(aura_surface, (*RED, alpha), (int(self.player.x), int(self.player.y)), 100, 4)
            self.screen.blit(aura_surface, (0, 0))
        
        if 'phase_shift' in self.player.modules and self.phase_shift_active:
            flash = (pygame.time.get_ticks() % 200) / 200.0
            alpha = int(100 + 100 * math.sin(flash * math.pi * 2))
            phase_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(phase_surface, (*PURPLE, alpha), (int(self.player.x), int(self.player.y)), self.player.radius + 5, 3)
            self.screen.blit(phase_surface, (0, 0))
        
        # Module icons at bottom
        if self.player.modules:
            icon_size = 40
            spacing = 50
            start_x = SCREEN_WIDTH / 2 - (len(self.player.modules) * spacing) / 2
            y = SCREEN_HEIGHT - 60
            
            for i, module_id in enumerate(self.player.modules):
                module = next((m for m in Module.MODULES if m['id'] == module_id), None)
                if module:
                    x = start_x + i * spacing
                    pygame.draw.circle(self.screen, DARK_GRAY, (int(x), int(y)), icon_size // 2)
                    pygame.draw.circle(self.screen, module['color'], (int(x), int(y)), icon_size // 2 - 2)
                    pygame.draw.circle(self.screen, WHITE, (int(x), int(y)), icon_size // 2, 2)
                    
                    letter = module['name'][0]
                    letter_text = self.small_font.render(letter, True, WHITE)
                    letter_rect = letter_text.get_rect(center=(int(x), int(y)))
                    self.screen.blit(letter_text, letter_rect)
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        
        self.player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        
        if self.boss:
            self.boss.draw(self.screen, self.small_font)
            for proj in self.boss_projectiles:
                proj.draw(self.screen)
            
        self.draw_ui()
        self.draw_module_indicators()
        
        # Always draw stats panel
        if self.show_stats:
            self.draw_stats_panel()
        
        # Boss dialogue
        if self.boss_dialogue:
            current_time = pygame.time.get_ticks()
            if current_time - self.boss_dialogue_time < 4000:
                dialogue_box_height = 80
                dialogue_box_y = SCREEN_HEIGHT - dialogue_box_height - 100
                dialogue_box = pygame.Rect(50, dialogue_box_y, SCREEN_WIDTH - 100, dialogue_box_height)
                pygame.draw.rect(self.screen, DARK_GRAY, dialogue_box)
                pygame.draw.rect(self.screen, GOLD, dialogue_box, 3)
                
                dialogue_text = self.small_font.render(f'THE SHAPE: "{self.boss_dialogue}"', True, WHITE)
                dialogue_rect = dialogue_text.get_rect(center=(SCREEN_WIDTH / 2, dialogue_box_y + dialogue_box_height / 2))
                self.screen.blit(dialogue_text, dialogue_rect)
            else:
                self.boss_dialogue = None
        
        if self.paused:
            if self.module_choices:
                self.draw_module_menu()
            else:
                self.draw_upgrade_menu()
        elif self.game_over or self.game_won:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
