import sys
import math
import random
from array import array

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
ENEMY_SCORE = 10

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
    mixer_ready = True
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
    except pygame.error:
        mixer_ready = False
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Invaders - Step 1")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 28)

    def draw_centered_text(text, font, y, color=(240, 240, 240)):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(surface, rect)

    def make_sound(frequency, duration, volume, noise=False):
        if not mixer_ready:
            return None
        sample_rate = 44100
        samples = int(duration * sample_rate)
        amplitude = 32767
        buffer = array("h")
        for i in range(samples):
            if noise:
                value = random.randint(-amplitude, amplitude)
            else:
                t = i / sample_rate
                value = int(amplitude * math.sin(2 * math.pi * frequency * t))
            buffer.append(value)
        sound = pygame.mixer.Sound(buffer=buffer.tobytes())
        sound.set_volume(volume)
        return sound

    def play_sound(sound):
        if sound is not None:
            sound.play()

    sounds = {
        "shoot": make_sound(880, 0.08, 0.3),
        "enemy": make_sound(220, 0.1, 0.2, noise=True),
        "ufo": make_sound(660, 0.14, 0.25),
    }

    def reset_game():
        player = pygame.Rect(
            (SCREEN_WIDTH - PLAYER_SIZE[0]) // 2,
            SCREEN_HEIGHT - PLAYER_SIZE[1] - 40,
            *PLAYER_SIZE,
        )
        return {
            "player_rect": player,
            "enemy_rects": build_enemy_rects(),
            "enemy_direction": 1,
            "bullet_rect": None,
            "enemy_bullets": [],
            "enemy_fire_timer": 0.0,
            "next_enemy_fire": random.uniform(
                ENEMY_FIRE_MIN_INTERVAL, ENEMY_FIRE_MAX_INTERVAL
            ),
            "score": 0,
            "ufo_rect": None,
            "ufo_timer": 0.0,
            "next_ufo_spawn": random.uniform(UFO_MIN_INTERVAL, UFO_MAX_INTERVAL),
            "ufo_direction": 1,
        }

    game_state = "START"
    state = reset_game()

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game_state == "START" and event.key == pygame.K_RETURN:
                    game_state = "PLAYING"
                elif game_state == "PLAYING" and event.key == pygame.K_SPACE:
                    if state["bullet_rect"] is None:
                        state["bullet_rect"] = pygame.Rect(
                            state["player_rect"].centerx - BULLET_SIZE[0] // 2,
                            state["player_rect"].top - BULLET_SIZE[1],
                            *BULLET_SIZE,
                        )
                        play_sound(sounds["shoot"])
                elif game_state in {"GAME_OVER", "WIN"} and event.key == pygame.K_r:
                    state = reset_game()
                    game_state = "PLAYING"

        if game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                state["player_rect"].x -= PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                state["player_rect"].x += PLAYER_SPEED

            state["player_rect"].x = max(
                0, min(state["player_rect"].x, SCREEN_WIDTH - state["player_rect"].width)
            )

            if state["bullet_rect"] is not None:
                state["bullet_rect"].y -= BULLET_SPEED
                if state["bullet_rect"].bottom < 0:
                    state["bullet_rect"] = None

            if state["enemy_rects"]:
                leftmost = min(rect.left for rect in state["enemy_rects"])
                rightmost = max(rect.right for rect in state["enemy_rects"])
                dx = ENEMY_SPEED * state["enemy_direction"] * dt
                edge_hit = (
                    (state["enemy_direction"] < 0 and leftmost + dx <= 0)
                    or (state["enemy_direction"] > 0 and rightmost + dx >= SCREEN_WIDTH)
                )
                if edge_hit:
                    state["enemy_direction"] *= -1
                    dx = ENEMY_SPEED * state["enemy_direction"] * dt
                    for rect in state["enemy_rects"]:
                        rect.y += ENEMY_DROP
                for rect in state["enemy_rects"]:
                    rect.x += dx
                    rect.y = max(0, rect.y)
                leftmost = min(rect.left for rect in state["enemy_rects"])
                rightmost = max(rect.right for rect in state["enemy_rects"])
                if leftmost < 0 or rightmost > SCREEN_WIDTH:
                    shift = 0
                    if leftmost < 0:
                        shift = -leftmost
                    elif rightmost > SCREEN_WIDTH:
                        shift = SCREEN_WIDTH - rightmost
                    for rect in state["enemy_rects"]:
                        rect.x += shift

            if state["bullet_rect"] is not None:
                hit_index = state["bullet_rect"].collidelist(state["enemy_rects"])
                if hit_index != -1:
                    state["enemy_rects"].pop(hit_index)
                    state["bullet_rect"] = None
                    state["score"] += ENEMY_SCORE
                    play_sound(sounds["enemy"])
                    if not state["enemy_rects"]:
                        game_state = "WIN"
            if state["enemy_rects"] and len(state["enemy_bullets"]) < ENEMY_BULLET_MAX:
                state["enemy_fire_timer"] += dt
                if state["enemy_fire_timer"] >= state["next_enemy_fire"]:
                    shooter = random.choice(state["enemy_rects"])
                    state["enemy_bullets"].append(
                        pygame.Rect(
                            shooter.centerx - ENEMY_BULLET_SIZE[0] // 2,
                            shooter.bottom,
                            *ENEMY_BULLET_SIZE,
                        )
                    )
                    state["enemy_fire_timer"] = 0.0
                    state["next_enemy_fire"] = random.uniform(
                        ENEMY_FIRE_MIN_INTERVAL, ENEMY_FIRE_MAX_INTERVAL
                    )

            if state["enemy_bullets"]:
                for bullet in state["enemy_bullets"][:]:
                    bullet.y += ENEMY_BULLET_SPEED
                    if bullet.top > SCREEN_HEIGHT:
                        state["enemy_bullets"].remove(bullet)
                    elif bullet.colliderect(state["player_rect"]):
                        game_state = "GAME_OVER"

            if state["ufo_rect"] is None:
                state["ufo_timer"] += dt
                if state["ufo_timer"] >= state["next_ufo_spawn"]:
                    state["ufo_direction"] = random.choice([-1, 1])
                    start_x = (
                        -UFO_SIZE[0] if state["ufo_direction"] == 1 else SCREEN_WIDTH
                    )
                    state["ufo_rect"] = pygame.Rect(start_x, UFO_Y, *UFO_SIZE)
                    state["ufo_timer"] = 0.0
                    state["next_ufo_spawn"] = random.uniform(
                        UFO_MIN_INTERVAL, UFO_MAX_INTERVAL
                    )
            else:
                state["ufo_rect"].x += int(UFO_SPEED * state["ufo_direction"] * dt)
                if (
                    state["ufo_rect"].right < 0
                    or state["ufo_rect"].left > SCREEN_WIDTH
                ):
                    state["ufo_rect"] = None

            if state["bullet_rect"] is not None and state["ufo_rect"] is not None:
                if state["bullet_rect"].colliderect(state["ufo_rect"]):
                    state["score"] += UFO_BONUS
                    state["bullet_rect"] = None
                    state["ufo_rect"] = None
                    play_sound(sounds["ufo"])

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, PLAYER_COLOR, state["player_rect"])
        for rect in state["enemy_rects"]:
            pygame.draw.rect(screen, ENEMY_COLOR, rect)
        if state["bullet_rect"] is not None:
            pygame.draw.rect(screen, BULLET_COLOR, state["bullet_rect"])
        if state["ufo_rect"] is not None:
            pygame.draw.rect(screen, UFO_COLOR, state["ufo_rect"])
        for bullet in state["enemy_bullets"]:
            pygame.draw.rect(screen, BULLET_COLOR, bullet)

        if game_state == "PLAYING":
            score_surface = font_small.render(f"Score: {state['score']}", True, (230, 230, 230))
            screen.blit(score_surface, (12, 10))
        elif game_state == "START":
            draw_centered_text("SPACE INVADERS", font_large, 200)
            draw_centered_text("Press ENTER to Start", font_medium, 280)
            draw_centered_text("Arrows: Move  Space: Shoot  ESC: Quit", font_small, 330)
        elif game_state in {"GAME_OVER", "WIN"}:
            title = "GAME OVER" if game_state == "GAME_OVER" else "YOU WIN"
            draw_centered_text(title, font_large, 220)
            draw_centered_text(f"Score: {state['score']}", font_medium, 290)
            draw_centered_text("Press R to Restart", font_small, 340)
            draw_centered_text("Press ESC to Quit", font_small, 370)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
