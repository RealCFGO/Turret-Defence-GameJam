import pygame
import math
import random
from constants import *


class Particle:
    """Simple particle for explosion effects"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-150, 150)
        self.vel_y = random.uniform(-150, 150)
        self.lifetime = random.uniform(0.3, 0.6)
        self.age = 0
        self.size = random.randint(3, 7)
        self.color = color
        
    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.age += dt
        
    def is_dead(self):
        return self.age >= self.lifetime
        
    def draw(self, screen):
        alpha_ratio = 1 - (self.age / self.lifetime)
        current_size = int(self.size * alpha_ratio)
        if current_size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), current_size)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.color = CYAN
        self.max_hp = BASE_MAX_HP
        self.hp = self.max_hp
        self.base_damage = BASE_DAMAGE
        self.damage = BASE_DAMAGE
        self.base_fire_rate = BASE_FIRE_RATE
        self.fire_rate = BASE_FIRE_RATE
        self.base_bullet_speed = BASE_BULLET_SPEED
        self.bullet_speed = BASE_BULLET_SPEED
        self.exp_multiplier = BASE_EXP_MULTIPLIER
        self.last_shot_time = 0
        self.angle = 0
        self.modules = []  # Active modules
        self.damage_taken_multiplier = 1.0  # For damage aura downside
        
    def aim(self, mouse_x, mouse_y):
        """Update turret angle to point at mouse"""
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        self.angle = math.atan2(dy, dx)
        
    def can_shoot(self, current_time):
        """Check if enough time has passed to shoot again"""
        shoot_interval = 1000 / self.fire_rate  # milliseconds between shots
        return current_time - self.last_shot_time >= shoot_interval
        
    def shoot(self, current_time):
        """Create a bullet in the direction the turret is facing"""
        if self.can_shoot(current_time):
            self.last_shot_time = current_time
            bullet_x = self.x + math.cos(self.angle) * self.radius
            bullet_y = self.y + math.sin(self.angle) * self.radius
            vel_x = math.cos(self.angle) * self.bullet_speed
            vel_y = math.sin(self.angle) * self.bullet_speed
            
            # Check for module effects
            explosive = 'explosive_rounds' in self.modules
            piercing = 'piercing_rounds' in self.modules
            homing = 'homing_missiles' in self.modules
            
            # Calculate damage with module effects
            bullet_damage = self.damage
            if piercing:
                bullet_damage *= 0.75  # Piercing downside
            if 'multi_shot' in self.modules:
                bullet_damage *= 0.7  # Multi-shot downside
            
            bullets = [Bullet(bullet_x, bullet_y, vel_x, vel_y, bullet_damage, explosive, piercing, homing)]
            
            # Multi-shot module
            if 'multi_shot' in self.modules:
                angle_offset = math.pi / 12  # 15 degrees
                for offset in [-angle_offset, angle_offset]:
                    angle = self.angle + offset
                    vel_x2 = math.cos(angle) * self.bullet_speed
                    vel_y2 = math.sin(angle) * self.bullet_speed
                    bullets.append(Bullet(bullet_x, bullet_y, vel_x2, vel_y2, bullet_damage, explosive, piercing, homing))
            
            return bullets
        return None
        
    def take_damage(self, damage):
        """Reduce HP"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
            
    def is_alive(self):
        """Check if player still has HP"""
        return self.hp > 0
        
    def draw(self, screen):
        """Draw the turret and barrel with improved visuals"""
        # Draw base shadow
        shadow_offset = 3
        pygame.draw.circle(screen, (20, 20, 20), (int(self.x + shadow_offset), int(self.y + shadow_offset)), self.radius)
        
        # Draw turret base (darker ring)
        pygame.draw.circle(screen, (30, 80, 100), (int(self.x), int(self.y)), self.radius + 3)
        
        # Draw turret body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw inner detail circle
        pygame.draw.circle(screen, (100, 200, 220), (int(self.x), int(self.y)), self.radius - 8, 2)
        
        # Draw barrel base (thicker part)
        barrel_base_length = 15
        base_end_x = self.x + math.cos(self.angle) * barrel_base_length
        base_end_y = self.y + math.sin(self.angle) * barrel_base_length
        pygame.draw.line(screen, (40, 40, 40), (self.x, self.y), (base_end_x, base_end_y), 10)
        
        # Draw barrel pointing at mouse
        barrel_length = 35
        end_x = self.x + math.cos(self.angle) * barrel_length
        end_y = self.y + math.sin(self.angle) * barrel_length
        pygame.draw.line(screen, DARK_GRAY, (self.x, self.y), (end_x, end_y), 8)
        pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 6)
        
        # Draw barrel tip
        pygame.draw.circle(screen, YELLOW, (int(end_x), int(end_y)), 4)
        
        # Draw turret outline
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 3)


