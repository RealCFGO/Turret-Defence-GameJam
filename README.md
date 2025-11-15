# Geometric Defense MVP

A minimal survival shooter prototype built with Pygame.

## Description

Control a stationary turret in the center of the screen, aiming with the mouse and shooting by clicking. Geometric enemies (circles, squares, triangles) spawn randomly at the screen edges and move toward the player. Each shape has distinct speed, HP, and EXP reward values.

### Features

- **Shooting Mechanics**: Bullets travel straight, deal fixed damage, and disappear on collision
- **Enemy Variety**: Three geometric shapes with different stats
- **Progression System**: Gain EXP from kills, level up, and choose from random stat upgrades
- **Difficulty Scaling**: Enemy spawn rate, HP, and speed increase over time
- **Minimalist Art**: Simple colored shapes and flat backgrounds
- **Boss fight**: At level 30, you will fight a boss.

### Upgrades

When leveling up, choose from random upgrades:
- Increased damage
- Faster fire rate
- Higher bullet speed
- More max HP
- Improved EXP gain

## Installation

```bash
pip install -r requirements.txt
```

## How to Play

```bash
python main.py
```

### Controls

- **Mouse**: Aim the turret
- **Left Click**: Shoot
- **ESC**: Restart after game over
- **Tab**: To toggle stats page

## Goal

Beat the boss at level 30.
