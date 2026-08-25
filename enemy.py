import math
import random


class Enemy:
    def __init__(self, enemy_type, x, y):
        self.type = enemy_type
        self.x = x
        self.y = y
        self.radius = 16
        self.alive = True
        self.attack_timer = 0.0
        self.damage_flash = 0.0

        if enemy_type == "goblin":
            self.max_health = 40
            self.health = 40
            self.speed = 110
            self.damage = 9
            self.attack_range = 32
            self.vision = 260
            self.color = (80, 170, 90)
            self.attack_speed = 0.95
        elif enemy_type == "archer":
            self.max_health = 32
            self.health = 32
            self.speed = 90
            self.damage = 7
            self.attack_range = 260
            self.vision = 380
            self.color = (190, 185, 90)
            self.attack_speed = 1.4
        elif enemy_type == "tank":
            self.max_health = 90
            self.health = 90
            self.speed = 65
            self.damage = 15
            self.attack_range = 38
            self.vision = 330
            self.color = (130, 45, 100)
            self.attack_speed = 1.6
        elif enemy_type == "mage":
            self.max_health = 52
            self.health = 52
            self.speed = 100
            self.damage = 11
            self.attack_range = 260
            self.vision = 420
            self.color = (110, 110, 235)
            self.attack_speed = 1.25
        else:
            self.max_health = 220
            self.health = 220
            self.speed = 96
            self.damage = 20
            self.attack_range = 90
            self.vision = 600
            self.color = (240, 80, 80)
            self.attack_speed = 1.2

    def update(self, dt, player, room):
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.damage_flash = max(0.0, self.damage_flash - dt)
        if not self.alive:
            return None

        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1.0, math.hypot(dx, dy))

        if dist <= self.vision:
            direction_x = dx / dist
            direction_y = dy / dist

            if self.type in ("archer", "mage"):
                desired_dist = 170 if self.type == "archer" else 210
                if dist < desired_dist - 10:
                    self.x -= direction_x * self.speed * dt
                    self.y -= direction_y * self.speed * dt
                elif dist > desired_dist + 10:
                    self.x += direction_x * self.speed * dt
                    self.y += direction_y * self.speed * dt
            else:
                self.x += direction_x * self.speed * dt
                self.y += direction_y * self.speed * dt

            self.x = max(room.bounds.left + 40, min(room.bounds.right - 40, self.x))
            self.y = max(room.bounds.top + 40, min(room.bounds.bottom - 40, self.y))

        if dist <= self.attack_range and self.attack_timer <= 0:
            if self.type in ("archer", "mage"):
                proj_speed = 420 if self.type == "archer" else 500
                vx = (player.x - self.x) / dist * proj_speed
                vy = (player.y - self.y) / dist * proj_speed
                self.attack_timer = self.attack_speed
                return {
                    "x": self.x,
                    "y": self.y,
                    "vx": vx,
                    "vy": vy,
                    "radius": 6,
                    "damage": self.damage,
                    "color": (220, 120, 120) if self.type == "mage" else (220, 200, 120),
                    "owner": "enemy",
                    "life": 2.0,
                    "pierce": 0,
                }

            player.take_damage(self.damage)
            self.attack_timer = self.attack_speed

        return None

    def take_damage(self, amount):
        self.health -= amount
        self.damage_flash = 0.12
        if self.health <= 0:
            self.alive = False

    def draw(self, screen, camera_x=0, camera_y=0):
        if not self.alive:
            return
        color = (255, 120, 120) if self.damage_flash > 0 else self.color
        pygame = __import__('pygame')
        pygame.draw.circle(screen, color, (int(self.x + camera_x), int(self.y + camera_y)), self.radius)
        pygame.draw.circle(screen, (30, 30, 30), (int(self.x + camera_x), int(self.y + camera_y)), self.radius - 5)

        bar_width = 30
        bar_x = int(self.x + camera_x - bar_width / 2)
        bar_y = int(self.y + camera_y - self.radius - 18)
        hp_ratio = max(0.0, self.health / self.max_health)
        pygame.draw.rect(screen, (90, 90, 90), (bar_x, bar_y, bar_width, 5))
        pygame.draw.rect(screen, (180, 220, 120), (bar_x, bar_y, int(bar_width * hp_ratio), 5))