class Bullet:
    def __init__(self, x, y, vel_x, vel_y, damage, explosive=False, piercing=False, homing=False):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.damage = damage
        self.radius = 5
        self.color = YELLOW
        self.explosive = explosive
        self.piercing = piercing
        self.homing = homing
        self.hits = 0  # For piercing bullets
        
    def update(self, dt, enemies=None):
        """Move the bullet"""
        # Homing behavior
        if self.homing and enemies:
            closest = None
            closest_dist = 300  # Homing range
            for enemy in enemies:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < closest_dist:
                    closest = enemy
                    closest_dist = dist
            
            if closest:
                # Steer toward closest enemy
                target_dx = closest.x - self.x
                target_dy = closest.y - self.y
                target_dist = math.sqrt(target_dx**2 + target_dy**2)
                if target_dist > 0:
                    speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
                    turn_rate = 0.1  # How quickly bullet turns
                    self.vel_x += (target_dx / target_dist * speed - self.vel_x) * turn_rate
                    self.vel_y += (target_dy / target_dist * speed - self.vel_y) * turn_rate
        
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
    def is_off_screen(self):
        """Check if bullet has left the screen"""
        return (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)
                
    def draw(self, screen):
        """Draw the bullet"""
        if self.explosive:
            # Explosive bullets are orange/red
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius + 2)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        elif self.piercing:
            # Piercing bullets are cyan
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius + 1)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 1)
        elif self.homing:
            # Homing bullets are magenta
            pygame.draw.circle(screen, MAGENTA, (int(self.x), int(self.y)), self.radius + 1)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 2)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


class Enemy:
    def __init__(self, x, y, enemy_type, difficulty_scale=1.0):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.stats = ENEMY_TYPES[enemy_type].copy()
        
        # Scale stats with difficulty
        self.max_hp = self.stats['hp'] * difficulty_scale
        self.hp = self.max_hp
        self.speed = self.stats['speed'] * (1 + (difficulty_scale - 1) * 0.3)  # Speed scales slower
        self.exp_reward = int(self.stats['exp'] * difficulty_scale)
        self.color = self.stats['color']
        
        # Calculate direction toward center
        center_x, center_y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        dx = center_x - self.x
        dy = center_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        self.vel_x = (dx / distance) * self.speed
        self.vel_y = (dy / distance) * self.speed
        
    def update(self, dt, player):
        """Move toward player"""
        # Recalculate direction to follow player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.vel_x = (dx / distance) * self.speed
            self.vel_y = (dy / distance) * self.speed
            
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
    def take_damage(self, damage):
        """Reduce HP"""
        self.hp -= damage
        
    def is_alive(self):
        """Check if enemy still has HP"""
        return self.hp > 0
        
    def collides_with_player(self, player):
        """Check collision with player"""
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.sqrt(dx**2 + dy**2)
        if self.type == 'circle':
            return distance < (self.stats['radius'] + player.radius)
        else:
            # Use approximate collision for square/triangle
            size = self.stats.get('size', self.stats.get('radius', 20))
            return distance < (size * 0.7 + player.radius)
            
    def collides_with_bullet(self, bullet):
        """Check collision with bullet"""
        dx = self.x - bullet.x
        dy = self.y - bullet.y
        distance = math.sqrt(dx**2 + dy**2)
        if self.type == 'circle':
            return distance < (self.stats['radius'] + bullet.radius)
        else:
            size = self.stats.get('size', self.stats.get('radius', 20))
            return distance < (size * 0.7 + bullet.radius)
            
    def draw(self, screen):
        """Draw the enemy based on type"""
        if self.type == 'circle':
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.stats['radius'])
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.stats['radius'], 2)
        elif self.type == 'square':
            size = self.stats['size']
            rect = pygame.Rect(int(self.x - size/2), int(self.y - size/2), size, size)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
        elif self.type == 'triangle':
            size = self.stats['size']
            points = [
                (self.x, self.y - size * 0.6),
                (self.x - size * 0.5, self.y + size * 0.4),
                (self.x + size * 0.5, self.y + size * 0.4)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            
        # Draw HP bar
        if self.hp < self.max_hp:
            bar_width = 40
            bar_height = 5
            bar_x = self.x - bar_width / 2
            bar_y = self.y - 35
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * hp_ratio, bar_height))


