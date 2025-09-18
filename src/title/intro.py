import ast
import time
import pygame
from settings import config as cfg
from rect.draw import draw_maze
from grid.utils import invert_maze_to_grid
from fileio.export import export_settings, move_one_file
from fileio.load import (
    get_levels,
    read_csv_dict,
    read_csv_path,
)
from game.start import load_settings
from game.level import get_level_data
from game.assets import init_items, init_enemies
from game.play import (
    determine_spawn,
    move_sprites,
    draw_sprites,
    check_game_tick,
)


# Function to factor appropriate variables based on fidelity
def perform_factoring(maze_width, maze_height, block_width, maze_path, maze_factor):
    # Scale inputs prior to creating maze grid, based on chosen fidelity
    maze_width_scaled = int(maze_width / maze_factor)
    maze_height_scaled = int(maze_height / maze_factor)
    block_width_scaled = int(block_width / maze_factor)
    coords_scaled = []
    for coord in maze_path:
        coords_scaled.append((int(coord[0] / maze_factor), int(coord[1] / maze_factor)))

    # Get maze grid
    maze_grid = invert_maze_to_grid(
        coords_scaled,
        maze_width_scaled,
        maze_height_scaled,
        0,
        0,
        0,
        block_width_scaled,
    )

    # Scale game tick based on animation smoothness
    game_tick = cfg.GAME_TICK * maze_factor

    return game_tick, maze_grid


# Function to process inputs during title screen
def process_title_input(
    flags,
    event,
    maze_factor,
    maze_fidelity,
    maze_fidelity_index,
):
    if event.type == pygame.QUIT:
        flags.running = False
        flags.quit_title = True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F5:
            flags.f5_pressed = True
        if event.key == pygame.K_SPACE:
            flags.running = False
    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_F5 and flags.f5_pressed:
            # Cycle to next maze fidelity
            if maze_fidelity_index >= len(cfg.MAZE_FIDELITY_OPTS) - 1:
                maze_fidelity_index = 0
            else:
                maze_fidelity_index += 1
            maze_factor = cfg.MAZE_FIDELITY_FACTORS[maze_fidelity_index]
            maze_fidelity = cfg.MAZE_FIDELITY_OPTS[maze_fidelity_index]

            # Load then re-export settings file
            settings = read_csv_dict(cfg.DIRS["settings"] + cfg.FILES["settings"])
            for key, value in settings[0].items():
                if key == "maze_fidelity":
                    settings[0][key] = maze_fidelity
            export_settings(settings[0])
            move_one_file(cfg.FILES["settings"], ".", cfg.DIRS["settings"])

            flags.update_animation_speed = True
            flags.rungame = False
            flags.f5_pressed = False

    return flags, maze_factor, maze_fidelity, maze_fidelity_index


# Function to print animation information
def print_animation_info(fonts, maze_fidelity, screen):
    for row, text_line in enumerate(cfg.ANIMATION_STRINGS):
        if row == 4:
            text_surface = fonts["normal"].render(
                maze_fidelity, True, cfg.COLORS["yellow"]
            )
        else:
            text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["white"])
        loc = cfg.TEXT_LOC["animation_info"]
        screen.blit(text_surface, (loc[0], loc[1] + row * loc[2]))


# Function to print game info and instructions
def print_intro_text(fonts, screen):
    # Game title, author, version, and begin game text
    text_surface = fonts["large"].render(cfg.TITLE_TEXT, True, cfg.COLORS["white"])
    loc = cfg.TEXT_LOC["title"]
    screen.blit(text_surface, (loc[0], loc[1]))

    text_surface = fonts["normal"].render(cfg.AUTHOR_TEXT, True, cfg.COLORS["white"])
    loc = cfg.TEXT_LOC["author"]
    screen.blit(text_surface, (loc[0], loc[1]))

    text_surface = fonts["normal"].render(cfg.VERSION_TEXT, True, cfg.COLORS["white"])
    loc = cfg.TEXT_LOC["version"]
    screen.blit(text_surface, (loc[0], loc[1]))

    text_surface = fonts["medium"].render(cfg.PROCEED_TEXT, True, cfg.COLORS["white"])
    loc = cfg.TEXT_LOC["proceed"]
    screen.blit(text_surface, (loc[0], loc[1]))


# Function to update screen
def update_title_screen(
    flags, screen, area_surf, fonts, maze_fidelity, sprite_image_data
):
    # Clear screen and re-draw background
    screen.fill(cfg.COLORS["black"])
    screen.blit(area_surf, (0, 0))

    black_rect = pygame.Rect(cfg.BLACK_RECTS["animation"])
    screen.fill(cfg.COLORS["black"], black_rect)
    # Print animation information
    for row, text_line in enumerate(cfg.ANIMATION_STRINGS):
        if row == 4:
            text_surface = fonts["normal"].render(
                maze_fidelity, True, cfg.COLORS["yellow"]
            )
        else:
            text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["white"])
        loc = cfg.TEXT_LOC["animation_info"]
        screen.blit(text_surface, (loc[0], loc[1] + row * loc[2]))

    # Print sprites
    for item in sprite_image_data:
        screen.blit(item[0], item[1])

    pygame.display.flip()
    flags.screen_change = False

    return flags


