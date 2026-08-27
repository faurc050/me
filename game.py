import json
import math
import os
import random

import pygame

from audio import AudioManager

WIDTH, HEIGHT = 1280, 720
ROOM_W, ROOM_H = 1180, 600
SAVE_PATH = os.path.join(os.path.dirname(__file__), "savegame.json")


class Weapon:
    def __init__(self, name, damage, range_, cooldown, projectile_speed=0, projectile_color=(255, 255, 255), projectile_radius=5, is_ranged=False, pierce=0):
        self.name = name
        self.damage = damage
        self.range = range_
        self.cooldown = cooldown
        self.projectile_speed = projectile_speed
        self.projectile_color = projectile_color
        self.projectile_radius = projectile_radius
        self.is_ranged = is_ranged
        self.pierce = pierce


WEAPONS = {
    "sword": Weapon("Sword", 12, 75, 0.38),
    "greatsword": Weapon("Greatsword", 22, 100, 0.75),
    "bow": Weapon("Bow", 9, 420, 0.46, 500, (221, 200, 100), 5, True),
    "staff": Weapon("Staff", 11, 440, 0.42, 560, (120, 170, 255), 6, True, 1),
    "reaver": Weapon("Reaver", 30, 118, 0.72),
    "phoenix_bow": Weapon("Phoenix Bow", 15, 500, 0.38, 640, (255, 170, 90), 7, True),
    "arcane_staff": Weapon("Arcane Staff", 18, 530, 0.34, 700, (155, 110, 255), 7, True, 2),
    "voidblade": Weapon("Voidblade", 38, 132, 0.68),
}


class Projectile:
    def __init__(self, x, y, vx, vy, radius, damage, color, owner):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.damage = damage
        self.color = color
        self.owner = owner
        self.life = 1.8

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt


class Drop:
    def __init__(self, x, y, kind, value=1):
        self.x = x
        self.y = y
        self.kind = kind
        self.value = value
        self.radius = 8
        self.life = 18.0
        self.color = {"gold": (238, 204, 96), "essence": (128, 196, 255), "vital": (120, 255, 160), "heal": (120, 255, 140)}[kind]
        self.vx = random.uniform(-18, 18)
        self.vy = random.uniform(-14, 14)

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.97
        self.vy *= 0.97

    def draw(self, screen):
        glow = max(3, int(self.radius + 5 + (1.0 - min(self.life, 12.0) / 12.0) * 12))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), glow)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), max(2, self.radius - 2))


