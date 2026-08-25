import random
from collections import defaultdict


class Room:
    def __init__(self, room_id, room_type, bounds):
        self.id = room_id
        self.type = room_type
        self.bounds = bounds
        self.enemies = []
        self.neighbors = {}
        self.cleared = False
        self.doors = {"left": False, "right": False, "up": False, "down": False}
        self.open = True
        self.spawned = False

    def add_enemy(self, enemy):
        self.enemies.append(enemy)


class Dungeon:
    def __init__(self):
        self.rooms = {}
        self.current_room_id = 0
        self.room_positions = {}

    def generate(self, room_count=9):
        self.rooms = {}
        self.room_positions = {0: (0, 0)}
        self.rooms[0] = Room(0, "start", __import__('pygame').Rect(80, 80, 1120, 560))
        for room_id in range(1, room_count):
            placed = False
            attempts = 0
            while not placed and attempts < 200:
                attempts += 1
                parent = random.choice(list(self.room_positions.keys()))
                parent_x, parent_y = self.room_positions[parent]
                dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                nx, ny = parent_x + dx, parent_y + dy
                if any(pos == (nx, ny) for pos in self.room_positions.values()):
                    continue
                self.room_positions[room_id] = (nx, ny)
                self.rooms[room_id] = Room(room_id, "normal", __import__('pygame').Rect(80, 80, 1120, 560))
                placed = True
            if not placed:
                break

        if not self.rooms:
            self.rooms[0] = Room(0, "start", __import__('pygame').Rect(80, 80, 1120, 560))

        boss_room_id = max(self.rooms.keys(), key=lambda rid: sum(abs(x) + abs(y) for x, y in [self.room_positions[rid]]))
        self.rooms[boss_room_id].type = "boss"

        # Ensure there is a shop room.
        normal_ids = [rid for rid in self.rooms if self.rooms[rid].type == "normal"]
        if normal_ids:
            shop_id = random.choice(normal_ids)
            self.rooms[shop_id].type = "shop"

        # Connection map.
        for rid, pos in self.room_positions.items():
            for other_id, other_pos in self.room_positions.items():
                if rid == other_id:
                    continue
                if abs(pos[0] - other_pos[0]) + abs(pos[1] - other_pos[1]) == 1:
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

        for rid, room in self.rooms.items():
            room.open = room.type != "boss"

    def current_room(self):
        return self.rooms[self.current_room_id]

    def transition(self, direction, player):
        room = self.rooms[self.current_room_id]
        if direction not in room.neighbors:
            return
        next_id = room.neighbors[direction]
        self.current_room_id = next_id
        next_room = self.rooms[next_id]
        if direction == "left":
            player.x = next_room.bounds.right - 70
            player.y = next_room.bounds.centery
        elif direction == "right":
            player.x = next_room.bounds.left + 70
            player.y = next_room.bounds.centery
        elif direction == "up":
            player.x = next_room.bounds.centerx
            player.y = next_room.bounds.bottom - 70
        elif direction == "down":
            player.x = next_room.bounds.centerx
            player.y = next_room.bounds.top + 70
        return next_room

    def room_name(self):
        room = self.rooms[self.current_room_id]
        names = {
            "start": "Starting Chamber",
            "normal": "Dungeon Room",
            "shop": "Shop Room",
            "boss": "Boss Room",
        }
        return names.get(room.type, "Dungeon")
