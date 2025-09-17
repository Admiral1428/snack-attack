import os
import pygame
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from settings import config as cfg
from rect.utils import define_rect, shift_rect_to_divisible_pos
from rect.draw import draw_square, draw_asset, draw_maze
from grid.utils import invert_maze_to_grid, grid_space
from fileio.load import import_image_dir
from fileio.export import (
    export_path_coords_to_csv,
    export_asset_coords_to_csv,
    export_metadata,
    move_files,
)
from path.utils import (
    rect_within_boundary,
    rect_gives_uniform_path,
)
from builder.start import (
    builder_init,
    Flags,
    print_draw_instructions,
    init_enemies,
    draw_enemies,
    draw_speed_enemy_text,
)
from builder.input import process_input
from builder.draw import draw_path, undo_path_rect, undo_asset_placement

# Initialize level builder
(
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
) = builder_init()


# Draw empty maze onto screen, with a gray boundary
# and inside drawable teal area
draw_maze(
    cfg.DRAW_IMAGE_X,
    cfg.DRAW_IMAGE_Y,
    image_boundary,
    maze_width,
    maze_height,
    block_width,
    cfg.COLORS["ltgray"],
    cfg.COLORS["ltgray"],
    [],
    screen,
    0,
    None,
)
draw_maze(
    cfg.DRAW_IMAGE_X + image_boundary,
    cfg.DRAW_IMAGE_Y + image_boundary,
    0,
    maze_width,
    maze_height,
    block_width,
    cfg.COLORS["teal"],
    cfg.COLORS["teal"],
    [],
    screen,
    0,
    None,
)

# Display instruction text
print_draw_instructions(fonts, screen)

# Initialize enemy images and quantities
enemy_quantity, enemy_index, images, enemy_image = init_enemies()


# Draw enemy sprites
draw_enemies(screen, enemy_image["corn"], enemy_image["tomato"], enemy_image["pumpkin"])

# Draw text for level speed and enemy quantity
draw_speed_enemy_text(
    fonts,
    screen,
    level_speed_index,
    enemy_quantity["corn"],
    enemy_index["corn"],
    enemy_quantity["tomato"],
    enemy_index["tomato"],
    enemy_quantity["pumpkin"],
    enemy_index["pumpkin"],
)

# Builder loop flags
flags = Flags()

# Builder loop
while flags.running:
    for event in pygame.event.get():
        (
            flags,
            current_arrow,
            level_speed_index,
            enemy_index,
            maze_color_index,
            asset_letters,
            asset_defs,
        ) = process_input(
            event,
            flags,
            screen,
            fonts,
            asset_coords,
            maze_width,
            maze_height,
            min_block_spacing,
            block_width,
            image_boundary,
            maze_colors,
            chosen_coords,
            dirty_rects,
            enemy_quantity,
            enemy_index,
            level_speed_index,
            maze_color_index,
            asset_letters,
            asset_defs,
        )

    # Limit input collection to 60 hz to limit CPU overhead
    clock.tick(60)

    # Check if an arrow key was pressed, or if left mouse is currently held
    # down (outside of event loop) If so, draw a new square at that location,
    # if shifted to nearest nth coordinate is deemed legal (based on
    # min_block_spacing)
    if (flags.arrow_pressed or flags.mouse_left_held) and flags.maze_draw:
        flags, arrow_index = draw_path(
            flags,
            chosen_coords,
            maze_height,
            maze_width,
            image_boundary,
            block_width,
            min_block_spacing,
            current_arrow,
            screen,
            dirty_rects,
            shifted_coords_history,
            arrow_index,
        )
    # Undo last path draw
    elif flags.mouse_right_click and len(chosen_coords) > 0 and flags.maze_draw:
        flags = undo_path_rect(
            chosen_coords,
            shifted_coords_history,
            block_width,
            maze_colors,
            maze_color_index,
            screen,
            dirty_rects,
            flags,
        )
    # Undo last asset drawing
    elif flags.mouse_right_click and len(asset_coords) > 0 and not flags.maze_draw:
        flags = undo_asset_placement(
            asset_coords, asset_defs, block_width, screen, dirty_rects, flags
        )


# Quit
pygame.quit()