class Boss:
    """Level 30 boss with multiple attack patterns"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 5000
        self.hp = self.max_hp
        self.radius = 60
        self.color = GOLD
        self.phase = 1  # Changes attack patterns
        self.pattern_timer = 0
        self.current_pattern = 'spiral'
        self.vulnerable = False  # Can only damage when vulnerable
        self.vulnerable_timer = 0
        self.pattern_cooldown = 0
        self.rotation = 0
        self.taunt_timer = 0
        self.last_taunt = 0
        
    def update(self, dt, player, current_time):
        """Update boss AI and patterns"""
        self.pattern_timer += dt
        self.vulnerable_timer += dt
        self.rotation += dt * 0.5
        self.taunt_timer += dt
        
        # Determine phase based on HP
        hp_ratio = self.hp / self.max_hp
        if hp_ratio > 0.66:
            self.phase = 1
        elif hp_ratio > 0.33:
            self.phase = 2
        else:
            self.phase = 3
        
        # Vulnerability windows
        if self.vulnerable_timer > 8:  # Vulnerable every 8 seconds
            self.vulnerable = True
            if self.vulnerable_timer > 11:  # 3 second window
                self.vulnerable = False
                self.vulnerable_timer = 0
        else:
            self.vulnerable = False
        
        # Dynamic movement - KITING AWAY from player
        center_x, center_y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        time_factor = current_time * 0.001
        
        # Calculate direction AWAY from player
        dx = self.x - player.x
        dy = self.y - player.y
        dist_to_player = math.sqrt(dx**2 + dy**2)
        
        if self.phase == 1:
            # Phase 1: Keep distance while circling
            if dist_to_player < 250:  # Too close, move away
                if dist_to_player > 0:
                    self.x += (dx / dist_to_player) * 80 * dt
                    self.y += (dy / dist_to_player) * 80 * dt
            # Also orbit around center
            orbit_radius = 200
            target_x = center_x + math.cos(time_factor * 0.5) * orbit_radius
            target_y = center_y + math.sin(time_factor * 0.5) * orbit_radius
            self.x += (target_x - self.x) * 0.02
            self.y += (target_y - self.y) * 0.02
            
        elif self.phase == 2:
            # Phase 2: More aggressive kiting with figure-8
            if dist_to_player < 280:
                if dist_to_player > 0:
                    self.x += (dx / dist_to_player) * 100 * dt
                    self.y += (dy / dist_to_player) * 100 * dt
            target_x = center_x + math.sin(time_factor * 0.7) * 250
            target_y = center_y + math.sin(time_factor * 1.4) * 150
            self.x += (target_x - self.x) * 0.03
            self.y += (target_y - self.y) * 0.03
            
        else:
            # Phase 3: Erratic kiting
            if dist_to_player < 300:
                if dist_to_player > 0:
                    self.x += (dx / dist_to_player) * 120 * dt
                    self.y += (dy / dist_to_player) * 120 * dt
            base_angle = time_factor * 0.8
            wave_offset = math.sin(time_factor * 3) * 100
            orbit_radius = 180 + wave_offset
            target_x = center_x + math.cos(base_angle) * orbit_radius
            target_y = center_y + math.sin(base_angle) * orbit_radius
            self.x += (target_x - self.x) * 0.04
            self.y += (target_y - self.y) * 0.04
            
            # Random teleports during vulnerability
            if self.vulnerable and int(time_factor * 10) % 20 == 0:
                angle = random.uniform(0, math.pi * 2)
                self.x = center_x + math.cos(angle) * 200
                self.y = center_y + math.sin(angle) * 200
        
        # Keep boss on screen
        margin = self.radius + 10
        self.x = max(margin, min(SCREEN_WIDTH - margin, self.x))
        self.y = max(margin, min(SCREEN_HEIGHT - margin, self.y))
        
    def get_current_pattern(self):
        """Get current bullet pattern based on phase"""
        if self.phase == 1:
            return random.choice(['spiral', 'ring'])
        elif self.phase == 2:
            return random.choice(['spiral', 'ring', 'aimed'])
        else:
            return random.choice(['spiral', 'ring', 'aimed', 'chaos'])
    
    def should_spawn_projectile(self, dt):
        """Check if boss should spawn a projectile"""
        self.pattern_cooldown -= dt
        if self.pattern_cooldown <= 0:
            self.pattern_cooldown = 0.1 / self.phase  # Faster in later phases
            return True
        return False
    
    def get_taunt(self, current_time):
        """Get random taunt if enough time has passed"""
        if current_time - self.last_taunt > 5000:  # Every 5 seconds
            self.last_taunt = current_time
            from dialogue import BossDialogue
            return random.choice(BossDialogue.BOSS_TAUNTS)
        return None
    
    def take_damage(self, damage):
        """Take damage only when vulnerable"""
        if self.vulnerable:
            self.hp -= damage
            return True
        return False
    
    def is_alive(self):
        return self.hp > 0
    
    def draw(self, screen, font):
        """Draw the boss"""
        # Draw shadow
        pygame.draw.circle(screen, (20, 20, 20), (int(self.x + 5), int(self.y + 5)), self.radius)
        
        # Draw main body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw rotating segments
        for i in range(8):
            angle = self.rotation + (i * math.pi / 4)
            seg_x = self.x + math.cos(angle) * (self.radius - 10)
            seg_y = self.y + math.sin(angle) * (self.radius - 10)
            pygame.draw.circle(screen, ORANGE if self.vulnerable else DARK_GRAY, 
                             (int(seg_x), int(seg_y)), 8)
        
        # Draw core
        core_color = RED if self.vulnerable else GRAY
        pygame.draw.circle(screen, core_color, (int(self.x), int(self.y)), 20)
        
        # Draw outline
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 4)
        
        # Draw HP bar
        bar_width = 400
        bar_height = 30
        bar_x = SCREEN_WIDTH / 2 - bar_width / 2
        bar_y = 50
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GOLD, (bar_x, bar_y, bar_width * hp_ratio, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)
        
        hp_text = font.render(f"THE SHAPE: {int(self.hp)}/{int(self.max_hp)}", True, WHITE)
        hp_rect = hp_text.get_rect(center=(SCREEN_WIDTH / 2, bar_y + bar_height / 2))
        screen.blit(hp_text, hp_rect)
        
        # Vulnerable indicator
        if self.vulnerable:
            vuln_text = font.render("VULNERABLE!", True, RED)
            vuln_rect = vuln_text.get_rect(center=(self.x, self.y - self.radius - 20))
            screen.blit(vuln_text, vuln_rect)


class BossProjectile:
    """Boss attack projectile - can be shot down"""
    def __init__(self, x, y, vel_x, vel_y):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = 8
        self.color = RED
        self.hp = 2  # Takes 2 hits to destroy
        
    def update(self, dt):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        
    def is_off_screen(self):
        return (self.x < -50 or self.x > SCREEN_WIDTH + 50 or
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)
    
    def collides_with_player(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < (self.radius + player.radius)
    
    def collides_with_bullet(self, bullet):
        """Check collision with player bullet"""
        dx = self.x - bullet.x
        dy = self.y - bullet.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < (self.radius + bullet.radius)
    
    def take_damage(self, damage):
        """Projectile can be shot down"""
        self.hp -= 1
        return self.hp <= 0
    
    def draw(self, screen):
        # Draw with HP indicator
        if self.hp > 1:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius - 3)
        else:
            # Damaged state - smaller and darker
            pygame.draw.circle(screen, DARK_GRAY, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius - 2)
