import pygame


def draw_hud(screen, player, dungeon, font):
    health_ratio = max(0.0, player.health / player.max_health)
    pygame.draw.rect(screen, (40, 40, 40), (30, 26, 260, 24))
    pygame.draw.rect(screen, (220, 40, 40), (30, 26, int(260 * health_ratio), 24))
    hp_label = font.render(f"HP: {int(player.health)} / {player.max_health}", True, (255, 255, 255))
    screen.blit(hp_label, (30, 52))

    weapon_text = font.render(f"Weapon: {player.weapon_name.title()}", True, (255, 255, 255))
    screen.blit(weapon_text, (310, 26))

    gold_text = font.render(f"Gold: {player.gold}", True, (255, 220, 110))
    screen.blit(gold_text, (310, 52))

    room_text = font.render(f"Room: {dungeon.room_name()}", True, (220, 220, 255))
    screen.blit(room_text, (760, 26))

    dodge_pct = 1.0 if player.dodge_cooldown <= 0 else max(0.0, 1.0 - (player.dodge_cooldown / player.dodge_cooldown_base))
    dodge_bar = pygame.Rect(1010, 28, 200, 16)
    pygame.draw.rect(screen, (50, 50, 50), dodge_bar)
    pygame.draw.rect(screen, (130, 220, 250), (dodge_bar.x, dodge_bar.y, int(dodge_bar.width * dodge_pct), dodge_bar.height))
    dodge_label = font.render("Dodge", True, (255, 255, 255))
    screen.blit(dodge_label, (1010, 46))

    dmg_text = font.render(f"Damage: {int(player.damage)}", True, (255, 255, 255))
    screen.blit(dmg_text, (760, 52))


def draw_room(screen, room):
    pygame.draw.rect(screen, (25, 28, 30), room.bounds)
    pygame.draw.rect(screen, (90, 105, 120), room.bounds, 2)
    wall_color = (90, 90, 120)

    # Draw walls and doors.
    if room.doors.get("left"):
        pygame.draw.rect(screen, (120, 160, 110), (room.bounds.left, room.bounds.centery - 50, 16, 100))
    else:
        pygame.draw.rect(screen, wall_color, (room.bounds.left, room.bounds.top + 50, 16, room.bounds.height - 100))

    if room.doors.get("right"):
        pygame.draw.rect(screen, (120, 160, 110), (room.bounds.right - 16, room.bounds.centery - 50, 16, 100))
    else:
        pygame.draw.rect(screen, wall_color, (room.bounds.right - 16, room.bounds.top + 50, 16, room.bounds.height - 100))

    if room.doors.get("up"):
        pygame.draw.rect(screen, (120, 160, 110), (room.bounds.centerx - 50, room.bounds.top, 100, 16))
    else:
        pygame.draw.rect(screen, wall_color, (room.bounds.left + 50, room.bounds.top, room.bounds.width - 100, 16))

    if room.doors.get("down"):
        pygame.draw.rect(screen, (120, 160, 110), (room.bounds.centerx - 50, room.bounds.bottom - 16, 100, 16))
    else:
        pygame.draw.rect(screen, wall_color, (room.bounds.left + 50, room.bounds.bottom - 16, room.bounds.width - 100, 16))


def draw_button(screen, rect, text, font, color, text_color=(255, 255, 255)):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    label = font.render(text, True, text_color)
    screen.blit(label, (rect.x + 15, rect.y + rect.height / 2 - 12))


def draw_menu(screen, font, large_font):
    screen.fill((18, 18, 20))
    title = large_font.render("Dungeon Warden", True, (230, 210, 170))
    screen.blit(title, (420, 120))
    subtitle = font.render("Press Enter to begin your run", True, (220, 220, 220))
    screen.blit(subtitle, (470, 240))
    small = font.render("WASD move, Mouse aim, Left click attack, Space dodge", True, (180, 180, 190))
    screen.blit(small, (350, 300))


def draw_game_over(screen, font):
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    title = font.render("Game Over", True, (255, 110, 110))
    screen.blit(title, (520, 250))
    hint = font.render("Press Enter to restart", True, (255, 255, 255))
    screen.blit(hint, (470, 330))


def draw_victory(screen, font):
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    title = font.render("Victory!", True, (200, 240, 140))
    screen.blit(title, (530, 250))
    hint = font.render("Press Enter to run again", True, (255, 255, 255))
    screen.blit(hint, (470, 330))


def draw_upgrade_selection(screen, choices, font):
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    title = font.render("Choose an upgrade", True, (255, 255, 255))
    screen.blit(title, (470, 120))

    boxes = []
    for i, choice in enumerate(choices):
        rect = pygame.Rect(170 + i * 300, 220, 250, 180)
        boxes.append(rect)
        pygame.draw.rect(screen, (58, 58, 70), rect)
        pygame.draw.rect(screen, (200, 200, 220), rect, 2)
        label = font.render(f"{i + 1}. {choice['name']}", True, (255, 255, 255))
        screen.blit(label, (rect.x + 15, rect.y + 20))
    return boxes


def draw_shop_selection(screen, choices, player, font):
    overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    title = font.render("Shop - Spend Gold", True, (255, 255, 255))
    screen.blit(title, (480, 120))
    gold = font.render(f"Gold: {player.gold}", True, (255, 220, 110))
    screen.blit(gold, (550, 155))

    boxes = []
    for i, choice in enumerate(choices):
        cost = 25 + i * 15
        rect = pygame.Rect(170 + i * 300, 220, 250, 180)
        boxes.append(rect)
        pygame.draw.rect(screen, (58, 58, 90), rect)
        pygame.draw.rect(screen, (200, 200, 220), rect, 2)
        label = font.render(f"{i + 1}. {choice['name']}", True, (255, 255, 255))
        screen.blit(label, (rect.x + 15, rect.y + 20))
        cost_label = font.render(f"Cost: {cost} gold", True, (255, 220, 110))
        screen.blit(cost_label, (rect.x + 15, rect.y + 90))
    return boxes