class HealingWell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.cooldown = 0.0
        self.pulse = 0.0

    def update(self, dt):
        self.cooldown = max(0.0, self.cooldown - dt)
        self.pulse = max(0.0, self.pulse - dt)

    def draw(self, screen):
        glow = 18 + int(8 * math.sin(pygame.time.get_ticks() * 0.006))
        pygame.draw.circle(screen, (90, 220, 140), (int(self.x), int(self.y)), glow, 2)
        pygame.draw.circle(screen, (120, 255, 170), (int(self.x), int(self.y)), max(6, glow // 3))


class Room:
    def __init__(self, kind, x=80, y=80, w=ROOM_W, h=ROOM_H):
        self.kind = kind
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left = x
        self.top = y
        self.right = x + w
        self.bottom = y + h
        self.neighbors = {}
        self.doors = {"left": False, "right": False, "up": False, "down": False}
        self.enemies = []
        self.spawned = False
        self.cleared = False
        self.upgrade_given = False
        self.theme = random.choice(["stone", "crypt", "forge", "swamp"])
        self.healing_well = None

    def center_x(self):
        return self.x + self.w / 2

    def center_y(self):
        return self.y + self.h / 2


class Enemy:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 16
        self.attack_cooldown = 0
        self.alive = True
        self.color = (200, 200, 200)
        self.speed = 0
        self.health = 0
        self.max_health = 0
        self.damage = 0
        self.attack_range = 0
        self.vision = 350
        self.charge_timer = 0.0
        self.roared = False

        if kind == "goblin":
            self.max_health = 28
            self.health = 28
            self.speed = 110
            self.damage = 8
            self.attack_range = 35
            self.color = (100, 180, 90)
        elif kind == "archer":
            self.max_health = 24
            self.health = 24
            self.speed = 90
            self.damage = 6
            self.attack_range = 200
            self.color = (185, 180, 90)
            self.vision = 400
        elif kind == "tank":
            self.max_health = 72
            self.health = 72
            self.speed = 60
            self.damage = 14
            self.attack_range = 42
            self.color = (170, 80, 125)
        elif kind == "brute":
            self.max_health = 54
            self.health = 54
            self.speed = 135
            self.damage = 16
            self.attack_range = 44
            self.color = (190, 90, 110)
        elif kind == "mage":
            self.max_health = 34
            self.health = 34
            self.speed = 80
            self.damage = 11
            self.attack_range = 260
            self.color = (120, 116, 220)
            self.vision = 520
        elif kind == "runner":
            self.max_health = 18
            self.health = 18
            self.speed = 175
            self.damage = 9
            self.attack_range = 28
            self.color = (200, 200, 110)
        elif kind == "boss":
            self.max_health = 220
            self.health = 220
            self.speed = 95
            self.damage = 18
            self.attack_range = 75
            self.color = (220, 80, 80)
            self.radius = 28
            self.vision = 560
        else:
            self.max_health = 20
            self.health = 20
            self.speed = 100
            self.damage = 7
            self.attack_range = 35

    def scale_for_floor(self, floor):
        if floor <= 1:
            return
        scale = 1.0 + (floor - 1) * 0.18
        self.max_health = int(self.max_health * scale)
        self.health = self.max_health
        self.damage = int(self.damage * (1.0 + (floor - 1) * 0.13))
        self.speed *= 1.0 + (floor - 1) * 0.04
        if self.kind in ("archer", "mage"):
            self.vision *= 1.0 + (floor - 1) * 0.05

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 0.12
        if self.health <= 0:
            self.alive = False
        return amount

    def update(self, dt, player, room, projectiles):
        if not self.alive:
            return

        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.charge_timer = max(0.0, self.charge_timer - dt)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1.0, math.hypot(dx, dy))

        if self.kind == "boss":
            if self.charge_timer > 0:
                move = self.speed * 2.1 * dt
                self.x += (dx / dist) * move
                self.y += (dy / dist) * move
            elif dist <= self.vision:
                move = self.speed * dt
                self.x += (dx / dist) * move * 0.8
                self.y += (dy / dist) * move * 0.8
                if dist < 180:
                    self.x -= (dx / dist) * move * 0.4
                    self.y -= (dy / dist) * move * 0.4

            if self.attack_cooldown <= 0 and dist <= 540:
                if dist < 220:
                    burst_count = 8
                    for i in range(burst_count):
                        angle = (2 * math.pi * i / burst_count) + (self.x * 0.01)
                        speed = 420
                        projectiles.append(Projectile(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, 7, self.damage, (255, 120, 120), "enemy"))
                    self.attack_cooldown = 1.3
                else:
                    angle = math.atan2(dy, dx)
                    spread = [-0.25, 0, 0.25]
                    for offset in spread:
                        rad = angle + offset
                        projectiles.append(Projectile(self.x, self.y, math.cos(rad) * 470, math.sin(rad) * 470, 8, self.damage, (255, 90, 120), "enemy"))
                    self.attack_cooldown = 1.1
                    self.charge_timer = 0.6
                return
        elif dist <= self.vision:
            if self.kind in ("archer", "mage"):
                desired = 180 if self.kind == "archer" else 210
                if dist < desired:
                    move = self.speed * dt
                    self.x -= (dx / dist) * move
                    self.y -= (dy / dist) * move
                elif dist > desired:
                    move = self.speed * dt
                    self.x += (dx / dist) * move
                    self.y += (dy / dist) * move
            else:
                move = self.speed * dt
                self.x += (dx / dist) * move
                self.y += (dy / dist) * move

            self.x = max(room.left + 35, min(room.right - 35, self.x))
            self.y = max(room.top + 35, min(room.bottom - 35, self.y))

        if self.kind == "mage" and self.attack_cooldown <= 0 and dist <= self.attack_range + 20:
            angle = math.atan2(dy, dx)
            for offset in (-0.35, 0.0, 0.35):
                rad = angle + offset
                projectiles.append(Projectile(self.x, self.y, math.cos(rad) * 340, math.sin(rad) * 340, 6, self.damage, (130, 140, 255), "enemy"))
            self.attack_cooldown = 1.8
            return

        if self.kind in ("archer", "boss") and self.attack_cooldown <= 0 and dist <= self.attack_range + 10:
            angle = math.atan2(dy, dx)
            speed = 480 if self.kind == "archer" else 420
            projectiles.append(Projectile(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, 7 if self.kind == "archer" else 10, self.damage, (220, 205, 120) if self.kind == "archer" else (255, 105, 105), "enemy"))
            self.attack_cooldown = 1.2 if self.kind == "archer" else 1.6
            return

        if dist <= self.attack_range and self.attack_cooldown <= 0:
            self.attack_cooldown = 1.1 if self.kind in ("goblin", "runner") else 1.6
            player.take_damage(self.damage)

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.ellipse(screen, (0, 0, 0), (int(self.x - self.radius * 1.1), int(self.y - self.radius * 0.5), int(self.radius * 2.2), int(self.radius * 1.1)))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (35, 35, 35), (int(self.x), int(self.y)), max(4, self.radius - 5))

        bar_w = 32
        bar_x = int(self.x - bar_w / 2)
        bar_y = int(self.y - self.radius - 16)
        ratio = max(0.0, self.health / self.max_health)
        pygame.draw.rect(screen, (70, 70, 70), (bar_x, bar_y, bar_w, 5))
        pygame.draw.rect(screen, (110, 220, 120), (bar_x, bar_y, int(bar_w * ratio), 5))


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.speed = 230
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.stamina = 100
        self.max_stamina = 100
        self.damage = 12
        self.weapon_name = "sword"
        self.attack_cooldown = 0.0
        self.angle = 0.0
        self.attack_pulse = 0.0
        self.gold = 0
        self.crit_chance = 0.12
        self.crit_damage = 1.6
        self.dodge_cooldown = 0.0
        self.dodge_time = 0.0
        self.hit_flash = 0.0
        self.lifesteal = 0.0
        self.dash_cooldown = 0.0
        self.dash_time = 0.0
        self.deflect_cooldown = 0.0
        self.heal_potions = 1

    def update(self, dt, keys, room, mouse_pos):
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.attack_pulse = max(0.0, self.attack_pulse - dt)
        self.dodge_cooldown = max(0.0, self.dodge_cooldown - dt)
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.deflect_cooldown = max(0.0, self.deflect_cooldown - dt)

        if self.dodge_time > 0:
            self.dodge_time -= dt
            return

        sprinting = False
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and (keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]):
            if self.stamina > 0:
                sprinting = True
                self.stamina = max(0.0, self.stamina - 28.0 * dt)
            else:
                self.stamina = min(self.max_stamina, self.stamina + 18.0 * dt)
        else:
            self.stamina = min(self.max_stamina, self.stamina + 22.0 * dt)

        mx = keys[pygame.K_d] - keys[pygame.K_a]
        my = keys[pygame.K_s] - keys[pygame.K_w]
        if mx or my:
            length = math.hypot(mx, my)
            speed = self.speed * (1.7 if sprinting else 1.0)
            self.x += (mx / length) * speed * dt
            self.y += (my / length) * speed * dt

        self.x = max(room.left + 30, min(room.right - 30, self.x))
        self.y = max(room.top + 30, min(room.bottom - 30, self.y))

        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        if dx != 0 or dy != 0:
            self.angle = math.atan2(dy, dx)

    def take_damage(self, amount):
        reduction = min(0.75, self.armor / 150.0)
        safe_amount = max(1, int(amount * (1.0 - reduction)))
        self.health -= safe_amount
        self.hit_flash = 0.18
        return safe_amount

    def dodge(self):
        if self.dodge_cooldown > 0:
            return False
        self.dodge_cooldown = 1.2
        self.dodge_time = 0.18
        return True

    def dash(self):
        if self.dash_cooldown > 0:
            return False
        self.dash_cooldown = 1.8
        self.dash_time = 0.18
        return True

    def deflect(self, projectiles):
        if self.deflect_cooldown > 0:
            return False
        self.deflect_cooldown = 2.8
        reflected = 0
        for projectile in projectiles:
            if projectile.owner != "enemy":
                continue
            if math.hypot(projectile.x - self.x, projectile.y - self.y) < 90:
                projectile.owner = "player"
                projectile.vx *= -1.25
                projectile.vy *= -1.25
                projectile.damage += self.damage * 0.55
                projectile.color = (180, 220, 255)
                reflected += 1
        return reflected > 0

    def attack(self, mouse_pos, room, enemies, projectiles):
        weapon = WEAPONS[self.weapon_name]
        if self.attack_cooldown > 0:
            return False
        self.attack_cooldown = weapon.cooldown
        self.attack_pulse = 0.22

        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        angle = math.atan2(dy, dx)
        self.angle = angle

        if weapon.is_ranged:
            speed = weapon.projectile_speed
            projectiles.append(Projectile(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, weapon.projectile_radius, weapon.damage + self.damage * 0.4, weapon.projectile_color, "player"))
            return {"projectile": True, "damage": int(weapon.damage + self.damage * 0.4)}

        for enemy in enemies:
            if not enemy.alive:
                continue
            ex = enemy.x - self.x
            ey = enemy.y - self.y
            dist = math.hypot(ex, ey)
            if dist > weapon.range:
                continue
            enemy_angle = math.atan2(ey, ex)
            delta = abs(math.atan2(math.sin(angle - enemy_angle), math.cos(angle - enemy_angle)))
            if delta > 1.2:
                continue
            crit = random.random() < self.crit_chance
            dmg = weapon.damage + self.damage
            if crit:
                dmg *= self.crit_damage
            damage_done = enemy.take_damage(dmg)
            if self.lifesteal > 0:
                self.health = min(self.max_health, self.health + dmg * self.lifesteal * 0.1)
            return {"enemy": enemy, "damage": int(damage_done), "critical": crit}
        return False

    def draw(self, screen):
        px = int(self.x)
        py = int(self.y)
        color = (255, 120, 120) if self.hit_flash > 0 else (255, 255, 255)
        pygame.draw.circle(screen, color, (px, py), self.radius)
        pygame.draw.circle(screen, (35, 35, 35), (px, py), self.radius - 6)

        weapon = WEAPONS[self.weapon_name]
        arm_x = px + math.cos(self.angle) * 18
        arm_y = py + math.sin(self.angle) * 18
        end_x = px + math.cos(self.angle) * 38
        end_y = py + math.sin(self.angle) * 38

        if weapon.name == "Sword":
            swing_alpha = max(0.0, self.attack_pulse / 0.22)
            swing_len = 28 + int(26 * swing_alpha)
            swing_end_x = px + math.cos(self.angle) * swing_len
            swing_end_y = py + math.sin(self.angle) * swing_len
            pygame.draw.line(screen, (220, 180, 110), (px, py), (swing_end_x, swing_end_y), 6)
            pygame.draw.line(screen, (255, 230, 180), (arm_x, arm_y), (swing_end_x, swing_end_y), 2)
            for offset in range(8):
                arc_x = px + math.cos(self.angle) * (18 + offset * 3)
                arc_y = py + math.sin(self.angle) * (18 + offset * 3)
                pygame.draw.circle(screen, (255, 190, 110), (int(arc_x), int(arc_y)), 2 + int(swing_alpha * 4))
        elif weapon.name == "Greatsword":
            end_x = px + math.cos(self.angle) * 54
            end_y = py + math.sin(self.angle) * 54
            pygame.draw.line(screen, (195, 120, 90), (px, py), (end_x, end_y), 10)
            pygame.draw.line(screen, (255, 200, 160), (arm_x, arm_y), (end_x, end_y), 3)
            if self.attack_pulse > 0:
                glow_r = 18 + int(18 * (self.attack_pulse / 0.22))
                pygame.draw.circle(screen, (255, 150, 120), (int(end_x), int(end_y)), glow_r, 2)
        elif weapon.name == "Bow":
            end_x = px + math.cos(self.angle) * 34
            end_y = py + math.sin(self.angle) * 34
            pygame.draw.line(screen, (205, 168, 90), (px, py), (end_x, end_y), 4)
            arc_rect = pygame.Rect(int(px + math.cos(self.angle) * 10 - 16), int(py + math.sin(self.angle) * 10 - 16), 32, 32)
            pygame.draw.arc(screen, (220, 180, 100), arc_rect, self.angle - 1.1, self.angle + 1.1, 3)
        elif weapon.name == "Staff":
            end_x = px + math.cos(self.angle) * 40
            end_y = py + math.sin(self.angle) * 40
            pygame.draw.line(screen, (110, 135, 255), (px, py), (end_x, end_y), 5)
            pygame.draw.circle(screen, (140, 180, 255), (int(end_x), int(end_y)), 6)
            if self.attack_pulse > 0:
                wave = int(12 + 18 * (self.attack_pulse / 0.22))
                pygame.draw.circle(screen, (180, 220, 255), (int(end_x), int(end_y)), wave, 2)


