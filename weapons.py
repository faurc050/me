from dataclasses import dataclass


@dataclass
class Weapon:
    name: str
    damage: float
    range: float
    cooldown: float
    projectile_speed: float = 0.0
    projectile_color: tuple = (255, 255, 255)
    projectile_radius: int = 5
    is_ranged: bool = False
    pierce: int = 0


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    damage: float
    color: tuple
    life: float
    owner: str
    pierce: int = 0


def get_weapon_catalog():
    return {
        "sword": Weapon("Sword", 14, 85, 0.38),
        "greatsword": Weapon("Greatsword", 26, 110, 0.72),
        "bow": Weapon("Bow", 11, 420, 0.58, projectile_speed=550, projectile_color=(216, 200, 100), projectile_radius=5, is_ranged=True),
        "staff": Weapon("Staff", 15, 420, 0.52, projectile_speed=620, projectile_color=(120, 150, 255), projectile_radius=6, is_ranged=True, pierce=1),
    }


def get_weapon(name: str):
    return get_weapon_catalog()[name]