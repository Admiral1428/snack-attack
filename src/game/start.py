import os
import ast
import pygame
import time
from collections import deque
from utils.exceptions import CustomError
from settings import config as cfg
from fileio.load import (
    import_image_dir,
    import_sound_dir,
    get_levels,
    read_csv_dict,
)


# Function to initialize pygame modules and screen
def game_init():
    # Clear terminal (Windows syntax)
    if os.name == "nt":
        os.system("cls")

    # Initialize pygame modules screen
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    # Use lucidaconsole text for retro look
    fonts = {}
    fonts["normal"] = pygame.font.SysFont("lucidaconsole", 26)
    fonts["medium"] = pygame.font.SysFont("lucidaconsole", 36)
    fonts["large"] = pygame.font.SysFont("lucidaconsole", 80)

    # Dimensions for window
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), vsync=1)

    # Set window title
    pygame.display.set_caption(cfg.TITLE_TEXT)

    # Scale variables
    maze_width = cfg.MAZE_WIDTH * cfg.SCALE_FACTOR
    maze_height = cfg.MAZE_HEIGHT * cfg.SCALE_FACTOR
    block_width = cfg.BLOCK_WIDTH * cfg.SCALE_FACTOR
    image_boundary = cfg.IMAGE_BOUNDARY * cfg.SCALE_FACTOR

    # Fill background with black color
    screen.fill(cfg.COLORS["black"])

    # Update initial display
    pygame.display.update()

    key_order = deque(maxlen=2)
    direction_order = deque(maxlen=1)
    score = 0
    lives = cfg.LIVES_DEFAULT
    game_time = pygame.time.Clock()
    start_time = time.time()
    pause_start = []

    return (
        fonts,
        screen,
        maze_width,
        maze_height,
        block_width,
        image_boundary,
        key_order,
        direction_order,
        score,
        lives,
        game_time,
        start_time,
        pause_start,
    )


# Function to load and interpret settings file
def load_settings():
    maze_fidelity = ""
    controls_option = None
    settings = read_csv_dict(cfg.DIRS["settings"] + cfg.FILES["settings"])
    for dict in settings:
        for key, value in dict.items():
            if key == "maze_fidelity":
                maze_fidelity = value
            elif key == "controls_option":
                controls_option = ast.literal_eval(value)

    if controls_option not in range(4):
        raise CustomError(cfg.ERROR_STRINGS["controls"])

    # Get maze fidelity options
    maze_fidelity_index = None
    maze_factor = None
    for index, opt in enumerate(cfg.MAZE_FIDELITY_OPTS):
        if maze_fidelity == opt:
            maze_fidelity_index = index
            maze_factor = cfg.MAZE_FIDELITY_FACTORS[index]
    if maze_fidelity_index == None or maze_factor == None:
        raise CustomError(cfg.ERROR_STRINGS["maze_fidelity"])

    return maze_fidelity, maze_fidelity_index, maze_factor, controls_option


# Function to load images, sounds, and levels
def load_resources():
    # Load enemy images and scale them
    images = import_image_dir(cfg.DIRS["images"])
    for image in images:
        images[image] = pygame.transform.scale(
            images[image],
            (
                int(images[image].get_width() * cfg.SCALE_FACTOR),
                int(images[image].get_height() * cfg.SCALE_FACTOR),
            ),
        )
        # Make teal the transparent color
        images[image].set_colorkey(cfg.COLORS["replace_teal"])

    # Get sound effects
    sounds = import_sound_dir(cfg.DIRS["sounds"])

    # Get levels and their supporting file paths
    level_dir = cfg.DIRS["levels"]
    levels = get_levels(level_dir)

    if not levels:
        raise CustomError(f"Could not load any level folders at {level_dir}")
    else:
        level_index = 0

    return images, sounds, levels, level_index


# Class to store game loop flags
class Flags:
    def __init__(self):
        self.running = True
        self.game_intro = True
        self.maze_draw = False
        self.create_sprites = False
        self.rungame = False
        self.paused = False
        self.f1_pressed = False
        self.f5_pressed = False
        self.f10_pressed = False
        self.escape_pressed = False
        self.fire_pressed = False
        self.need_pause_text = False
        self.reached_last_level = False
        self.exit_created = False
        self.exit_found = False
        self.exit_opening = False
        self.exit_closing = False
        self.exit_sound_played = False
        self.screen_change = True
        self.update_animation_speed = False
        self.quit_title = False
