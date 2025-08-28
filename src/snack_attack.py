import os
import ast
import time
import pygame
from utils.exceptions import CustomError
from rect.draw import draw_maze
from asset.sprite import Sprite
from fileio.load import (
    import_image_dir,
    get_levels,
    read_csv_dict,
    read_csv_path,
    import_maze_grid_from_txt,
)


# Clear terminal (Windows syntax)
if os.name == "nt":
    os.system("cls")

# Initialize pygame modules
pygame.init()
pygame.font.init()

# Use Arial text
font = pygame.font.SysFont("Arial", 26)

# Dimensions for window
width, height = (1600, 900)
screen = pygame.display.set_mode((width, height), vsync=1)

# Define maze properties
maze_width = 256
maze_height = 192
block_width = 12
min_block_spacing = 4
draw_image_x = 20
draw_image_y = 20
image_boundary = 4

# Set window title
pygame.display.set_caption("Snack Attack")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
teal = (0, 168, 168)
yellow = (255, 255, 0)
orange = (255, 128, 0)
green = (0, 255, 0)
dkgreen = (0, 102, 0)
purple = (128, 0, 128)
magenta = (253, 61, 181)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (128, 128, 128)

# Create a list of colors to be used for selecting maze wall color
maze_colors = [teal, yellow, orange, green, dkgreen, purple, magenta, red, blue, gray]

# Scale variables
scale_factor = 4
maze_width *= scale_factor
maze_height *= scale_factor
block_width *= scale_factor
min_block_spacing *= scale_factor
image_boundary *= scale_factor

# Fill background with black color
screen.fill(black)

# Display instruction text
text_strings = [
    "I, K, J, L = Move up, down, left, right",
    "Space = Stop movement",
    "F = Fire weapon",
    "Pause = Pause game",
    "S = Skip level",
]

# Load enemy images and scale them
images = import_image_dir("../assets/sprites/")
for image in images:
    images[image] = pygame.transform.scale(
        images[image],
        (
            int(images[image].get_width() * scale_factor),
            int(images[image].get_height() * scale_factor),
        ),
    )
    # Make teal the transparent color
    images[image].set_colorkey(teal)

# Get levels and their supporting file paths
level_dir = "../assets/levels/"
levels = get_levels(level_dir)

if not levels:
    raise CustomError(f"Could not load any level folders at {level_dir}")
else:
    level_index = 0

# Level speed definitions for time delay
level_speed_timing = {"slow": 0.005, "medium": 0.004, "fast": 0.003, "frantic": 0.002}

# Update initial display
pygame.display.update()

# Game loop
maze_draw = True
draw_asset_starts = False
rungame = False
paused = False
need_pause_text = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                s_pressed = True
            if event.key == pygame.K_PAUSE:
                paused = not paused
                need_pause_text = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s and s_pressed:
                # Skip to next level
                if level_index >= len(levels) - 1:
                    level_index = 0
                else:
                    level_index += 1
                maze_draw = True
                s_pressed = False

    # Draw maze and instructions on screen
    if maze_draw:
        maze_assets = read_csv_dict(levels[level_index].get("assets"))
        maze_metadata = read_csv_dict(levels[level_index].get("metadata"))[0]
        maze_path = read_csv_path(levels[level_index].get("path"))
        maze_grid = import_maze_grid_from_txt(levels[level_index].get("grid"))

        # Perform clearing of screen to remove old maze and clear up memory
        screen.fill(black)
        pygame.display.flip()

        # Print instructions and draw maze
        for row, text_line in enumerate(text_strings):
            text_surface = font.render(text_line, True, white)
            screen.blit(text_surface, (1140, 500 + row * 50))
        draw_maze(
            draw_image_x,
            draw_image_y,
            image_boundary,
            maze_width,
            maze_height,
            block_width,
            ast.literal_eval(maze_metadata.get("maze_color")),
            black,
            maze_path,
            screen,
        )

        # Save subsurface for game loop re-draw
        rect_area = pygame.Rect(0, 0, width, height)
        temp_surf = screen.subsurface(rect_area)
        area_surf = temp_surf.copy()

        # Save relevant metadata
        level_speed = maze_metadata.get("level_speed")

        # Assign appropriate delay for level speed, defaulting to slow
        if level_speed in level_speed_timing.keys():
            level_speed_delay = level_speed_timing.get(level_speed)
        else:
            level_speed_delay = level_speed_timing.get("slow")

        # Save maze asset coordinates into a single dictionary and check validity
        # of asset coordinates with error handling
        allowable_letters = ["S", "R", "E", "1", "2", "3", "4", "H"]
        asset_coord = {}
        for dict in maze_assets:
            asset_coord[dict.get("letter")] = ast.literal_eval(dict.get("location"))
        if (
            len(asset_coord) != len(allowable_letters)
            or any(
                not isinstance(value, tuple) or not value
                for value in asset_coord.values()
            )
            or any(key not in allowable_letters for key in asset_coord.keys())
        ):
            custom_string = (
                "Level error! The asset coordinates csv must include"
                " exactly 8 unique asset locations, assigned to each of the following: "
            )
            raise CustomError(custom_string + str(allowable_letters))

        # Set flags
        draw_asset_starts = True
        maze_draw = False
    # Draw assets at their starting locations
    elif draw_asset_starts:

        # Initialize player
        player = Sprite(
            "player",
            images["combine"],
            asset_coord.get("S"),
            100,
            True,
            int(block_width / 4),
            block_width,
        )

        # Move player to respawn if they were destroyed
        if player.isdestroyed():
            start_to_respawn = (
                asset_coord.get("R")[0] - asset_coord.get("S")[0],
                asset_coord.get("R")[1] - asset_coord.get("S")[1],
            )
            player.move(start_to_respawn, maze_grid)

        # Draw player, update screen, and set flags
        display_rect = player.draw(draw_image_x, draw_image_y, image_boundary, screen)

        # Update screen and set flags
        pygame.display.flip()
        draw_asset_starts = False
        rungame = True
    elif rungame and not paused:
        # Clear screen and re-draw background
        screen.fill(black)
        screen.blit(area_surf, (0, 0))

        # Player movement input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l]:
            player.set_direction(1, 0, maze_grid)  # right
        elif keys[pygame.K_j]:
            player.set_direction(-1, 0, maze_grid)  # left
        elif keys[pygame.K_i]:
            player.set_direction(0, -1, maze_grid)  # up
        elif keys[pygame.K_k]:
            player.set_direction(0, 1, maze_grid)  # down
        elif keys[pygame.K_SPACE]:
            player.set_direction(0, 0, maze_grid)  # stop

        # Set delay to achieve level speed
        time.sleep(level_speed_delay)

        # Move player, draw sprite
        player.perform_move(maze_grid)
        player.draw(draw_image_x, draw_image_y, image_boundary, screen)

        # Update screen
        pygame.display.flip()
    elif paused:
        if need_pause_text:
            text_surface = font.render(
                "Game paused. Press Pause button to resume.", True, white
            )
            screen.blit(text_surface, (500, 850))
            pygame.display.flip()
            need_pause_text = False

# Quit
pygame.quit()
