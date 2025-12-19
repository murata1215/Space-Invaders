import sys
import random

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (10, 10, 20)
PLAYER_COLOR = (80, 200, 120)
ENEMY_COLOR = (200, 80, 80)
BULLET_COLOR = (240, 240, 120)

PLAYER_SIZE = (60, 20)
PLAYER_SPEED = 6

BULLET_SIZE = (6, 12)
BULLET_SPEED = 10

ENEMY_SIZE = (40, 20)
ENEMY_COLUMNS = 8
ENEMY_ROWS = 3
ENEMY_GAP_X = 20
ENEMY_GAP_Y = 15
ENEMY_TOP_MARGIN = 60
ENEMY_SPEED = 120
ENEMY_DROP = 20
ENEMY_BULLET_SIZE = (6, 12)
ENEMY_BULLET_SPEED = 6
ENEMY_BULLET_MAX = 3
ENEMY_FIRE_MIN_INTERVAL = 0.6
ENEMY_FIRE_MAX_INTERVAL = 1.4

UFO_COLOR = (220, 140, 240)
UFO_SIZE = (60, 20)
UFO_SPEED = 140
UFO_MIN_INTERVAL = 10.0
UFO_MAX_INTERVAL = 15.0
UFO_Y = 40
UFO_BONUS = 100


def build_enemy_rects():
    enemy_rects = []
    total_width = ENEMY_COLUMNS * ENEMY_SIZE[0] + (ENEMY_COLUMNS - 1) * ENEMY_GAP_X
    start_x = (SCREEN_WIDTH - total_width) // 2

    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLUMNS):
            x = start_x + col * (ENEMY_SIZE[0] + ENEMY_GAP_X)
            y = ENEMY_TOP_MARGIN + row * (ENEMY_SIZE[1] + ENEMY_GAP_Y)
            enemy_rects.append(pygame.Rect(x, y, *ENEMY_SIZE))
    return enemy_rects


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invaders - Step 1")
    clock = pygame.time.Clock()

    player_rect = pygame.Rect(
        (SCREEN_WIDTH - PLAYER_SIZE[0]) // 2,
        SCREEN_HEIGHT - PLAYER_SIZE[1] - 40,
        *PLAYER_SIZE,
    )
    enemy_rects = build_enemy_rects()
    enemy_direction = 1
    bullet_rect = None
    enemy_bullets = []
    enemy_fire_timer = 0.0
    next_enemy_fire = random.uniform(ENEMY_FIRE_MIN_INTERVAL, ENEMY_FIRE_MAX_INTERVAL)
    score = 0
    ufo_rect = None
    ufo_timer = 0.0
    next_ufo_spawn = random.uniform(UFO_MIN_INTERVAL, UFO_MAX_INTERVAL)
    ufo_direction = 1

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if bullet_rect is None:
                    bullet_rect = pygame.Rect(
                        player_rect.centerx - BULLET_SIZE[0] // 2,
                        player_rect.top - BULLET_SIZE[1],
                        *BULLET_SIZE,
                    )

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player_rect.x += PLAYER_SPEED

        player_rect.x = max(0, min(player_rect.x, SCREEN_WIDTH - player_rect.width))

        if bullet_rect is not None:
            bullet_rect.y -= BULLET_SPEED
            if bullet_rect.bottom < 0:
                bullet_rect = None

        if enemy_rects:
            leftmost = min(rect.left for rect in enemy_rects)
            rightmost = max(rect.right for rect in enemy_rects)
            if leftmost <= 0 or rightmost >= SCREEN_WIDTH:
                enemy_direction *= -1
                for rect in enemy_rects:
                    rect.y += ENEMY_DROP
            for rect in enemy_rects:
                rect.x += ENEMY_SPEED * enemy_direction * dt

        if bullet_rect is not None:
            hit_index = bullet_rect.collidelist(enemy_rects)
            if hit_index != -1:
                enemy_rects.pop(hit_index)
                bullet_rect = None
        if enemy_rects and len(enemy_bullets) < ENEMY_BULLET_MAX:
            enemy_fire_timer += dt
            if enemy_fire_timer >= next_enemy_fire:
                shooter = random.choice(enemy_rects)
                enemy_bullets.append(
                    pygame.Rect(
                        shooter.centerx - ENEMY_BULLET_SIZE[0] // 2,
                        shooter.bottom,
                        *ENEMY_BULLET_SIZE,
                    )
                )
                enemy_fire_timer = 0.0
                next_enemy_fire = random.uniform(
                    ENEMY_FIRE_MIN_INTERVAL, ENEMY_FIRE_MAX_INTERVAL
                )

        if enemy_bullets:
            for bullet in enemy_bullets[:]:
                bullet.y += ENEMY_BULLET_SPEED
                if bullet.top > SCREEN_HEIGHT:
                    enemy_bullets.remove(bullet)
                elif bullet.colliderect(player_rect):
                    running = False

        if ufo_rect is None:
            ufo_timer += dt
            if ufo_timer >= next_ufo_spawn:
                ufo_direction = random.choice([-1, 1])
                start_x = -UFO_SIZE[0] if ufo_direction == 1 else SCREEN_WIDTH
                ufo_rect = pygame.Rect(start_x, UFO_Y, *UFO_SIZE)
                ufo_timer = 0.0
                next_ufo_spawn = random.uniform(UFO_MIN_INTERVAL, UFO_MAX_INTERVAL)
        else:
            ufo_rect.x += int(UFO_SPEED * ufo_direction * dt)
            if ufo_rect.right < 0 or ufo_rect.left > SCREEN_WIDTH:
                ufo_rect = None

        if bullet_rect is not None and ufo_rect is not None:
            if bullet_rect.colliderect(ufo_rect):
                score += UFO_BONUS
                bullet_rect = None
                ufo_rect = None

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, PLAYER_COLOR, player_rect)
        for rect in enemy_rects:
            pygame.draw.rect(screen, ENEMY_COLOR, rect)
        if bullet_rect is not None:
            pygame.draw.rect(screen, BULLET_COLOR, bullet_rect)
        if ufo_rect is not None:
            pygame.draw.rect(screen, UFO_COLOR, ufo_rect)
        for bullet in enemy_bullets:
            pygame.draw.rect(screen, BULLET_COLOR, bullet)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
