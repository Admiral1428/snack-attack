import pygame
import time
from settings import config as cfg
from rect.utils import define_rect, shift_rect_to_divisible_pos
from rect.draw import draw_square
from path.utils import (
    rect_within_boundary,
    rect_gives_uniform_path,
)


# Function to process inputs for path drawing
def process_path_inputs(
    flags,
    chosen_coords,
    image_boundary,
    block_width,
    min_block_spacing,
    current_arrow,
    arrow_index,
):
    if flags.arrow_pressed:
        if not chosen_coords:
            # If no previous points chosen with mouse, start at upper left corner
            current_selected_pos = (
                cfg.DRAW_IMAGE_X + image_boundary + int(block_width / 2),
                cfg.DRAW_IMAGE_Y + image_boundary + int(block_width / 2),
            )
        else:
            try:
                current_selected_pos = chosen_coords[-1]
                if current_arrow == pygame.K_UP:
                    current_selected_pos = (
                        chosen_coords[arrow_index][0],
                        chosen_coords[arrow_index][1] - min_block_spacing,
                    )
                elif current_arrow == pygame.K_DOWN:
                    current_selected_pos = (
                        chosen_coords[arrow_index][0],
                        chosen_coords[arrow_index][1] + min_block_spacing,
                    )
                elif current_arrow == pygame.K_LEFT:
                    current_selected_pos = (
                        chosen_coords[arrow_index][0] - min_block_spacing,
                        chosen_coords[arrow_index][1],
                    )
                elif current_arrow == pygame.K_RIGHT:
                    current_selected_pos = (
                        chosen_coords[arrow_index][0] + min_block_spacing,
                        chosen_coords[arrow_index][1],
                    )
            except:
                # Catching case where index may be out of bounds
                pass
    else:
        current_selected_pos = pygame.mouse.get_pos()

    return current_selected_pos


# Function to draw path
def draw_path(
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
):

    current_selected_pos = process_path_inputs(
        flags,
        chosen_coords,
        image_boundary,
        block_width,
        min_block_spacing,
        current_arrow,
        arrow_index,
    )

    my_rect = define_rect(current_selected_pos, block_width)
    my_rect = shift_rect_to_divisible_pos(
        my_rect,
        cfg.DRAW_IMAGE_X,
        cfg.DRAW_IMAGE_Y,
        min_block_spacing,
        image_boundary,
    )

    # If chosen coordinate from arrow keys is already in chosen coordinates,
    # save that space so that user can backtrack.
    # Subsequently highlight the block with flashing so that they know where
    # they are for context.
    if flags.arrow_pressed and my_rect.center in chosen_coords:
        arrow_index = chosen_coords.index(my_rect.center)
        for i in range(3):
            draw_square(my_rect, screen, cfg.COLORS["white"], dirty_rects)
            time.sleep(1 / 30)
            draw_square(my_rect, screen, cfg.COLORS["black"], dirty_rects)
            time.sleep(1 / 30)
    else:
        arrow_index = -1

    # Reset flag for arrow key press
    flags.arrow_pressed = False

    # Coarsen inputs prior to checking maze grid to optimize runtime
    coords_scaled = []
    for coord in chosen_coords:
        coords_scaled.append(
            (
                int((coord[0] - cfg.DRAW_IMAGE_X - image_boundary) / cfg.SCALE_FACTOR),
                int((coord[1] - cfg.DRAW_IMAGE_Y - image_boundary) / cfg.SCALE_FACTOR),
            )
        )
    new_center = (
        int((my_rect.center[0] - cfg.DRAW_IMAGE_X - image_boundary) / cfg.SCALE_FACTOR),
        int((my_rect.center[1] - cfg.DRAW_IMAGE_Y - image_boundary) / cfg.SCALE_FACTOR),
    )
    my_rect_scaled = define_rect(new_center, cfg.BLOCK_WIDTH)

    # Check to make sure the current shifted position is not the same as
    # the last, and that it's not in chosen coords. If all criteria met,
    # draw the new path square
    if (
        not shifted_coords_history or my_rect.center != shifted_coords_history[-1]
    ) and my_rect.center not in chosen_coords:
        shifted_coords_history.append(my_rect.center)

        if rect_within_boundary(
            my_rect,
            cfg.DRAW_IMAGE_X,
            cfg.DRAW_IMAGE_Y,
            image_boundary,
            maze_width,
            maze_height,
        ) and rect_gives_uniform_path(
            coords_scaled,
            my_rect_scaled,
            cfg.MAZE_WIDTH,
            cfg.MAZE_HEIGHT,
            0,
            0,
            0,
            cfg.BLOCK_WIDTH,
        ):
            # Add updated mouse position to list of previous points
            chosen_coords.append((my_rect.center))
            draw_square(my_rect, screen, cfg.COLORS["black"], dirty_rects)

    return flags, arrow_index


