import os
import pygame
import tkinter as tk
from settings import config as cfg
from fileio.load import import_image_dir


# Function to initialize pygame modules and screen
def builder_init():
    # Clear terminal (Windows syntax)
    if os.name == "nt":
        os.system("cls")

    # Create the main application window for messages and hide it
    root = tk.Tk()
    root.withdraw()

    # Initialize pygame modules
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    # Use lucidaconsole text for retro look
    fonts = {}
    fonts["small"] = pygame.font.SysFont("lucidaconsole", 20)
    fonts["normal"] = pygame.font.SysFont("lucidaconsole", 24)

    # Dimensions for window
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), vsync=1)

    # Set window title
    pygame.display.set_caption("Level Builder")

    # Create a list of colors to be used for selecting maze wall color
    maze_colors = []
    maze_color_index = 0
    for key, value in cfg.COLORS.items():
        if key not in ["white", "black", "ltgray"]:
            maze_colors.append(value)

    # Scale variables
    maze_width = cfg.MAZE_WIDTH * cfg.SCALE_FACTOR
    maze_height = cfg.MAZE_HEIGHT * cfg.SCALE_FACTOR
    block_width = cfg.BLOCK_WIDTH * cfg.SCALE_FACTOR
    image_boundary = cfg.IMAGE_BOUNDARY * cfg.SCALE_FACTOR
    min_block_spacing = cfg.MIN_BLOCK_SPACING * cfg.SCALE_FACTOR

    # Initialize level speed and arrow key selection
    level_speed_index = 0
    arrow_index = -1

    # List of dirty rectangles, representing areas of screen to be updated
    dirty_rects = []

    # List of mouse coordinates that have been added
    chosen_coords = []

    # Track previous shifted coordinate history
    shifted_coords_history = []

    # List of assets and asset coordinates that have been added
    asset_coords = []
    asset_letters = []
    asset_defs = cfg.ASSET_DEFS.copy()

    # Fill background with white color
    screen.fill(cfg.COLORS["white"])

    return (
        clock,
        fonts,
        screen,
        maze_colors,
        maze_color_index,
        maze_width,
        maze_height,
        block_width,
        image_boundary,
        min_block_spacing,
        level_speed_index,
        arrow_index,
        dirty_rects,
        chosen_coords,
        shifted_coords_history,
        asset_coords,
        asset_letters,
        asset_defs,
    )


# Function to display draw instruction text
def print_draw_instructions(fonts, screen):
    for row, text_line in enumerate(cfg.DRAW_STRINGS):
        if row <= 7:
            selected_color = cfg.COLORS["black"]
        elif row == 8:
            selected_color = cfg.COLORS["dkgreen"]
        elif row == 9:
            selected_color = cfg.COLORS["red"]
        else:
            selected_color = cfg.COLORS["orange"]
        text_surface = fonts["normal"].render(text_line, True, selected_color)
        loc = cfg.TEXT_LOC["maze_draw"]
        screen.blit(text_surface, (loc[0], loc[1] + row * loc[2]))

    text_surface = fonts["normal"].render(cfg.LOAD_TEXT, True, cfg.COLORS["black"])
    loc = cfg.TEXT_LOC["maze_load"]
    screen.blit(text_surface, (loc[0], loc[1]))


# Function to load enemy images and max quantities
def init_enemies():
    # Initialize number of enemies
    enemy_quantity = {}
    enemy_quantity["corn"] = range(cfg.MAX_CORN + 1)
    enemy_quantity["tomato"] = range(cfg.MAX_TOMATO + 1)
    enemy_quantity["pumpkin"] = range(cfg.MAX_PUMPKIN + 1)
    enemy_index = {}
    enemy_index["corn"] = 0
    enemy_index["tomato"] = 0
    enemy_index["pumpkin"] = 0

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
        images[image].set_colorkey(cfg.COLORS["teal"])

    enemy_image = {}
    enemy_image["corn"] = images["corn"]
    enemy_image["tomato"] = images["tomato"]
    enemy_image["pumpkin"] = images["pumpkin"]

    return enemy_quantity, enemy_index, images, enemy_image


# Function to draw enemy sprites
def draw_enemies(screen, corn_image, tomato_image, pumpkin_image):
    # Display enemy images
    screen.blit(corn_image, cfg.IMAGE_LOC["corn"])
    screen.blit(tomato_image, cfg.IMAGE_LOC["tomato"])
    screen.blit(pumpkin_image, cfg.IMAGE_LOC["pumpkin"])

    # Update initial display
    pygame.display.update()


# Function to draw text for speed and enemy quantity
def draw_speed_enemy_text(
    fonts,
    screen,
    level_speed_index,
    corn_quantities,
    corn_index,
    tomato_quantities,
    tomato_index,
    pumpkin_quantities,
    pumpkin_index,
):
    # Display level speed in blue color
    text_surface = fonts["normal"].render(
        str(cfg.LEVEL_SPEED_ORDER[level_speed_index]), True, cfg.COLORS["blue"]
    )
    loc = cfg.TEXT_LOC["level_speed"]
    screen.blit(text_surface, (loc[0], loc[1]))

    # Display number of enemies below each image
    text_surface = fonts["normal"].render(
        str(corn_quantities[corn_index]), True, cfg.COLORS["dkgreen"]
    )
    screen.blit(text_surface, cfg.TEXT_LOC["corn"])
    text_surface = fonts["normal"].render(
        str(tomato_quantities[tomato_index]), True, cfg.COLORS["red"]
    )
    screen.blit(text_surface, cfg.TEXT_LOC["tomato"])
    text_surface = fonts["normal"].render(
        str(pumpkin_quantities[pumpkin_index]), True, cfg.COLORS["orange"]
    )
    screen.blit(text_surface, cfg.TEXT_LOC["pumpkin"])

    # Update initial display
    pygame.display.update()


# Class to store builder loop flags
class Flags:
    def __init__(self):
        self.running = True
        self.mouse_left_held = False
        self.mouse_right_held = False
        self.mouse_right_click = False
        self.arrow_pressed = False
        self.maze_draw = True
        self.x_pressed = True
        self.draw_dots = False
