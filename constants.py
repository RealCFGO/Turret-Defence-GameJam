import pygame

# Initialize Pygame
pygame.init()
info = pygame.display.Info()

SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
FPS = 60

ASPECT_RATIO = 16 / 9
SCREEN_WIDTH = int(info.current_w * 0.8)  # 80% of the screen width
SCREEN_HEIGHT = int(SCREEN_WIDTH / ASPECT_RATIO)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
CYAN = (50, 255, 255)
MAGENTA = (255, 50, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)
GOLD = (255, 215, 0)

# Rarity colors
COMMON_COLOR = (200, 200, 200)
RARE_COLOR = (100, 150, 255)
EPIC_COLOR = (160, 32, 240)
LEGENDARY_COLOR = (255, 215, 0)

# Game balance constants
BASE_DAMAGE = 8
BASE_FIRE_RATE = 6  
BASE_BULLET_SPEED = 350
BASE_MAX_HP = 80
BASE_EXP_MULTIPLIER = 1.0

# Enemy types
ENEMY_TYPES = {
    'circle': {'color': RED, 'speed': 60, 'hp': 25, 'exp': 10, 'radius': 20},
    'square': {'color': GREEN, 'speed': 45, 'hp': 40, 'exp': 15, 'size': 35},
    'triangle': {'color': BLUE, 'speed': 75, 'hp': 15, 'exp': 8, 'size': 30}
}