class FloatingText:
    def __init__(self, x, y, text, color, life=0.8, size=20):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size

    def update(self, dt):
        self.life -= dt
        self.y -= 26 * dt

    def draw(self, screen, font):
        alpha = max(0, min(1.0, self.life / max(0.1, self.max_life)))
        color = (*self.color[:3], int(alpha * 255))
        rendered = font.render(self.text, True, color)
        screen.blit(rendered, (int(self.x), int(self.y)))


class Dungeon:
    def __init__(self):
        self.rooms = {}
        self.current_room_id = 0
        self.positions = {}

    def generate(self):
        self.rooms = {}
        self.positions = {0: (0, 0)}
        self.current_room_id = 0
        self.rooms[0] = Room("start", 80, 80, ROOM_W, ROOM_H)
        next_id = 1

        for _ in range(8):
            parent_id = random.choice(list(self.rooms.keys()))
            px, py = self.positions[parent_id]
            options = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(options)
            placed = False
            for dx, dy in options:
                nx, ny = px + dx, py + dy
                if any(pos == (nx, ny) for pos in self.positions.values()):
                    continue
                self.positions[next_id] = (nx, ny)
                self.rooms[next_id] = Room("normal", 80, 80, ROOM_W, ROOM_H)
                next_id += 1
                placed = True
                break
            if not placed:
                break

        if self.rooms:
            boss_id = max(self.rooms.keys(), key=lambda rid: abs(self.positions[rid][0]) + abs(self.positions[rid][1]))
            self.rooms[boss_id].kind = "boss"
            normal_ids = [rid for rid in self.rooms if self.rooms[rid].kind == "normal"]
            if normal_ids:
                shop_id = random.choice(normal_ids)
                self.rooms[shop_id].kind = "shop"

        for rid, pos in self.positions.items():
            for other_id, other_pos in self.positions.items():
                if rid == other_id:
                    continue
                if abs(pos[0] - other_pos[0]) + abs(pos[1] - other_pos[1]) != 1:
                    continue
                room = self.rooms[rid]
                other = self.rooms[other_id]
                if pos[0] < other_pos[0]:
                    room.neighbors["right"] = other_id
                    other.neighbors["left"] = rid
                    room.doors["right"] = True
                    other.doors["left"] = True
                elif pos[0] > other_pos[0]:
                    room.neighbors["left"] = other_id
                    other.neighbors["right"] = rid
                    room.doors["left"] = True
                    other.doors["right"] = True
                elif pos[1] < other_pos[1]:
                    room.neighbors["down"] = other_id
                    other.neighbors["up"] = rid
                    room.doors["down"] = True
                    other.doors["up"] = True
                elif pos[1] > other_pos[1]:
                    room.neighbors["up"] = other_id
                    other.neighbors["down"] = rid
                    room.doors["up"] = True
                    other.doors["down"] = True

    def current_room(self):
        return self.rooms[self.current_room_id]

    def room_name(self):
        names = {"start": "Starting Chamber", "normal": "Dungeon Room", "shop": "Shop Room", "boss": "Boss Room"}
        return names.get(self.current_room().kind, "Dungeon")


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dungeon Warden v1.0.2")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.big_font = pygame.font.SysFont("arial", 42, bold=True)
        self.audio = AudioManager()
        self.dungeon = Dungeon()
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.current_room = None
        self.state = "menu"
        self.menu_buttons = []
        self.projectiles = []
        self.drops = []
        self.damage_texts = []
        self.keys = None
        self.pending_choices = []
        self.pending_boxes = []
        self.shop_choices = []
        self.shop_boxes = []
        self.shop_costs = []
        self.shop_leave_button = None
        self.shop_room_id = None
        self.transition_lock = 0.0
        self.near_door = None
        self.door_pos = None
        self.current_floor = 1
        self.max_floor = 4
        self.unlocked_weapons = {"sword"}
        self.weapon_unlocks = {"greatsword": 2, "bow": 2, "staff": 2, "reaver": 3, "phoenix_bow": 3, "arcane_staff": 4, "voidblade": 5}
        self.boss_intro_timer = 0.0
        self.phase_message_timer = 0.0
        self.settings = {"music": True, "shadows": True}
        self.audio.play_theme("menu")

    def save_game(self):
        data = {
            "current_floor": self.current_floor,
            "max_floor": self.max_floor,
            "player": {
                "x": self.player.x,
                "y": self.player.y,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "damage": self.player.damage,
                "gold": self.player.gold,
                "armor": self.player.armor,
                "weapon_name": self.player.weapon_name,
                "heal_potions": self.player.heal_potions,
                "crit_chance": self.player.crit_chance,
                "crit_damage": self.player.crit_damage,
                "lifesteal": self.player.lifesteal,
            },
            "unlocked_weapons": sorted(self.unlocked_weapons),
            "settings": self.settings,
            "room": self.dungeon.current_room_id if self.dungeon is not None else 0,
            "dungeon": {"rooms": []},
        }
        with open(SAVE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def load_game(self):
        if not os.path.exists(SAVE_PATH):
            return False
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception:
            return False
        self.current_floor = int(data.get("current_floor", 1))
        self.max_floor = int(data.get("max_floor", 4))
        self.settings = data.get("settings", self.settings)
        self.audio.music_muted = not self.settings.get("music", True)
        self.unlocked_weapons = set(data.get("unlocked_weapons", ["sword"]))
        self.dungeon.generate()
        self.current_room = self.dungeon.current_room()
        self.dungeon.current_room_id = int(data.get("room", 0))
        self.current_room = self.dungeon.rooms.get(self.dungeon.current_room_id, self.dungeon.current_room())
        self.player = Player(self.current_room.center_x(), self.current_room.center_y())
        p = data.get("player", {})
        self.player.x = float(p.get("x", WIDTH / 2))
        self.player.y = float(p.get("y", HEIGHT / 2))
        self.player.health = float(p.get("health", self.player.max_health))
        self.player.max_health = float(p.get("max_health", self.player.max_health))
        self.player.damage = float(p.get("damage", self.player.damage))
        self.player.gold = int(p.get("gold", 0))
        self.player.armor = int(p.get("armor", 0))
        self.player.weapon_name = p.get("weapon_name", "sword")
        self.player.heal_potions = int(p.get("heal_potions", 1))
        self.player.crit_chance = float(p.get("crit_chance", self.player.crit_chance))
        self.player.crit_damage = float(p.get("crit_damage", self.player.crit_damage))
        self.player.lifesteal = float(p.get("lifesteal", self.player.lifesteal))
        self.projectiles = []
        self.drops = []
        self.damage_texts = []
        self.pending_choices = []
        self.pending_boxes = []
        self.shop_choices = []
        self.shop_boxes = []
        self.shop_costs = []
        self.shop_leave_button = None
        self.shop_room_id = None
        self.transition_lock = 0.0
        self.near_door = None
        self.door_pos = None
        self.state = "playing"
        self.audio.play_theme("game")
        self.spawn_room_enemies()
        return True

    def maybe_unlock_weapons(self):
        for weapon_name, floor_needed in self.weapon_unlocks.items():
            if self.current_floor >= floor_needed:
                self.unlocked_weapons.add(weapon_name)
        if self.player.weapon_name not in self.unlocked_weapons:
            self.player.weapon_name = "sword"

    def start_run(self):
        self.current_floor = 1
        self.max_floor = 4
        self.unlocked_weapons = {"sword"}
        self.dungeon.generate()
        self.current_room = self.dungeon.current_room()
        self.current_room.spawned = False
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.projectiles = []
        self.drops = []
        self.damage_texts = []
        self.pending_choices = []
        self.pending_boxes = []
        self.shop_choices = []
        self.shop_boxes = []
        self.shop_costs = []
        self.shop_leave_button = None
        self.shop_room_id = None
        self.transition_lock = 0.0
        self.near_door = None
        self.door_pos = None
        self.boss_intro_timer = 0.0
        self.phase_message_timer = 0.0
        self.maybe_unlock_weapons()
        self.state = "playing"
        self.audio.play_theme("game")
        self.spawn_room_enemies()
        if self.current_room.kind == "boss":
            self.boss_intro_timer = 2.8

    def advance_floor(self):
        if self.current_floor >= self.max_floor:
            self.state = "victory"
            self.audio.play("victory")
            return

        self.current_floor += 1
        self.maybe_unlock_weapons()
        self.dungeon.generate()
        self.dungeon.current_room_id = 0
        self.current_room = self.dungeon.current_room()
        self.current_room.spawned = False
        self.player.x = WIDTH // 2
        self.player.y = HEIGHT // 2
        self.player.health = min(self.player.max_health, self.player.health + 18)
        self.projectiles = []
        self.drops = []
        self.damage_texts = []
        self.pending_choices = []
        self.pending_boxes = []
        self.shop_choices = []
        self.shop_boxes = []
        self.shop_costs = []
        self.shop_leave_button = None
        self.shop_room_id = None
        self.transition_lock = 0.0
        self.near_door = None
        self.door_pos = None
        self.boss_intro_timer = 0.0
        self.phase_message_timer = 0.0
        self.state = "playing"
        self.audio.play_theme("game")
        self.spawn_room_enemies()
        if self.current_room.kind == "boss":
            self.boss_intro_timer = 2.8

    def spawn_room_enemies(self):
        room = self.current_room
        if room.spawned:
            return
        room.enemies = []
        if room.kind == "start":
            enemies = [Enemy("goblin", room.left + 250, room.top + 260), Enemy("goblin", room.right - 250, room.top + 320)]
            for enemy in enemies:
                enemy.scale_for_floor(self.current_floor)
            room.enemies = enemies
        elif room.kind == "shop":
            room.enemies = []
        elif room.kind == "boss":
            boss = Enemy("boss", room.center_x(), room.center_y())
            boss.scale_for_floor(self.current_floor)
            room.enemies = [boss]
        else:
            count = 2 + self.current_floor * 2 + random.randint(0, 3)
            count = min(count, 12)
            kinds = ["goblin", "goblin", "archer", "tank", "brute", "mage", "runner"]
            door_positions = {
                "left": (room.left + 40, room.center_y()),
                "right": (room.right - 40, room.center_y()),
                "up": (room.center_x(), room.top + 40),
                "down": (room.center_x(), room.bottom - 40),
            }
            for _ in range(count):
                kind = random.choice(kinds)
                placed = False
                for _ in range(60):
                    x = random.randint(room.left + 120, room.right - 120)
                    y = random.randint(room.top + 120, room.bottom - 120)
                    if min(math.hypot(x - px, y - py) for px, py in door_positions.values()) > 160:
                        placed = True
                        break
                if not placed:
                    x = room.center_x()
                    y = room.center_y()
                enemy = Enemy(kind, x, y)
                enemy.scale_for_floor(self.current_floor)
                room.enemies.append(enemy)
        if self.current_floor >= 2 and random.random() < 0.35:
            room.healing_well = HealingWell(room.center_x() + random.uniform(-120, 120), room.center_y() + random.uniform(-90, 90))
        else:
            room.healing_well = None
        room.spawned = True
        room.cleared = False
        room.upgrade_given = False

    def spawn_enemy_drop(self, enemy):
        if not enemy.alive:
            return
        if enemy.kind == "boss":
            for i in range(10):
                self.drops.append(Drop(enemy.x + random.uniform(-20, 20), enemy.y + random.uniform(-20, 20), "essence", 1))
            self.drops.append(Drop(enemy.x, enemy.y, "vital", 1))
            self.player.gold += 40
            self.player.health = min(self.player.max_health, self.player.health + 12)
        else:
            if random.random() < 0.85:
                roll = random.random()
                if roll < 0.55:
                    kind = "gold"
                elif roll < 0.85:
                    kind = "essence"
                else:
                    kind = "heal"
                self.drops.append(Drop(enemy.x, enemy.y, kind, 1))

    def apply_upgrade(self, upgrade):
        typ = upgrade["type"]
        if typ == "max_health":
            self.player.max_health += int(upgrade["value"])
            self.player.health = self.player.max_health
        elif typ == "damage":
            self.player.damage += upgrade["value"]
        elif typ == "speed":
            self.player.speed *= 1.0 + upgrade["value"]
        elif typ == "crit_chance":
            self.player.crit_chance = min(0.75, self.player.crit_chance + upgrade["value"])
        elif typ == "crit_damage":
            self.player.crit_damage += upgrade["value"]
        elif typ == "dodge":
            self.player.dodge_cooldown = max(0.1, self.player.dodge_cooldown - 0.2)
        elif typ == "lifesteal":
            self.player.lifesteal += upgrade["value"]
        elif typ == "weapon":
            self.unlocked_weapons.add(upgrade["value"])
            self.player.weapon_name = upgrade["value"]
        elif typ == "heal":
            self.player.health = min(self.player.max_health, self.player.health + int(upgrade["value"]))
        elif typ == "armor":
            self.player.armor += int(upgrade["value"])
        elif typ == "potion":
            self.player.heal_potions += int(upgrade["value"])

    def random_upgrades(self):
        pool = [
            {"name": "Max HP +20", "type": "max_health", "value": 20, "rarity": "common"},
            {"name": "Damage +3", "type": "damage", "value": 3, "rarity": "common"},
            {"name": "Move Speed +10%", "type": "speed", "value": 0.1, "rarity": "common"},
            {"name": "Crit Chance +5%", "type": "crit_chance", "value": 0.05, "rarity": "common"},
            {"name": "Dodge Boost", "type": "dodge", "value": 0.15, "rarity": "common"},
            {"name": "Armor +6", "type": "armor", "value": 6, "rarity": "common"},
            {"name": "Potion +1", "type": "potion", "value": 1, "rarity": "common"},
            {"name": "Lifesteal +8%", "type": "lifesteal", "value": 0.08, "rarity": "uncommon"},
            {"name": "Heal +15", "type": "heal", "value": 15, "rarity": "common"},
            {"name": "Crit Damage +20%", "type": "crit_damage", "value": 0.2, "rarity": "uncommon"},
            {"name": "Greatsword", "type": "weapon", "value": "greatsword", "rarity": "rare"},
            {"name": "Bow", "type": "weapon", "value": "bow", "rarity": "rare"},
            {"name": "Staff", "type": "weapon", "value": "staff", "rarity": "rare"},
            {"name": "Reaver", "type": "weapon", "value": "reaver", "rarity": "epic"},
            {"name": "Phoenix Bow", "type": "weapon", "value": "phoenix_bow", "rarity": "epic"},
            {"name": "Arcane Staff", "type": "weapon", "value": "arcane_staff", "rarity": "epic"},
            {"name": "Voidblade", "type": "weapon", "value": "voidblade", "rarity": "legendary"},
            {"name": "Max HP +40", "type": "max_health", "value": 40, "rarity": "uncommon"},
            {"name": "Damage +6", "type": "damage", "value": 6, "rarity": "uncommon"},
            {"name": "Move Speed +18%", "type": "speed", "value": 0.18, "rarity": "uncommon"},
            {"name": "Crit Chance +10%", "type": "crit_chance", "value": 0.10, "rarity": "rare"},
            {"name": "Armor +12", "type": "armor", "value": 12, "rarity": "uncommon"},
        ]

        for option in pool:
            if option["type"] == "weapon" and option["value"] not in self.unlocked_weapons:
                option["rarity"] = "legendary" if option["rarity"] == "legendary" else "epic"

        weights = {"common": 70, "uncommon": 25, "rare": 8, "epic": 4, "legendary": 1}
        selected = []
        seen = set()
        while len(selected) < 3:
            option = random.choices(pool, weights=[weights.get(item["rarity"], 1) for item in pool], k=1)[0]
            key = (option["type"], option.get("value"), option["name"])
            if key in seen:
                continue
            seen.add(key)
            option["display_name"] = f"{option['rarity'].title()} {option['name']}"
            selected.append(option)
        return selected[:3]

    def transition_to(self, direction):
        room = self.current_room
        if direction not in room.neighbors:
            return
        next_id = room.neighbors[direction]
        self.current_room = self.dungeon.rooms[next_id]
        self.dungeon.current_room_id = next_id
        self.transition_lock = 0.25
        self.near_door = None
        self.door_pos = None
        self.spawn_room_enemies()

        if direction == "left":
            self.player.x = self.current_room.right - 60
            self.player.y = self.current_room.center_y()
        elif direction == "right":
            self.player.x = self.current_room.left + 60
            self.player.y = self.current_room.center_y()
        elif direction == "up":
            self.player.x = self.current_room.center_x()
            self.player.y = self.current_room.bottom - 60
        elif direction == "down":
            self.player.x = self.current_room.center_x()
            self.player.y = self.current_room.top + 60

    def get_door_prompt(self):
        room = self.current_room
        if room is None:
            return None, None

        door_positions = {
            "left": (room.left + 12, room.center_y()),
            "right": (room.right - 12, room.center_y()),
            "up": (room.center_x(), room.top + 12),
            "down": (room.center_x(), room.bottom - 12),
        }

        for direction in ("left", "right", "up", "down"):
            if direction not in room.neighbors or not room.doors.get(direction):
                continue
            x, y = door_positions[direction]
            if math.hypot(self.player.x - x, self.player.y - y) < 80:
                return direction, (x, y)
        return None, None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.state == "menu":
                    if self.menu_buttons is not None:
                        for button in self.menu_buttons:
                            if button["rect"].collidepoint(pos):
                                action = button["action"]
                                if action == "start":
                                    self.start_run()
                                elif action == "load":
                                    self.load_game()
                                elif action == "settings":
                                    self.state = "settings"
                                break
                elif self.state == "playing":
                    hit = self.player.attack(pos, self.current_room, self.current_room.enemies, self.projectiles)
                    if hit:
                        self.audio.play("attack" if not WEAPONS[self.player.weapon_name].is_ranged else "shoot")
                        self.audio.play("sword_voice")
                        if isinstance(hit, dict) and hit.get("enemy") is not None:
                            info = hit
                            base = info["enemy"].x
                            base_y = info["enemy"].y - 18
                            label = f"{int(info['damage'])}"
                            if info.get("critical"):
                                label = f"CRIT {int(info['damage'])}"
                                self.damage_texts.append(FloatingText(base, base_y, label, (255, 220, 110), 0.9, 20))
                            else:
                                self.damage_texts.append(FloatingText(base, base_y, label, (255, 210, 120), 0.8, 18))
                elif self.state == "upgrade":
                    for idx, rect in enumerate(self.pending_boxes):
                        if rect.collidepoint(pos):
                            self.apply_upgrade(self.pending_choices[idx])
                            self.state = "playing"
                            self.pending_choices = []
                            self.pending_boxes = []
                            self.current_room.upgrade_given = True
                            break
                elif self.state == "shop":
                    if self.shop_leave_button and self.shop_leave_button.collidepoint(pos):
                        self.state = "playing"
                        self.shop_room_id = self.dungeon.current_room_id
                        self.shop_choices = []
                        self.shop_boxes = []
                        self.shop_costs = []
                        self.shop_leave_button = None
                        break
                    for idx, rect in enumerate(self.shop_boxes):
                        if rect.collidepoint(pos):
                            cost = self.shop_costs[idx]
                            if self.player.gold >= cost:
                                self.player.gold -= cost
                                self.apply_upgrade(self.shop_choices[idx])
                                self.audio.play("victory")
                            break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.audio.toggle_music()
                elif event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                        self.audio.pause_music()
                    elif self.state == "paused":
                        self.state = "playing"
                        self.audio.resume_music()
                    elif self.state == "shop":
                        self.state = "playing"
                        self.shop_room_id = self.dungeon.current_room_id
                        self.shop_choices = []
                        self.shop_boxes = []
                        self.shop_costs = []
                        self.shop_leave_button = None
                elif self.state == "menu" and event.key == pygame.K_RETURN:
                    self.start_run()
                elif self.state == "settings" and event.key == pygame.K_1:
                    self.settings["music"] = not self.settings.get("music", True)
                    self.audio.music_muted = not self.settings["music"]
                    if self.settings["music"]:
                        self.audio.resume_music()
                    else:
                        self.audio.pause_music()
                elif self.state == "settings" and event.key == pygame.K_2:
                    self.settings["shadows"] = not self.settings.get("shadows", True)
                elif self.state == "settings" and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    self.state = "menu"
                elif self.state == "playing" and event.key == pygame.K_s:
                    self.save_game()
                elif self.state in ("game_over", "victory") and event.key == pygame.K_RETURN:
                    self.start_run()
                elif self.state == "paused" and event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self.audio.resume_music()
                elif self.state in ("playing", "shop") and event.key == pygame.K_e:
                    direction, _ = self.get_door_prompt()
                    if direction is not None:
                        self.transition_to(direction)
                        if self.state == "shop":
                            self.state = "playing"
                elif self.state == "playing" and event.key == pygame.K_q:
                    if self.player.deflect(self.projectiles):
                        self.audio.play("victory")
                elif self.state == "playing" and event.key == pygame.K_r:
                    self.start_run()
                elif self.state == "playing" and event.key == pygame.K_h:
                    if self.player.heal_potions > 0:
                        self.player.heal_potions -= 1
                        self.player.health = min(self.player.max_health, self.player.health + 38 + self.current_floor * 5)
                        self.audio.play("victory")
                elif self.state == "playing" and event.key == pygame.K_f:
                    if self.player.dash():
                        self.player.x += math.cos(self.player.angle) * 45
                        self.player.y += math.sin(self.player.angle) * 45
                        self.audio.play("dodge")
                elif self.state == "upgrade" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx = event.key - pygame.K_1
                    if idx < len(self.pending_choices):
                        self.apply_upgrade(self.pending_choices[idx])
                        self.state = "playing"
                        self.pending_choices = []
                        self.pending_boxes = []
                        self.current_room.upgrade_given = True
                elif self.state == "shop" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx = event.key - pygame.K_1
                    if idx < len(self.shop_choices):
                        cost = self.shop_costs[idx]
                        if self.player.gold >= cost:
                            self.player.gold -= cost
                            self.apply_upgrade(self.shop_choices[idx])
                            self.audio.play("victory")
                elif self.state == "shop" and event.key == pygame.K_q:
                    self.state = "playing"
                    self.shop_room_id = self.dungeon.current_room_id
                    self.shop_choices = []
                    self.shop_boxes = []
                    self.shop_costs = []
                    self.shop_leave_button = None

        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_SPACE] and self.state == "playing":
            if self.player.dodge():
                self.audio.play("dodge")
        return True

    def update(self, dt):
        if self.state not in ("playing", "shop"):
            return

        self.maybe_unlock_weapons()
        room = self.current_room
        if self.keys is None:
            self.keys = pygame.key.get_pressed()
        self.player.update(dt, self.keys, room, pygame.mouse.get_pos())

        if self.transition_lock > 0:
            self.transition_lock -= dt

        self.near_door, self.door_pos = self.get_door_prompt()

        if self.player.dash_time > 0:
            self.player.dash_time -= dt

        if self.boss_intro_timer > 0:
            self.boss_intro_timer = max(0.0, self.boss_intro_timer - dt)
        if self.phase_message_timer > 0:
            self.phase_message_timer = max(0.0, self.phase_message_timer - dt)

        if self.current_room.kind == "shop" and self.state == "playing" and self.shop_room_id != self.dungeon.current_room_id:
            self.state = "shop"
            self.shop_choices = self.random_upgrades()
            self.shop_costs = [30, 40, 50]
            self.shop_boxes = []
            self.shop_leave_button = pygame.Rect(500, 520, 280, 56)
            self.shop_room_id = self.dungeon.current_room_id

        if self.current_room.kind != "shop" and self.current_room.kind != "boss" and len(self.current_room.enemies) == 0 and not self.current_room.upgrade_given and not self.current_room.cleared:
            self.current_room.cleared = True
            self.pending_choices = self.random_upgrades()
            self.pending_boxes = []
            self.state = "upgrade"
            self.audio.play("victory")

        for enemy in list(self.current_room.enemies):
            if not enemy.alive:
                self.spawn_enemy_drop(enemy)
                self.player.gold += 8 + (20 if enemy.kind == "boss" else 0)
                self.current_room.enemies.remove(enemy)
                self.audio.play("hit")
                if enemy.kind == "boss":
                    self.audio.play("boss_roar")
                continue
            enemy.update(dt, self.player, self.current_room, self.projectiles)

        for projectile in list(self.projectiles):
            projectile.update(dt)
            if projectile.life <= 0:
                self.projectiles.remove(projectile)
                continue
            if projectile.owner == "player":
                for enemy in self.current_room.enemies:
                    if not enemy.alive:
                        continue
                    if math.hypot(projectile.x - enemy.x, projectile.y - enemy.y) < enemy.radius + projectile.radius:
                        damage = enemy.take_damage(projectile.damage)
                        self.damage_texts.append(FloatingText(enemy.x, enemy.y - 18, f"{int(damage)}", (255, 210, 120), 0.8, 18))
                        self.audio.play("hit")
                        self.projectiles.remove(projectile)
                        break
            else:
                if math.hypot(projectile.x - self.player.x, projectile.y - self.player.y) < self.player.radius + projectile.radius:
                    damage = self.player.take_damage(projectile.damage)
                    self.damage_texts.append(FloatingText(self.player.x, self.player.y - 18, f"-{int(damage)}", (255, 120, 120), 0.8, 18))
                    self.audio.play("hurt")
                    self.projectiles.remove(projectile)

        for text in list(self.damage_texts):
            text.update(dt)
            if text.life <= 0:
                self.damage_texts.remove(text)

        for drop in list(self.drops):
            drop.update(dt)
            if drop.life <= 0:
                self.drops.remove(drop)
                continue
            if math.hypot(drop.x - self.player.x, drop.y - self.player.y) < self.player.radius + drop.radius + 10:
                if drop.kind == "gold":
                    self.player.gold += 6
                elif drop.kind == "essence":
                    self.player.damage += 1
                    self.player.health = min(self.player.max_health, self.player.health + 6)
                elif drop.kind == "vital":
                    self.player.health = min(self.player.max_health, self.player.health + 24)
                    self.player.damage += 2
                elif drop.kind == "heal":
                    self.player.health = min(self.player.max_health, self.player.health + 18)
                self.drops.remove(drop)

        if self.current_room and self.current_room.healing_well is not None:
            well = self.current_room.healing_well
            if math.hypot(well.x - self.player.x, well.y - self.player.y) < well.radius + self.player.radius + 8:
                if well.cooldown <= 0:
                    self.player.health = min(self.player.max_health, self.player.health + 8)
                    well.cooldown = 3.0
                    well.pulse = 0.5

        if self.player.health <= 0:
            self.state = "game_over"
            self.audio.play("death")

        if self.current_room.kind == "boss" and len(self.current_room.enemies) == 0 and not self.current_room.upgrade_given:
            self.current_room.upgrade_given = True
            if self.current_floor >= self.max_floor:
                self.state = "victory"
            else:
                self.advance_floor()
            self.audio.play("victory")

        if self.current_room.kind == "boss" and len(self.current_room.enemies) > 0:
            for enemy in self.current_room.enemies:
                if enemy.kind == "boss" and enemy.health < enemy.max_health * 0.5 and not getattr(enemy, "roared", False):
                    enemy.roared = True
                    self.phase_message_timer = 1.8
                    self.audio.play("boss_roar")
                if enemy.kind == "boss" and enemy.health < enemy.max_health * 0.5 and enemy.attack_cooldown <= 0:
                    enemy.attack_cooldown = 0.7
                    for i in range(10):
                        angle = (2 * math.pi * i / 10) + (self.current_floor * 0.7)
                        self.projectiles.append(Projectile(enemy.x, enemy.y, math.cos(angle) * 380, math.sin(angle) * 380, 8, 12, (255, 160, 110), "enemy"))

    def draw(self):
        self.screen.fill((20, 23, 30))

        if self.state == "menu":
            self.screen.fill((11, 15, 22))
            panel = pygame.Rect(150, 90, WIDTH - 300, HEIGHT - 180)
            pygame.draw.rect(self.screen, (20, 27, 36), panel)
            pygame.draw.rect(self.screen, (205, 160, 110), panel, 3)

            title = self.big_font.render("Dungeon Warden", True, (245, 214, 176))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 165)))

            self.menu_buttons = []
            actions = [
                ("Start Run", "start", pygame.Rect(470, 240, 340, 54)),
                ("Load Save", "load", pygame.Rect(470, 312, 340, 54)),
                ("Settings", "settings", pygame.Rect(470, 384, 340, 54)),
            ]
            for label, action, rect in actions:
                self.menu_buttons.append({"label": label, "action": action, "rect": rect})
                color = (72, 86, 100) if action != "start" else (92, 120, 110)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (220, 220, 220), rect, 2)
                text = self.font.render(label, True, (255, 255, 255))
                self.screen.blit(text, text.get_rect(center=rect.center))

            hint = self.font.render("Use the mouse or press Enter to start", True, (201, 211, 224))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH / 2, 470)))
            controls = [
                "WASD = move",
                "Shift = sprint",
                "Space = dodge",
                "Left click = attack",
                "F = dash",
                "Q = deflect",
                "H = potion",
                "R = reset run",
                "E = enter door",
                "Esc = pause",
            ]
            start_y = 520
            for i, line in enumerate(controls):
                label = self.font.render(line, True, (220, 220, 220))
                self.screen.blit(label, label.get_rect(center=(WIDTH / 2, start_y + i * 20)))

            footer = self.font.render("Clear each floor, survive the boss, and buy upgrades in the shop.", True, (170, 200, 180))
            self.screen.blit(footer, footer.get_rect(center=(WIDTH / 2, 660)))
            pygame.display.flip()
            return

        if self.state == "settings":
            self.screen.fill((11, 15, 22))
            panel = pygame.Rect(250, 150, 780, 420)
            pygame.draw.rect(self.screen, (22, 31, 40), panel)
            pygame.draw.rect(self.screen, (200, 180, 130), panel, 3)
            title = self.big_font.render("Settings", True, (245, 214, 176))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 210)))
            music_text = self.font.render(f"1. Music: {'On' if self.settings.get('music', True) else 'Off'}", True, (255, 255, 255))
            shadows_text = self.font.render(f"2. Shadows: {'On' if self.settings.get('shadows', True) else 'Off'}", True, (255, 255, 255))
            self.screen.blit(music_text, music_text.get_rect(center=(WIDTH / 2, 300)))
            self.screen.blit(shadows_text, shadows_text.get_rect(center=(WIDTH / 2, 340)))
            footer = self.font.render("Press 1 or 2 to toggle, Enter or Esc to return", True, (200, 210, 220))
            self.screen.blit(footer, footer.get_rect(center=(WIDTH / 2, 430)))
            pygame.display.flip()
            return

        room = self.current_room
        if room is None:
            pygame.display.flip()
            return

        tile_themes = {
            "stone": ((34, 40, 49), (56, 48, 42)),
            "crypt": ((30, 30, 40), (46, 38, 54)),
            "forge": ((62, 46, 36), (46, 30, 26)),
            "swamp": ((38, 52, 46), (30, 42, 36)),
        }
        a, b = tile_themes.get(room.theme, tile_themes["stone"])
        for tile_x in range(room.left, room.right, 32):
            for tile_y in range(room.top, room.bottom, 32):
                color = a if ((tile_x // 32) + (tile_y // 32)) % 2 == 0 else b
                pygame.draw.rect(self.screen, color, (tile_x, tile_y, 32, 32))

        pygame.draw.rect(self.screen, (35, 40, 48), (room.x, room.y, room.w, room.h), 3)
        for edge_x in range(room.left, room.right, 64):
            pygame.draw.rect(self.screen, (72, 80, 92), (edge_x, room.top, 8, room.h))
            pygame.draw.rect(self.screen, (72, 80, 92), (edge_x, room.bottom - 8, 8, 8))
        for edge_y in range(room.top, room.bottom, 64):
            pygame.draw.rect(self.screen, (72, 80, 92), (room.left, edge_y, room.w, 8))
            pygame.draw.rect(self.screen, (72, 80, 92), (room.right - 8, edge_y, 8, 8))

        if room.doors["left"]:
            pygame.draw.rect(self.screen, (110, 155, 125), (room.left, room.center_y() - 45, 18, 90))
            pygame.draw.rect(self.screen, (160, 210, 170), (room.left + 4, room.center_y() - 36, 10, 72), 2)
        else:
            pygame.draw.rect(self.screen, (85, 95, 110), (room.left, room.top + 60, 18, room.h - 120))
        if room.doors["right"]:
            pygame.draw.rect(self.screen, (110, 155, 125), (room.right - 18, room.center_y() - 45, 18, 90))
            pygame.draw.rect(self.screen, (160, 210, 170), (room.right - 14, room.center_y() - 36, 10, 72), 2)
        else:
            pygame.draw.rect(self.screen, (85, 95, 110), (room.right - 18, room.top + 60, 18, room.h - 120))
        if room.doors["up"]:
            pygame.draw.rect(self.screen, (110, 155, 125), (room.center_x() - 45, room.top, 90, 18))
            pygame.draw.rect(self.screen, (160, 210, 170), (room.center_x() - 36, room.top + 4, 72, 10), 2)
        else:
            pygame.draw.rect(self.screen, (85, 95, 110), (room.left + 60, room.top, room.w - 120, 18))
        if room.doors["down"]:
            pygame.draw.rect(self.screen, (110, 155, 125), (room.center_x() - 45, room.bottom - 18, 90, 18))
            pygame.draw.rect(self.screen, (160, 210, 170), (room.center_x() - 36, room.bottom - 14, 72, 10), 2)
        else:
            pygame.draw.rect(self.screen, (85, 95, 110), (room.left + 60, room.bottom - 18, room.w - 120, 18))

        for enemy in room.enemies:
            enemy.draw(self.screen)
        for projectile in self.projectiles:
            pygame.draw.circle(self.screen, projectile.color, (int(projectile.x), int(projectile.y)), projectile.radius)
        for drop in self.drops:
            drop.draw(self.screen)
        if self.current_room and self.current_room.healing_well is not None:
            self.current_room.healing_well.draw(self.screen)
        self.player.draw(self.screen)
        for text in self.damage_texts:
            text.draw(self.screen, self.font)

        hp_bar = pygame.Rect(30, 20, 260, 24)
        hp_ratio = self.player.health / self.player.max_health
        pygame.draw.rect(self.screen, (60, 60, 60), hp_bar)
        pygame.draw.rect(self.screen, (230, 80, 80), (hp_bar.x, hp_bar.y, int(hp_bar.width * hp_ratio), hp_bar.height))
        self.screen.blit(self.font.render(f"HP {int(self.player.health)}/{self.player.max_health}", True, (255, 255, 255)), (36, 48))
        self.screen.blit(self.font.render(f"Weapon: {self.player.weapon_name.title()}", True, (255, 255, 255)), (320, 22))
        self.screen.blit(self.font.render(f"Gold: {self.player.gold}", True, (255, 220, 110)), (320, 48))
        self.screen.blit(self.font.render(f"Armor: {self.player.armor}", True, (180, 210, 255)), (520, 22))
        self.screen.blit(self.font.render(f"Potions: {self.player.heal_potions}", True, (160, 250, 180)), (520, 48))
        self.screen.blit(self.font.render(f"Floor: {self.current_floor}/{self.max_floor}", True, (180, 220, 255)), (760, 22))
        self.screen.blit(self.font.render(f"Room: {self.dungeon.room_name()}", True, (210, 220, 255)), (760, 48))
        self.screen.blit(self.font.render(f"Damage: {self.player.damage}", True, (255, 255, 255)), (1010, 22))
        self.screen.blit(self.font.render("S = save", True, (170, 230, 180)), (1010, 78))

        stamina_bar = pygame.Rect(30, 58, 260, 12)
        stamina_ratio = self.player.stamina / self.player.max_stamina
        pygame.draw.rect(self.screen, (60, 60, 60), stamina_bar)
        pygame.draw.rect(self.screen, (90, 170, 255), (stamina_bar.x, stamina_bar.y, int(stamina_bar.width * stamina_ratio), stamina_bar.height))
        self.screen.blit(self.font.render("Sprint", True, (255, 255, 255)), (36, 74))

        dodge_bar = pygame.Rect(1010, 46, 210, 18)
        dodge_fill = 1.0 if self.player.dodge_cooldown <= 0 else max(0.0, 1.0 - (self.player.dodge_cooldown / 1.2))
        pygame.draw.rect(self.screen, (55, 55, 55), dodge_bar)
        pygame.draw.rect(self.screen, (120, 170, 255), (dodge_bar.x, dodge_bar.y, int(dodge_bar.width * dodge_fill), dodge_bar.height))
        self.screen.blit(self.font.render("Dodge", True, (255, 255, 255)), (1010, 42))

        if self.state in ("playing", "shop") and self.near_door is not None and self.door_pos is not None:
            prompt = self.font.render("Press E", True, (255, 255, 255))
            px = int(self.door_pos[0])
            py = int(self.door_pos[1]) - 34
            self.screen.blit(prompt, prompt.get_rect(center=(px, py)))

        if self.current_room and self.current_room.kind == "boss" and self.boss_intro_timer > 0:
            alpha = min(1.0, self.boss_intro_timer / 2.8)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int((1.0 - alpha) * 180)))
            self.screen.blit(overlay, (0, 0))
            title = self.big_font.render("BOSS", True, (255, 120, 110))
            sub = self.font.render("The Warden Awakens", True, (255, 220, 180))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 28)))
            self.screen.blit(sub, sub.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20)))

        if self.phase_message_timer > 0 and self.current_room and self.current_room.kind == "boss":
            phase_text = self.big_font.render("PHASE SHIFT", True, (255, 188, 92))
            self.screen.blit(phase_text, phase_text.get_rect(center=(WIDTH / 2, 110)))

        if self.state == "upgrade":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))
            title = self.font.render("Choose an upgrade", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 120)))
            self.pending_boxes = []
            rarity_colors = {"common": (46, 62, 76), "uncommon": (46, 76, 60), "rare": (72, 52, 90), "epic": (96, 64, 140), "legendary": (140, 100, 40)}
            for i, choice in enumerate(self.pending_choices):
                rect = pygame.Rect(170 + i * 300, 200, 240, 190)
                self.pending_boxes.append(rect)
                tint = rarity_colors.get(choice.get("rarity", "common"), (55, 55, 80))
                pygame.draw.rect(self.screen, tint, rect)
                pygame.draw.rect(self.screen, (220, 220, 220), rect, 2)
                rarity_label = self.font.render(choice.get("rarity", "common").title(), True, (255, 255, 255))
                self.screen.blit(rarity_label, rarity_label.get_rect(center=(rect.centerx, rect.y + 25)))
                name_label = self.font.render(choice.get("display_name", choice["name"]), True, (255, 255, 255))
                self.screen.blit(name_label, name_label.get_rect(center=(rect.centerx, rect.y + 80)))
        elif self.state == "shop":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            panel = pygame.Rect(120, 90, WIDTH - 240, HEIGHT - 180)
            pygame.draw.rect(self.screen, (28, 34, 46), panel)
            pygame.draw.rect(self.screen, (190, 180, 120), panel, 3)
            title = self.big_font.render("Mystic Shop", True, (240, 220, 170))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 140)))
            subtitle = self.font.render("Buy a boon or leave before the next room", True, (220, 220, 220))
            self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH / 2, 176)))
            self.shop_boxes = []
            rarity_colors = {"common": (46, 62, 76), "uncommon": (46, 76, 60), "rare": (72, 52, 90)}
            for i, choice in enumerate(self.shop_choices):
                rect = pygame.Rect(170 + i * 300, 220, 240, 190)
                self.shop_boxes.append(rect)
                tint = rarity_colors.get(choice.get("rarity", "common"), (55, 55, 80))
                pygame.draw.rect(self.screen, tint, rect)
                pygame.draw.rect(self.screen, (220, 220, 220), rect, 2)
                rarity_label = self.font.render(choice.get("rarity", "common").title(), True, (255, 255, 255))
                self.screen.blit(rarity_label, rarity_label.get_rect(center=(rect.centerx, rect.y + 25)))
                name_label = self.font.render(choice["name"], True, (255, 255, 255))
                self.screen.blit(name_label, name_label.get_rect(center=(rect.centerx, rect.y + 75)))
                cost_label = self.font.render(f"Cost: {self.shop_costs[i]}", True, (255, 220, 110))
                self.screen.blit(cost_label, cost_label.get_rect(center=(rect.centerx, rect.y + 120)))
            self.shop_leave_button = pygame.Rect(500, 520, 280, 56)
            pygame.draw.rect(self.screen, (120, 82, 69), self.shop_leave_button)
            pygame.draw.rect(self.screen, (240, 220, 190), self.shop_leave_button, 2)
            leave_text = self.font.render("Leave Shop (Q)", True, (255, 255, 255))
            self.screen.blit(leave_text, leave_text.get_rect(center=self.shop_leave_button.center))
        elif self.state == "paused":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            title = self.big_font.render("Paused", True, (180, 220, 255))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 220)))
            label = self.font.render("Esc or Enter to resume | M toggles music", True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=(WIDTH / 2, 300)))
        elif self.state == "game_over":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            title = self.big_font.render("Game Over", True, (255, 110, 110))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 220)))
            label = self.font.render("Press Enter to restart", True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=(WIDTH / 2, 300)))
        elif self.state == "victory":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            title = self.big_font.render("Victory!", True, (180, 220, 140))
            self.screen.blit(title, title.get_rect(center=(WIDTH / 2, 220)))
            label = self.font.render("Press Enter to run again", True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(center=(WIDTH / 2, 300)))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            if self.state in ("playing", "paused"):
                self.audio.play_theme("game")
            else:
                self.audio.play_theme("menu")
            running = self.handle_events()
            if self.state == "playing":
                self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
