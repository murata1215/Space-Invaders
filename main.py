import sys
import math
import random
from array import array

import pygame


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (10, 10, 20)
PLAYER_COLOR = (80, 200, 120)
PLAYER_ACCENT_COLOR = (60, 160, 90)
STAGE_ENEMY_COLORS = {
    1: (220, 60, 60),
    2: (80, 140, 240),
    3: (80, 200, 120),
    4: (160, 100, 60),
    5: (160, 90, 200),
}
STAGE_ENEMY_ACCENT_COLORS = {
    1: (180, 40, 40),
    2: (60, 100, 200),
    3: (60, 160, 90),
    4: (120, 70, 40),
    5: (120, 60, 160),
}
BULLET_COLOR = (255, 220, 80)
BULLET_GLOW_COLOR = (255, 255, 150)
ENEMY_BULLET_COLOR = (255, 100, 100)

PLAYER_SIZE = (60, 30)
PLAYER_SPEED = 6

BULLET_SIZE = (4, 16)
BULLET_SPEED = 10
ENEMY_SCORE = 10

ENEMY_SIZE = (44, 32)
ENEMY_COLUMNS = 8
ENEMY_ROWS = 3
ENEMY_GAP_X = 16
ENEMY_GAP_Y = 12
ENEMY_TOP_MARGIN = 70
ENEMY_SPEED = 120
ENEMY_DROP = 20
ENEMY_BULLET_SIZE = (4, 14)
ENEMY_BULLET_SPEED = 6
ENEMY_BULLET_MAX = 3
ENEMY_FIRE_MIN_INTERVAL = 0.6
ENEMY_FIRE_MAX_INTERVAL = 1.4
STAGE_COUNT = 5
STAGE_SPEED_BOOST = 0.25
STAGE_FIRE_RATE_BOOST = 0.08
STAGE_BANNER_DURATION = 1.0

UFO_COLOR = (220, 140, 240)
UFO_ACCENT_COLOR = (180, 100, 200)
UFO_SIZE = (60, 24)
UFO_SPEED = 140
UFO_MIN_INTERVAL = 10.0
UFO_MAX_INTERVAL = 15.0
UFO_Y = 40
UFO_BONUS = 100

PLAYER_LIVES = 3
RESPAWN_DELAY = 1.5


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


