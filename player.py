import math
import random

from weapons import Projectile, get_weapon


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.health = 100
        self.max_health = 100
        self.damage = 14
        self.speed = 240
        self.attack_speed = 1.0
        self.crit_chance = 0.12
        self.crit_damage = 1.5
        self.projectile_speed = 1.0
        self.dodge_cooldown_base = 1.2
        self.dodge_cooldown = 0.0
        self.dodge_time = 0.0
        self.attack_cooldown = 0.0
        self.weapon_name = "sword"
        self.weapon = get_weapon(self.weapon_name)
        self.gold = 0
        self.lifesteal = 0.0
        self.facing = 1.0
        self.invuln = 0.0
        self.hit_flash = 0.0

    def update(self, dt, keys, mouse_pos, room):
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.dodge_cooldown = max(0.0, self.dodge_cooldown - dt)
        self.invuln = max(0.0, self.invuln - dt)
        self.hit_flash = max(0.0, self.hit_flash - dt)

        if self.dodge_time > 0:
            self.dodge_time -= dt
            return

        move_x = (keys[ord('d')] - keys[ord('a')])
        move_y = (keys[ord('s')] - keys[ord('w')])
        if move_x or move_y:
            length = math.hypot(move_x, move_y)
            dx = (move_x / length) * self.speed * dt
            dy = (move_y / length) * self.speed * dt
            self.x += dx
            self.y += dy

        self.x = max(room.bounds.left + 30, min(room.bounds.right - 30, self.x))
        self.y = max(room.bounds.top + 30, min(room.bounds.bottom - 30, self.y))

        mx = mouse_pos[0] - self.x
        my = mouse_pos[1] - self.y
        if mx != 0 or my != 0:
            self.facing = 1 if mx >= 0 else -1

    def dodge(self):
        if self.dodge_cooldown > 0:
            return
        self.dodge_time = 0.2
        self.dodge_cooldown = self.dodge_cooldown_base
        self.invuln = 0.28

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 0.15
        self.invuln = 0.25

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def attack(self, mouse_pos, room):
        if self.attack_cooldown > 0:
            return []

        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            dist = 1

        angle = math.atan2(dy, dx)
        weapon = get_weapon(self.weapon_name)
        self.attack_cooldown = weapon.cooldown / self.attack_speed

        projectiles = []
        if weapon.is_ranged:
            speed = weapon.projectile_speed * self.projectile_speed
            projectiles.append(Projectile(
                self.x,
                self.y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                weapon.projectile_radius,
                weapon.damage * self.damage / 14,
                weapon.projectile_color,
                1.3,
                "player",
                weapon.pierce,
            ))
            return projectiles

        for enemy in room.enemies:
            if not enemy.alive:
                continue
            ex = enemy.x - self.x
            ey = enemy.y - self.y
            enemy_dist = math.hypot(ex, ey)
            if enemy_dist > weapon.range:
                continue
            enemy_angle = math.atan2(ey, ex)
            if abs(math.atan2(math.sin(angle - enemy_angle), math.cos(angle - enemy_angle))) > 1.2:
                continue
            crit = random.random() < self.crit_chance
            dmg = weapon.damage + self.damage
            if crit:
                dmg *= self.crit_damage
            enemy.take_damage(dmg)
            if self.lifesteal > 0:
                self.heal(dmg * self.lifesteal * 0.12)

        return projectiles

    def switch_weapon(self, weapon_name):
        self.weapon_name = weapon_name
        self.weapon = get_weapon(weapon_name)

    def draw(self, screen, camera_x=0, camera_y=0):
        pygame = __import__('pygame')
        px = int(self.x + camera_x)
        py = int(self.y + camera_y)
        hit_color = (255, 80, 80) if self.hit_flash > 0 else (255, 255, 255)
        pygame.draw.circle(screen, hit_color, (px, py), self.radius)
        pygame.draw.circle(screen, (30, 30, 30), (px, py), self.radius - 6)

        weapon = get_weapon(self.weapon_name)
        if weapon.name == "Sword":
            end_x = px + self.facing * 34
            end_y = py
            pygame.draw.line(screen, (205, 180, 120), (px, py), (end_x, end_y), 6)
            pygame.draw.line(screen, (255, 230, 180), (px + self.facing * 8, py - 4), (end_x, end_y), 2)
        elif weapon.name == "Greatsword":
            end_x = px + self.facing * 48
            end_y = py
            pygame.draw.line(screen, (200, 110, 90), (px, py), (end_x, end_y), 10)
            pygame.draw.line(screen, (255, 200, 160), (px + self.facing * 8, py - 5), (end_x, end_y), 3)
        elif weapon.name == "Bow":
            end_x = px + self.facing * 40
            end_y = py
            pygame.draw.line(screen, (200, 170, 90), (px, py), (end_x, end_y), 4)
            pygame.draw.arc(screen, (180, 150, 80), (px + self.facing * 10, py - 12, 32, 24), 0 if self.facing > 0 else 3.14, 3.14 if self.facing > 0 else 6.28, 3)
        elif weapon.name == "Staff":
            end_x = px + self.facing * 42
            end_y = py
            pygame.draw.line(screen, (120, 140, 255), (px, py), (end_x, end_y), 5)
            pygame.draw.circle(screen, (130, 180, 255), (end_x, end_y), 6)