# Function to erase a path rect, then re-drawing overlapping squares
def erase_and_redraw(
    cur_coord,
    block_width,
    maze_colors,
    maze_color_index,
    screen,
    dirty_rects,
    chosen_coords,
):
    # Draw a block overtop the old coordinate
    my_rect = define_rect(cur_coord, block_width)
    selected_color = maze_colors[maze_color_index]
    draw_square(my_rect, screen, selected_color, dirty_rects)

    # Draw previous coordinates which were overlapping erased square
    for coord in chosen_coords:
        temp_rect = define_rect(coord, block_width)
        if temp_rect.colliderect(my_rect):
            draw_square(temp_rect, screen, cfg.COLORS["black"], dirty_rects)


# Function to erase path at current mouse location
def erase_path(
    block_width,
    min_block_spacing,
    image_boundary,
    shifted_coords_history,
    chosen_coords,
    maze_colors,
    maze_color_index,
    screen,
    dirty_rects,
):
    current_selected_pos = pygame.mouse.get_pos()

    my_rect = define_rect(current_selected_pos, block_width)
    my_rect = shift_rect_to_divisible_pos(
        my_rect,
        cfg.DRAW_IMAGE_X,
        cfg.DRAW_IMAGE_Y,
        min_block_spacing,
        image_boundary,
    )

    if my_rect.center in chosen_coords:
        # Determine if removing this coordinate produces legal maze
        temp_coords = chosen_coords.copy()
        temp_coords.remove(my_rect.center)
        # Coarsen inputs prior to checking maze grid to optimize runtime
        coords_scaled = []
        for coord in temp_coords:
            coords_scaled.append(
                (
                    int(
                        (coord[0] - cfg.DRAW_IMAGE_X - image_boundary)
                        / cfg.SCALE_FACTOR
                    ),
                    int(
                        (coord[1] - cfg.DRAW_IMAGE_Y - image_boundary)
                        / cfg.SCALE_FACTOR
                    ),
                )
            )
        if rect_gives_uniform_path(
            coords_scaled,
            None,
            cfg.MAZE_WIDTH,
            cfg.MAZE_HEIGHT,
            0,
            0,
            0,
            cfg.BLOCK_WIDTH,
        ):
            # Remove chosen position and redraw around it
            chosen_coords.remove(my_rect.center)
            shifted_coords_history.remove(my_rect.center)

            erase_and_redraw(
                my_rect.center,
                block_width,
                maze_colors,
                maze_color_index,
                screen,
                dirty_rects,
                chosen_coords,
            )


# Function to undo drawing of path rect
def undo_path_rect(
    chosen_coords,
    shifted_coords_history,
    block_width,
    maze_colors,
    maze_color_index,
    screen,
    dirty_rects,
    flags,
):
    # Remove last coordinate (undo)
    last_coord = chosen_coords.pop()

    # Remove last shifted coordinate from history
    shifted_coords_history.pop()

    erase_and_redraw(
        last_coord,
        block_width,
        maze_colors,
        maze_color_index,
        screen,
        dirty_rects,
        chosen_coords,
    )

    # Reset flag for right click
    flags.x_pressed = False

    return flags


# Function to undo last asset placement
def undo_asset_placement(
    asset_coords, asset_defs, block_width, screen, dirty_rects, flags
):
    # Get last coordinate
    remove_asset_coord = asset_coords.pop()

    # Set asset coordinate in dictionary to ()
    for asset in asset_defs:
        if asset.get("location") == remove_asset_coord:
            asset["location"] = ()
            break

    # Erase asset on maze by drawing black square
    temp_rect = define_rect(remove_asset_coord, block_width)
    draw_square(temp_rect, screen, cfg.COLORS["black"], dirty_rects)

    # Reset flag for right click
    flags.mouse_right_click = False

    return flags