# Main function to run title screen
def run_title_screen(
    flags,
    fonts,
    screen,
    images,
    sounds,
    maze_width,
    maze_height,
    block_width,
    image_boundary,
):
    sounds["intro"].play()

    # Load game settings
    maze_fidelity, maze_fidelity_index, maze_factor, _ = load_settings()
    game_tick = cfg.GAME_TICK * maze_factor

    # Fill background with black color
    screen.fill(cfg.COLORS["black"])

    # Get levels and their supporting file paths
    levels = get_levels(cfg.DIRS["title"])
    level_index = 0
    maze_path = []
    flags.maze_draw = True

    # Update initial display
    pygame.display.update()

    while flags.running:
        for event in pygame.event.get():
            flags, maze_factor, maze_fidelity, maze_fidelity_index = (
                process_title_input(
                    flags,
                    event,
                    maze_factor,
                    maze_fidelity,
                    maze_fidelity_index,
                )
            )

        # Draw maze and instructions on screen
        if flags.maze_draw:
            maze_assets = read_csv_dict(levels[level_index].get("assets"))
            maze_metadata = read_csv_dict(levels[level_index].get("metadata"))[0]
            maze_path = read_csv_path(levels[level_index].get("path"))

            # Perform clearing of screen to remove old maze and clear up memory
            screen.fill(cfg.COLORS["black"])
            pygame.display.flip()

            draw_maze(
                cfg.DRAW_IMAGE_X,
                cfg.DRAW_IMAGE_Y,
                image_boundary,
                maze_width,
                maze_height,
                block_width,
                ast.literal_eval(maze_metadata.get("maze_color")),
                cfg.COLORS["black"],
                maze_path,
                screen,
                0,
                None,
                None,
            )

            # Print game info and instructions
            print_intro_text(fonts, screen)

            # Save subsurface for game loop re-draw
            rect_area = pygame.Rect(0, 0, cfg.WIDTH, cfg.HEIGHT)
            temp_surf = screen.subsurface(rect_area)
            area_surf = temp_surf.copy()

            # Set flags
            flags.update_animation_speed = True
            flags.maze_draw = False

        if flags.update_animation_speed:
            # Get variables which are affected by maze fidelity
            game_tick, maze_grid = perform_factoring(
                maze_width, maze_height, block_width, maze_path, maze_factor
            )

            # Determine level characteristics
            (
                num_corn,
                num_tomato,
                num_pumpkin,
                pixels_per_second,
                seconds_to_spawn,
                asset_coord,
            ) = get_level_data(flags, maze_factor, maze_metadata, maze_assets)

            flags = update_title_screen(
                flags, screen, area_surf, fonts, maze_fidelity, []
            )

            # Print animation options info
            print_animation_info(fonts, maze_fidelity, screen)

            # Set flags
            flags.create_sprites = True
            flags.update_animation_speed = False

        # Create Sprite objects
        if flags.create_sprites:
            # Initialize items
            items = init_items(asset_coord, images, block_width, maze_factor)

            # Initialize enemies
            corns = init_enemies(
                "corn",
                num_corn,
                images[cfg.IMAGE_SERIES["corn"][0]],
                asset_coord.get("E"),
                pixels_per_second,
                int(block_width / (maze_factor * 2)),
                int(block_width / maze_factor),
                False,
            )
            tomatoes = init_enemies(
                "tomato",
                num_tomato,
                images[cfg.IMAGE_SERIES["tomato"][0]],
                asset_coord.get("E"),
                pixels_per_second,
                int(block_width / (maze_factor * 2)),
                int(block_width / maze_factor),
                False,
            )
            pumpkins = init_enemies(
                "pumpkin",
                num_pumpkin,
                images[cfg.IMAGE_SERIES["pumpkin"][0]],
                asset_coord.get("E"),
                pixels_per_second,
                int(block_width / (maze_factor * 2)),
                int(block_width / maze_factor),
                True,
            )

            # Update screen, set flags and variables
            game_time = pygame.time.Clock()
            start_time = time.time()
            flags.rungame = True
            flags.screen_change = True
            flags.create_sprites = False
            spawned_enemies = 0
        # Primary game loop
        elif flags.rungame:
            # Clear images and Rects for screen blit
            sprite_image_data = []

            # Get alive enemies
            alive_corns = [corn for corn in corns if not corn.is_destroyed()]
            alive_tomatoes = [
                tomato for tomato in tomatoes if not tomato.is_destroyed()
            ]
            alive_pumpkins = [
                pumpkin for pumpkin in pumpkins if not pumpkin.is_destroyed()
            ]

            # Determine whether to spawn enemies based on time and their state
            alive_enemies = alive_corns + alive_tomatoes + alive_pumpkins
            spawned_enemies = determine_spawn(
                start_time, spawned_enemies, seconds_to_spawn, alive_enemies
            )
            active_enemies = [enemy for enemy in alive_enemies if enemy.can_spawn()]

            # Move player, projectiles, and enemies
            flags = move_sprites(
                None, None, active_enemies, flags, maze_grid, game_tick
            )

            # Draw item and enemy sprites
            sprite_image_data, _ = draw_sprites(
                sprite_image_data,
                flags,
                items,
                active_enemies,
                None,
                None,
                None,
                None,
                image_boundary,
                maze_factor,
                0,
            )

            # Update screen if necessasry
            if flags.screen_change:
                flags = update_title_screen(
                    flags, screen, area_surf, fonts, maze_fidelity, sprite_image_data
                )

            # Check game tick versus actual time
            check_game_tick(game_time, game_tick)

    if flags.quit_title:
        return False
    return True
