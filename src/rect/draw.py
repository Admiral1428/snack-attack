import pygame
import time
from settings import config as cfg
from rect.utils import define_rect, shift_rect_to_divisible_pos
from builder.utils import scale_coords
from path.utils import (
    rect_within_boundary,
    rect_gives_uniform_path,
)


# Function to draw square onto the screen
def draw_square(my_rect, screen, selected_color, dirty_rects):
    draw_rect = pygame.draw.rect(screen, selected_color, my_rect)

    dirty_rects.append(draw_rect)

    # Update necessary portion of the screen
    pygame.display.update(dirty_rects)
    dirty_rects.clear()


# Function to choose and draw location of asset for level builder
def draw_asset(
    asset_coords,
    chosen_coords,
    dirty_rects,
    screen,
    draw_image_x,
    draw_image_y,
    maze_width,
    maze_height,
    image_boundary,
    min_block_spacing,
    block_width,
    letter,
    selected_color,
    black,
    font,
):
    # Get current mouse position where letter was pressed, make rect,
    # and shift to divisible position.
    current_mouse_pos = pygame.mouse.get_pos()
    my_rect = define_rect(current_mouse_pos, block_width)
    my_rect = shift_rect_to_divisible_pos(
        my_rect, draw_image_x, draw_image_y, min_block_spacing, image_boundary
    )

    # Check if position could be interpolated between two adjacent locations
    rects_above = []
    rects_below = []
    rects_left = []
    rects_right = []
    increment = min_block_spacing
    while increment < block_width:
        rect_above = my_rect.move(0, -increment)
        rects_above.append((rect_above.center))
        rect_below = my_rect.move(0, increment)
        rects_below.append((rect_below.center))
        rect_left = my_rect.move(-increment, 0)
        rects_left.append((rect_left.center))
        rect_right = my_rect.move(increment, 0)
        rects_right.append((rect_right.center))
        increment += min_block_spacing

    # Check if any interpolatable positions exist in coordinates
    vert_interp = not set(rects_above).isdisjoint(set(chosen_coords)) and not set(
        rects_below
    ).isdisjoint(set(chosen_coords))
    horz_interp = not set(rects_left).isdisjoint(set(chosen_coords)) and not set(
        rects_right
    ).isdisjoint(set(chosen_coords))

    # Check for collision with other assets
    asset_collision = False
    for coord in asset_coords:
        temp_rect = define_rect(coord, block_width)
        if temp_rect.colliderect(my_rect):
            asset_collision = True
            break

    # Check if path legal (since interpolated position may be within a wall)
    # Coarsen inputs prior to checking maze grid to optimize runtime
    coords_scaled = scale_coords(chosen_coords, image_boundary)
    new_center = (
        int((my_rect.center[0] - cfg.DRAW_IMAGE_X - image_boundary) / cfg.SCALE_FACTOR),
        int((my_rect.center[1] - cfg.DRAW_IMAGE_Y - image_boundary) / cfg.SCALE_FACTOR),
    )
    my_rect_scaled = define_rect(new_center, cfg.BLOCK_WIDTH)

    legal_path_position = False
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
        legal_path_position = True

    # If asset does not collide with another asset, and it's within maze path
    if legal_path_position and not asset_collision and (
        my_rect.center in chosen_coords or vert_interp or horz_interp
    ):
        # Create square with outer boundary of appropriate color,
        # and letter inside
        draw_square(my_rect, screen, selected_color, dirty_rects)
        inner_rect = define_rect(my_rect.center, int(block_width * 0.8))
        draw_square(inner_rect, screen, black, dirty_rects)

        # Draw letter inside center of box
        text_surface = font.render(letter, True, selected_color)
        text_rect = text_surface.get_rect()
        text_rect.center = my_rect.center
        screen.blit(text_surface, text_rect)
        pygame.display.update(text_rect)

        # Return adjusted location of the asset after appending to list
        asset_coords.append((my_rect.center))
        return my_rect.center
    return None


# Function to draw maze walls
def draw_maze(
    draw_image_x,
    draw_image_y,
    image_boundary,
    maze_width,
    maze_height,
    block_width,
    maze_color,
    path_color,
    path_coords,
    screen,
    time_delay,
    quit_key,
    dot_color,
):
    outer_rect = pygame.Rect(
        draw_image_x,
        draw_image_y,
        maze_width + (2 * image_boundary),
        maze_height + (2 * image_boundary),
    )
    pygame.draw.rect(screen, maze_color, outer_rect)
    pygame.display.update()

    exit_key_selected = False
    dirty_rects = []
    for coord in path_coords:
        shifted_coord = (
            coord[0] + draw_image_x + image_boundary,
            coord[1] + draw_image_x + image_boundary,
        )
        my_rect = define_rect(shifted_coord, block_width)
        draw_square(my_rect, screen, path_color, dirty_rects)

        if time_delay > 0:
            # Pause to create an old-school block-by-block tracing of the level,
            # and gives player a moment to recover from previous level
            time.sleep(time_delay)

        # Quit draw if key pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == quit_key:
                    quit_key_down = True
            if event.type == pygame.KEYUP:
                try:
                    if event.key == quit_key and quit_key_down:
                        exit_key_selected = True
                        break
                except:
                    pass

        if exit_key_selected:
            break
    # Overlay dots to show path if color specified
    if dot_color:
        for coord in path_coords:
            shifted_coord = (
                coord[0] + draw_image_x + image_boundary,
                coord[1] + draw_image_x + image_boundary,
            )
            my_rect = define_rect(shifted_coord, int(block_width / 12))
            draw_square(my_rect, screen, dot_color, dirty_rects)
    return exit_key_selected
