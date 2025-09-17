import pygame
import time
from collections import deque
from settings import config as cfg
from fileio.export import export_settings, move_one_file
from fileio.load import (
    read_csv_dict,
)
from game.play import end_game


# Function to process inputs
def process_input(
    event,
    flags,
    key_order,
    controls_option,
    score,
    lives,
    levels,
    level_index,
    fonts,
    screen,
    sounds,
    game_time,
    start_time,
    pause_start,
):
    pause_delta = 0
    if event.type == pygame.QUIT:
        flags.running = False
    elif event.type == pygame.KEYDOWN and not flags.game_intro:
        if event.key == pygame.K_F10:
            flags.f10_pressed = True
        if event.key == pygame.K_ESCAPE:
            flags.escape_pressed = True
        if event.key == pygame.K_F1:
            flags.screen_change = True
            key_order = deque(maxlen=2)
            if controls_option == len(cfg.CONTROLS_TEXT) - 1:
                controls_option = 0
            else:
                controls_option += 1
            flags.f1_pressed = True

            # Load then re-export settings file
            settings = read_csv_dict(cfg.DIRS["settings"] + cfg.FILES["settings"])
            for key, value in settings[0].items():
                if key == "controls_option":
                    settings[0][key] = controls_option
            export_settings(settings[0])
            move_one_file(cfg.FILES["settings"], ".", cfg.DIRS["settings"])
        if event.key == pygame.K_PAUSE:
            # Adjust game loop start timer based on pause behavior
            if not flags.paused:
                pause_start = time.time()
            else:
                pause_end = time.time()
                pause_delta = pause_end - pause_start
                start_time += pause_delta

            # Pause or unpause, and reset flag for printing text
            flags.paused = not flags.paused
            flags.need_pause_text = True

            # Update game clock at end of pause
            game_time.tick()
        if (
            controls_option == 0
            and event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
        ) or (
            controls_option == 1
            and event.key in [pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l]
        ):
            key_order.append(event.key)
        if (controls_option in [0, 2] and event.key == pygame.K_RETURN) or (
            controls_option in [1, 3] and event.key == pygame.K_f
        ):
            flags.fire_pressed = True
    elif event.type == pygame.KEYUP and not flags.game_intro:
        if event.key == pygame.K_F10 and flags.f10_pressed:
            # Skip to next level
            if level_index >= len(levels) - 1:
                level_index = 0
                flags.reached_last_level = True
            else:
                level_index += 1
            flags.maze_draw = True
            flags.f10_pressed = False
        if event.key == pygame.K_ESCAPE and flags.escape_pressed:
            flags.escape_pressed = False
            flags, level_index, score, lives = end_game(flags, fonts, screen, sounds)
        if event.key == pygame.K_F1 and flags.f1_pressed:
            flags.f1_pressed = False
        if (
            (controls_option in [0, 2] and event.key == pygame.K_RETURN)
            or (controls_option in [1, 3] and event.key == pygame.K_f)
            and flags.fire_pressed
        ):
            flags.fire_pressed = False

    return (
        score,
        lives,
        level_index,
        key_order,
        controls_option,
        flags,
        start_time,
        pause_start,
        pause_delta,
    )