def draw_cannon(surface, rect, color, accent_color):
    """砲台を描画（クラシックなスペースインベーダー風）"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height

    # 砲台のベース部分
    base_rect = pygame.Rect(x, y + h * 0.5, w, h * 0.5)
    pygame.draw.rect(surface, color, base_rect)

    # 砲台の中央部分（少し高い）
    mid_width = w * 0.6
    mid_rect = pygame.Rect(x + (w - mid_width) / 2, y + h * 0.3, mid_width, h * 0.4)
    pygame.draw.rect(surface, color, mid_rect)

    # 砲身（上部の細い部分）
    barrel_width = w * 0.15
    barrel_rect = pygame.Rect(x + (w - barrel_width) / 2, y, barrel_width, h * 0.4)
    pygame.draw.rect(surface, color, barrel_rect)

    # アクセントライン
    pygame.draw.line(surface, accent_color, (x + 4, y + h - 4), (x + w - 4, y + h - 4), 2)


def draw_crab_enemy(surface, rect, color, accent_color, frame):
    """カニ風の敵を描画（アニメーション付き）"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height

    # 胴体（楕円）
    body_rect = pygame.Rect(x + w * 0.15, y + h * 0.25, w * 0.7, h * 0.5)
    pygame.draw.ellipse(surface, color, body_rect)

    # 目（2つの円）
    eye_radius = int(w * 0.1)
    eye_y = int(y + h * 0.35)
    pygame.draw.circle(surface, (255, 255, 255), (int(x + w * 0.35), eye_y), eye_radius)
    pygame.draw.circle(surface, (255, 255, 255), (int(x + w * 0.65), eye_y), eye_radius)
    pygame.draw.circle(surface, (0, 0, 0), (int(x + w * 0.35), eye_y), eye_radius // 2)
    pygame.draw.circle(surface, (0, 0, 0), (int(x + w * 0.65), eye_y), eye_radius // 2)

    # ハサミ（左右）- アニメーションで動く
    claw_offset = 2 if frame % 2 == 0 else -2
    # 左ハサミ
    left_claw = [
        (x + w * 0.1, y + h * 0.4),
        (x - w * 0.05, y + h * 0.3 + claw_offset),
        (x + w * 0.05, y + h * 0.2 + claw_offset),
        (x + w * 0.15, y + h * 0.35),
    ]
    pygame.draw.polygon(surface, color, left_claw)
    # 右ハサミ
    right_claw = [
        (x + w * 0.9, y + h * 0.4),
        (x + w * 1.05, y + h * 0.3 - claw_offset),
        (x + w * 0.95, y + h * 0.2 - claw_offset),
        (x + w * 0.85, y + h * 0.35),
    ]
    pygame.draw.polygon(surface, color, right_claw)

    # 脚（6本）- アニメーションで交互に動く
    leg_y_base = y + h * 0.7
    for i in range(3):
        leg_offset = 3 if (frame + i) % 2 == 0 else -3
        # 左脚
        leg_x_left = x + w * (0.25 + i * 0.15)
        pygame.draw.line(surface, accent_color,
                        (leg_x_left, leg_y_base - 5),
                        (leg_x_left - 5, y + h + leg_offset), 3)
        # 右脚
        leg_x_right = x + w * (0.75 - i * 0.15)
        pygame.draw.line(surface, accent_color,
                        (leg_x_right, leg_y_base - 5),
                        (leg_x_right + 5, y + h - leg_offset), 3)


def draw_ufo(surface, rect, color, accent_color):
    """UFOを描画"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height

    # ドーム部分（上部の半円）
    dome_rect = pygame.Rect(x + w * 0.25, y, w * 0.5, h * 0.6)
    pygame.draw.ellipse(surface, accent_color, dome_rect)

    # 本体（楕円）
    body_rect = pygame.Rect(x, y + h * 0.35, w, h * 0.5)
    pygame.draw.ellipse(surface, color, body_rect)

    # ライト（下部に3つの点滅）
    light_y = int(y + h * 0.7)
    for i, lx in enumerate([0.25, 0.5, 0.75]):
        light_color = (255, 255, 100) if (pygame.time.get_ticks() // 150 + i) % 2 == 0 else (100, 100, 50)
        pygame.draw.circle(surface, light_color, (int(x + w * lx), light_y), 3)


def draw_player_bullet(surface, rect):
    """プレイヤーの弾を描画（光る効果付き）"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    # グロー効果
    glow_rect = pygame.Rect(x - 2, y - 2, w + 4, h + 4)
    pygame.draw.ellipse(surface, BULLET_GLOW_COLOR, glow_rect)
    # 弾本体
    pygame.draw.rect(surface, BULLET_COLOR, rect)


def draw_enemy_bullet(surface, rect):
    """敵の弾を描画（ジグザグ）"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    points = [
        (x + w / 2, y),
        (x + w, y + h * 0.25),
        (x, y + h * 0.5),
        (x + w, y + h * 0.75),
        (x + w / 2, y + h),
    ]
    pygame.draw.lines(surface, ENEMY_BULLET_COLOR, False, points, 3)


def draw_lives(surface, lives, x, y, size=20):
    """残機を砲台アイコンで表示"""
    for i in range(lives):
        mini_rect = pygame.Rect(x + i * (size + 10), y, size, size * 0.6)
        # ミニ砲台を描画
        pygame.draw.rect(surface, PLAYER_COLOR,
                        pygame.Rect(mini_rect.x, mini_rect.y + mini_rect.height * 0.5,
                                   mini_rect.width, mini_rect.height * 0.5))
        pygame.draw.rect(surface, PLAYER_COLOR,
                        pygame.Rect(mini_rect.x + mini_rect.width * 0.35, mini_rect.y,
                                   mini_rect.width * 0.3, mini_rect.height * 0.6))


def main():
    pygame.init()
    mixer_ready = True
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
    except pygame.error:
        mixer_ready = False
    if mixer_ready:
        pygame.mixer.set_num_channels(8)
        pygame.mixer.set_reserved(1)
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
        try:
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
        except pygame.error:
            return None

    def make_tone_sequence(segments, volume):
        if not mixer_ready:
            return None
        sample_rate = 44100
        amplitude = 32767
        buffer = array("h")
        try:
            for frequency, duration in segments:
                samples = int(duration * sample_rate)
                for i in range(samples):
                    t = i / sample_rate
                    value = int(amplitude * math.sin(2 * math.pi * frequency * t))
                    buffer.append(value)
            sound = pygame.mixer.Sound(buffer=buffer.tobytes())
            sound.set_volume(volume)
            return sound
        except pygame.error:
            return None

    def play_sound(sound):
        if sound is not None:
            sound.play()

    sounds = {
        "shoot": make_sound(880, 0.08, 0.3),
        "enemy": make_sound(220, 0.1, 0.2, noise=True),
        "ufo": make_sound(660, 0.14, 0.25),
        "ufo_loop": make_tone_sequence(
            [(780, 0.12), (540, 0.12), (780, 0.12), (540, 0.12)], 0.25
        ),
        "win": make_tone_sequence([(880, 0.12), (1180, 0.12)], 0.3),
        "game_over": make_tone_sequence([(320, 0.14), (220, 0.16)], 0.3),
    }
    ufo_channel = pygame.mixer.Channel(0) if mixer_ready else None
    ufo_loop_playing = False

    def stage_enemy_speed(stage):
        return ENEMY_SPEED * (1 + STAGE_SPEED_BOOST * (stage - 1))

    def stage_fire_interval_range(stage):
        reduction = max(0.0, 1 - STAGE_FIRE_RATE_BOOST * (stage - 1))
        min_interval = max(0.2, ENEMY_FIRE_MIN_INTERVAL * reduction)
        max_interval = max(min_interval + 0.2, ENEMY_FIRE_MAX_INTERVAL * reduction)
        return min_interval, max_interval

    def stage_enemy_color(stage):
        return STAGE_ENEMY_COLORS.get(stage, STAGE_ENEMY_COLORS[1])

    def reset_game():
        player = pygame.Rect(
            (SCREEN_WIDTH - PLAYER_SIZE[0]) // 2,
            SCREEN_HEIGHT - PLAYER_SIZE[1] - 40,
            *PLAYER_SIZE,
        )
        min_fire, max_fire = stage_fire_interval_range(1)
        return {
            "player_rect": player,
            "enemy_rects": build_enemy_rects(),
            "enemy_direction": 1,
            "bullet_rect": None,
            "enemy_bullets": [],
            "enemy_fire_timer": 0.0,
            "next_enemy_fire": random.uniform(min_fire, max_fire),
            "score": 0,
            "stage": 1,
            "stage_banner_timer": 0.0,
            "ufo_rect": None,
            "ufo_timer": 0.0,
            "next_ufo_spawn": random.uniform(UFO_MIN_INTERVAL, UFO_MAX_INTERVAL),
            "ufo_direction": 1,
            "lives": PLAYER_LIVES,
            "respawn_timer": 0.0,
            "player_visible": True,
            "animation_frame": 0,
            "animation_timer": 0.0,
        }

    game_state = "START"
    state = reset_game()

    running = True
    while running:
        previous_game_state = game_state
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
                enemy_speed = stage_enemy_speed(state["stage"])
                dx = enemy_speed * state["enemy_direction"] * dt
                edge_hit = (
                    (state["enemy_direction"] < 0 and leftmost + dx <= 0)
                    or (state["enemy_direction"] > 0 and rightmost + dx >= SCREEN_WIDTH)
                )
                if edge_hit:
                    state["enemy_direction"] *= -1
                    dx = enemy_speed * state["enemy_direction"] * dt
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
                        if state["stage"] >= STAGE_COUNT:
                            game_state = "WIN"
                        else:
                            state["stage"] += 1
                            state["enemy_rects"] = build_enemy_rects()
                            state["enemy_direction"] = 1
                            state["bullet_rect"] = None
                            state["enemy_bullets"] = []
                            state["enemy_fire_timer"] = 0.0
                            min_fire, max_fire = stage_fire_interval_range(state["stage"])
                            state["next_enemy_fire"] = random.uniform(min_fire, max_fire)
                            state["ufo_rect"] = None
                            state["ufo_timer"] = 0.0
                            state["next_ufo_spawn"] = random.uniform(
                                UFO_MIN_INTERVAL, UFO_MAX_INTERVAL
                            )
                            state["stage_banner_timer"] = STAGE_BANNER_DURATION
                            state["player_rect"].centerx = SCREEN_WIDTH // 2
                            if ufo_channel and ufo_loop_playing:
                                ufo_channel.stop()
                                ufo_loop_playing = False
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
                    min_fire, max_fire = stage_fire_interval_range(state["stage"])
                    state["next_enemy_fire"] = random.uniform(min_fire, max_fire)

            if state["enemy_bullets"] and state["player_visible"]:
                for bullet in state["enemy_bullets"][:]:
                    bullet.y += ENEMY_BULLET_SPEED
                    if bullet.top > SCREEN_HEIGHT:
                        state["enemy_bullets"].remove(bullet)
                    elif bullet.colliderect(state["player_rect"]):
                        state["lives"] -= 1
                        state["enemy_bullets"].remove(bullet)
                        if state["lives"] <= 0:
                            game_state = "GAME_OVER"
                        else:
                            state["player_visible"] = False
                            state["respawn_timer"] = RESPAWN_DELAY
                            state["bullet_rect"] = None
                        break

            # リスポーン処理
            if not state["player_visible"]:
                state["respawn_timer"] -= dt
                if state["respawn_timer"] <= 0:
                    state["player_visible"] = True
                    state["player_rect"].centerx = SCREEN_WIDTH // 2
                    state["enemy_bullets"] = []

            # アニメーションフレーム更新
            state["animation_timer"] += dt
            if state["animation_timer"] >= 0.3:
                state["animation_frame"] += 1
                state["animation_timer"] = 0.0

            ufo_was_visible = state["ufo_rect"] is not None
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

            ufo_is_visible = state["ufo_rect"] is not None
            if ufo_is_visible and not ufo_was_visible and sounds["ufo_loop"]:
                if ufo_channel and not ufo_loop_playing:
                    ufo_channel.play(sounds["ufo_loop"], loops=-1)
                    ufo_loop_playing = True
            if (not ufo_is_visible and ufo_was_visible) or game_state != "PLAYING":
                if ufo_channel and ufo_loop_playing:
                    ufo_channel.stop()
                    ufo_loop_playing = False

            if state["stage_banner_timer"] > 0:
                state["stage_banner_timer"] = max(
                    0.0, state["stage_banner_timer"] - dt
                )

        if game_state != "PLAYING" and ufo_loop_playing:
            if ufo_channel:
                ufo_channel.stop()
            ufo_loop_playing = False

        if game_state != previous_game_state:
            if game_state == "WIN":
                play_sound(sounds["win"])
            elif game_state == "GAME_OVER":
                play_sound(sounds["game_over"])

        screen.fill(BACKGROUND_COLOR)

        # プレイヤーの描画（リスポーン中は点滅）
        if state["player_visible"]:
            draw_cannon(screen, state["player_rect"], PLAYER_COLOR, PLAYER_ACCENT_COLOR)
        elif int(state["respawn_timer"] * 6) % 2 == 0:
            draw_cannon(screen, state["player_rect"], (80, 80, 80), (60, 60, 60))

        # 敵の描画
        enemy_color = stage_enemy_color(state["stage"])
        enemy_accent = STAGE_ENEMY_ACCENT_COLORS.get(state["stage"], STAGE_ENEMY_ACCENT_COLORS[1])
        for rect in state["enemy_rects"]:
            draw_crab_enemy(screen, rect, enemy_color, enemy_accent, state["animation_frame"])

        # プレイヤーの弾
        if state["bullet_rect"] is not None:
            draw_player_bullet(screen, state["bullet_rect"])

        # UFO
        if state["ufo_rect"] is not None:
            draw_ufo(screen, state["ufo_rect"], UFO_COLOR, UFO_ACCENT_COLOR)

        # 敵の弾
        for bullet in state["enemy_bullets"]:
            draw_enemy_bullet(screen, bullet)

        if game_state == "PLAYING":
            score_surface = font_small.render(
                f"Score: {state['score']}", True, (230, 230, 230)
            )
            screen.blit(score_surface, (12, 10))
            stage_surface = font_small.render(
                f"Stage: {state['stage']}/{STAGE_COUNT}", True, (230, 230, 230)
            )
            stage_rect = stage_surface.get_rect(topright=(SCREEN_WIDTH - 12, 10))
            screen.blit(stage_surface, stage_rect)

            # 残機表示
            draw_lives(screen, state["lives"], SCREEN_WIDTH // 2 - 50, 8)

            if state["stage_banner_timer"] > 0:
                draw_centered_text(f"STAGE {state['stage']}", font_large, 260)
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
