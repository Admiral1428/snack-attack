import pygame
from settings import config as cfg
from builder.action import (
    export_maze_files,
    change_maze_color,
    cycle_level_speed,
    cycle_enemy_quantity,
    init_asset_placement,
    assign_asset_loc,
    import_maze_from_file,
)
from rect.draw import draw_maze


# Function to handle inputs for level builder
def process_input(
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
    shifted_coords_history,
):
    current_arrow = None
    flags.arrow_pressed = False
    if event.type == pygame.QUIT:
        flags.running = False
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left mouse button
            flags.mouse_left_held = True
        elif event.button == 3:  # Right mouse button
            flags.mouse_right_click = True
            flags.mouse_right_held = True
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:  # Left mouse button
            flags.mouse_left_held = False
        elif event.button == 3:  # Right mouse button
            flags.mouse_right_held = False
            if flags.draw_dots:
                # Re-draw maze without center dots
                chosen_coords_draw = [
                    (
                        x - cfg.DRAW_IMAGE_X - image_boundary,
                        y - cfg.DRAW_IMAGE_Y - image_boundary,
                    )
                    for x, y in chosen_coords
                ]
                draw_maze(
                    cfg.DRAW_IMAGE_X + image_boundary,
                    cfg.DRAW_IMAGE_Y + image_boundary,
                    0,
                    maze_width,
                    maze_height,
                    int(block_width),
                    maze_colors[maze_color_index],
                    cfg.COLORS["black"],
                    chosen_coords_draw,
                    screen,
                    0,
                    None,
                    None,
                )
                flags.draw_dots = False
    elif event.type == pygame.KEYDOWN:
        if flags.maze_draw and event.key in [
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_LEFT,
            pygame.K_RIGHT,
        ]:
            flags.arrow_pressed = True
            match event.key:
                case pygame.K_UP:
                    current_arrow = pygame.K_UP
                case pygame.K_DOWN:
                    current_arrow = pygame.K_DOWN
                case pygame.K_LEFT:
                    current_arrow = pygame.K_LEFT
                case pygame.K_RIGHT:
                    current_arrow = pygame.K_RIGHT
        elif event.key == pygame.K_c and not flags.maze_draw:
            export_maze_files(
                screen,
                asset_coords,
                maze_width,
                maze_height,
                image_boundary,
                chosen_coords,
                maze_colors,
                maze_color_index,
                level_speed_index,
                enemy_quantity,
                enemy_index,
                asset_defs,
            )
        elif event.key == pygame.K_x and flags.maze_draw:
            flags.x_pressed = True
        elif event.key == pygame.K_w and flags.maze_draw:
            maze_color_index = change_maze_color(
                screen,
                maze_color_index,
                maze_colors,
                image_boundary,
                maze_width,
                maze_height,
            )
        elif event.key == pygame.K_f and flags.maze_draw:
            level_speed_index = cycle_level_speed(
                level_speed_index, screen, dirty_rects, fonts
            )
        elif event.key == pygame.K_j and flags.maze_draw:
            enemy_index = cycle_enemy_quantity(
                "corn", enemy_index, enemy_quantity, screen, fonts, dirty_rects
            )
        elif event.key == pygame.K_k and flags.maze_draw:
            enemy_index = cycle_enemy_quantity(
                "tomato", enemy_index, enemy_quantity, screen, fonts, dirty_rects
            )
        elif event.key == pygame.K_l and flags.maze_draw:
            enemy_index = cycle_enemy_quantity(
                "pumpkin", enemy_index, enemy_quantity, screen, fonts, dirty_rects
            )
        elif event.key == pygame.K_ESCAPE and flags.maze_draw:
            chosen_coords, shifted_coords_history, maze_color_index = (
                import_maze_from_file(
                    image_boundary, maze_width, maze_height, block_width, screen
                )
            )
        elif event.key == pygame.K_a:
            asset_letters, asset_defs = init_asset_placement(
                chosen_coords,
                image_boundary,
                maze_width,
                maze_height,
                screen,
                flags,
                fonts,
                asset_letters,
                asset_defs,
            )
        elif not flags.maze_draw and event.unicode.lower() in asset_letters:
            asset_defs = assign_asset_loc(
                event,
                asset_coords,
                chosen_coords,
                dirty_rects,
                screen,
                image_boundary,
                min_block_spacing,
                block_width,
                fonts,
                asset_defs,
            )

    return (
        flags,
        current_arrow,
        level_speed_index,
        enemy_index,
        maze_color_index,
        asset_letters,
        asset_defs,
        shifted_coords_history,
        chosen_coords,
    )
