import random

UPGRADE_POOL = [
    {"name": "Max HP +20", "type": "max_hp", "value": 20},
    {"name": "Damage +3", "type": "damage", "value": 3},
    {"name": "Attack Speed +8%", "type": "attack_speed", "value": 0.08},
    {"name": "Move Speed +8%", "type": "move_speed", "value": 0.08},
    {"name": "Crit Chance +4%", "type": "crit_chance", "value": 0.04},
    {"name": "Crit Damage +20%", "type": "crit_damage", "value": 0.2},
    {"name": "Projectile Speed +15%", "type": "projectile_speed", "value": 0.15},
    {"name": "Dodge Cooldown -10%", "type": "dodge_cooldown", "value": 0.1},
    {"name": "Lifesteal +8%", "type": "lifesteal", "value": 0.08},
]


def get_random_upgrades(count=3):
    selected = random.sample(UPGRADE_POOL, k=min(count, len(UPGRADE_POOL)))
    return selected


def apply_upgrade(player, upgrade):
    stat = upgrade["type"]
    if stat == "max_hp":
        player.max_health += int(upgrade["value"])
        player.health = min(player.max_health, player.health + int(upgrade["value"]))
    elif stat == "damage":
        player.damage += upgrade["value"]
    elif stat == "move_speed":
        player.speed *= 1 + upgrade["value"]
    elif stat == "attack_speed":
        player.attack_speed *= 1 - min(upgrade["value"], 0.3)
    elif stat == "crit_chance":
        player.crit_chance = min(0.75, player.crit_chance + upgrade["value"])
    elif stat == "crit_damage":
        player.crit_damage += upgrade["value"]
    elif stat == "projectile_speed":
        player.projectile_speed *= 1 + upgrade["value"]
    elif stat == "dodge_cooldown":
        player.dodge_cooldown_base *= 1 - min(upgrade["value"], 0.3)
    elif stat == "lifesteal":
        player.lifesteal += upgrade["value"]
