import random
from constants import *


class Module:
    """Represents a powerful module that changes gameplay"""
    MODULES = [
        # Original 10
        {'id': 'explosive_rounds', 'name': 'Explosive Rounds', 'description': 'Bullets explode on impact',
         'upside': '+50% splash damage in radius', 'downside': '-20% fire rate', 'color': ORANGE},
        {'id': 'fire_ring', 'name': 'Fire Ring', 'description': 'Burn nearby enemies',
         'upside': '5 damage/sec in 150 radius', 'downside': '-15% bullet speed', 'color': RED},
        {'id': 'piercing_rounds', 'name': 'Piercing Rounds', 'description': 'Bullets pierce enemies',
         'upside': 'Hit up to 3 targets', 'downside': '-25% damage per bullet', 'color': CYAN},
        {'id': 'regeneration', 'name': 'Regeneration', 'description': 'Slowly heal over time',
         'upside': 'Restore 2 HP/second', 'downside': '-10% max HP', 'color': GREEN},
        {'id': 'multi_shot', 'name': 'Multi-Shot', 'description': 'Fire 3 bullets spread',
         'upside': '3 bullets per shot', 'downside': '-30% damage per bullet', 'color': YELLOW},
        {'id': 'homing_missiles', 'name': 'Homing Missiles', 'description': 'Bullets track enemies',
         'upside': 'Auto-aim within 300 units', 'downside': '-20% bullet speed', 'color': MAGENTA},
        {'id': 'exp_magnet', 'name': 'EXP Magnet', 'description': 'Amplify experience gain',
         'upside': '+50% EXP from kills', 'downside': 'Enemies spawn 15% faster', 'color': PURPLE},
        {'id': 'damage_aura', 'name': 'Damage Aura', 'description': 'Boost all damage',
         'upside': '+40% damage output', 'downside': 'Take +30% damage', 'color': RED},
        {'id': 'time_slow', 'name': 'Time Slow Field', 'description': 'Slow nearby enemies',
         'upside': '-40% enemy speed in 200 radius', 'downside': '-30% fire rate', 'color': BLUE},
        {'id': 'shield_generator', 'name': 'Shield Generator', 'description': '50 HP rechargeable shield',
         'upside': 'Absorbs damage, regens 5/2sec', 'downside': '-15% fire rate', 'color': CYAN},
        # New 10 modules
        {'id': 'rapid_fire', 'name': 'Rapid Fire', 'description': 'Fire rate overcharge',
         'upside': '+50% fire rate', 'downside': '-20% damage per bullet', 'color': YELLOW},
        {'id': 'sniper_mode', 'name': 'Sniper Mode', 'description': 'High damage precision',
         'upside': '+100% damage per bullet', 'downside': '-50% fire rate', 'color': BLUE},
        {'id': 'chain_lightning', 'name': 'Chain Lightning', 'description': 'Kills chain to nearby',
         'upside': '50% damage to 2 nearby enemies', 'downside': '-15% base damage', 'color': CYAN},
        {'id': 'berserker', 'name': 'Berserker Mode', 'description': 'Lower HP = more damage',
         'upside': '+75% damage under 50% HP', 'downside': 'Cannot heal above 50% HP', 'color': RED},
        {'id': 'vampiric', 'name': 'Vampiric Rounds', 'description': 'Lifesteal on kills',
         'upside': 'Heal 10 HP per kill', 'downside': '-20% max HP', 'color': MAGENTA},
        {'id': 'overcharge', 'name': 'Overcharge', 'description': 'All stats boosted',
         'upside': '+15% to all stats', 'downside': 'Lose 1 HP/second', 'color': ORANGE},
        {'id': 'ricochet', 'name': 'Ricochet Rounds', 'description': 'Bullets bounce off walls',
         'upside': 'Bullets bounce 2 times', 'downside': '-40% bullet speed', 'color': CYAN},
        {'id': 'armor_plating', 'name': 'Armor Plating', 'description': 'Reduce incoming damage',
         'upside': 'Take 30% less damage', 'downside': '-30% bullet speed', 'color': GRAY},
        {'id': 'laser_sight', 'name': 'Laser Sight', 'description': 'Faster, more precise',
         'upside': '+60% bullet speed', 'downside': '-15% fire rate', 'color': RED},
        {'id': 'phase_shift', 'name': 'Phase Shift', 'description': 'Periodic invulnerability',
         'upside': '2 sec invuln every 8 sec', 'downside': '-20% fire rate', 'color': PURPLE}
    ]
    
    @staticmethod
    def get_available_modules(player_modules):
        """Get modules that haven't been selected yet"""
        return [m for m in Module.MODULES if m['id'] not in player_modules]
    
    @staticmethod
    def get_random_modules(player_modules, count=3):
        """Get random unique modules that haven't been selected"""
        available = Module.get_available_modules(player_modules)
        if not available:
            return []
        return random.sample(available, min(count, len(available)))
