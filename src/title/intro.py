import os
import ast
import time
import pygame
from rect.draw import draw_maze
from asset.sprite import Sprite
from asset.player import Player
from asset.enemy import Enemy
from grid.utils import invert_maze_to_grid
from utils.exceptions import CustomError
from fileio.export import export_settings, move_one_file
from fileio.load import (
    get_levels,
    read_csv_dict,
    read_csv_path,
)


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

    # Level speed definitions (coordinates per game tick for moving sprites)
    level_speeds = {
        "slow": int(144 / maze_factor),
        "medium": int(180 / maze_factor),
        "fast": int(240 / maze_factor),
        "frantic": (360 / maze_factor),
    }

    # Set game tick speed to such that movement calculation is no more than one
    # coordinate per tick, and defined speeds have meaningful changes to gameplay
    # e.g., ticks needed to move one coordinate:
    # slow:     144 * 5 = 720
    # medium:   180 * 4 = 720
    # fast:     240 * 3 = 720
    # frantic:  360 * 2 = 720
    game_tick = 1 / (720 / maze_factor)

    return level_speeds, game_tick, maze_grid


def run_title_screen(screen, images, item_image_defs, spawn_speeds, maze_fidelity):

    # Use lucidaconsole text for retro look
    font_large = pygame.font.SysFont("lucidaconsole", 80)
    font_medium = pygame.font.SysFont("lucidaconsole", 36)
    font = pygame.font.SysFont("lucidaconsole", 26)

    # Define maze fidelity options
    maze_fidelity_opts = ["coarse", "normal", "fine"]
    maze_fidelity_factors = [4, 2, 1]

    maze_fidelity_index = None
    maze_factor = None
    for index, opt in enumerate(maze_fidelity_opts):
        if maze_fidelity == opt:
            maze_fidelity_index = index
            maze_factor = maze_fidelity_factors[index]
    if maze_fidelity_index == None or maze_factor == None:
        raise CustomError("Maze fidelity not a valid option.")

    # Window dimensions
    width, height = (1600, 900)

    # Define maze properties
    maze_width = 256
    maze_height = 192
    block_width = 12
    min_block_spacing = 4
    draw_image_x = 20
    draw_image_y = 20
    image_boundary = 4

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
    maze_colors = [
        teal,
        yellow,
        orange,
        green,
        dkgreen,
        purple,
        magenta,
        red,
        blue,
        gray,
    ]

    # Scale variables
    scale_factor = 4
    maze_width *= scale_factor
    maze_height *= scale_factor
    block_width *= scale_factor
    min_block_spacing *= scale_factor
    image_boundary *= scale_factor

    # Fill background with black color
    screen.fill(black)

    # Display title text
    title_text = "Snack Attack"
    author_text = "Programmed in Python by Tim Roble"
    version_text = "Version 1.0.0, September 2025"
    proceed_text = "Press Spacebar to Start Game"

    # Display animation information
    info_strings = [
        "Press F5 to cycle",
        "animation smoothness",
        "",
        "Current option: ",
        "",
        "",
        "'normal' or 'fine' options",
        "may be laggy on slower",
        "PCs. Sprites should",
        "maintain same speed when",
        "toggling. If they appear",
        "slower, revert to a more",
        "coarse setting.",
    ]

    # Get levels and their supporting file paths
    level_dir = "../assets/title/"
    levels = get_levels(level_dir)
    level_index = 0

    # Update initial display
    pygame.display.update()

    # Game loop
    maze_draw = True
    create_sprites = False
    rungame = False
    f5_pressed = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    f5_pressed = True
                if event.key == pygame.K_SPACE:
                    running = False
                    return True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_F5 and f5_pressed:
                    # Cycle to next maze fidelity
                    if maze_fidelity_index >= len(maze_fidelity_opts) - 1:
                        maze_fidelity_index = 0
                    else:
                        maze_fidelity_index += 1
                    maze_factor = maze_fidelity_factors[maze_fidelity_index]
                    maze_fidelity = maze_fidelity_opts[maze_fidelity_index]

                    # Load then re-export settings file
                    settings = read_csv_dict("../assets/settings/config.csv")
                    for key, value in settings[0].items():
                        if key == "maze_fidelity":
                            settings[0][key] = maze_fidelity
                    export_settings(settings[0])
                    move_one_file("config.csv", ".", "../assets/settings/")

                    # Get variables which are affected by maze fidelity
                    level_speeds, game_tick, maze_grid = perform_factoring(
                        maze_width, maze_height, block_width, maze_path, maze_factor
                    )
                    create_sprites = True
                    rungame = False
                    f5_pressed = False

        # Draw maze and instructions on screen
        if maze_draw:
            maze_assets = read_csv_dict(levels[level_index].get("assets"))
            maze_metadata = read_csv_dict(levels[level_index].get("metadata"))[0]
            maze_path = read_csv_path(levels[level_index].get("path"))

            # Perform clearing of screen to remove old maze and clear up memory
            screen.fill(black)
            pygame.display.flip()

            # Print animation information
            for row, text_line in enumerate(info_strings):
                if row == 4:
                    text_surface = font.render(maze_fidelity, True, yellow)
                else:
                    text_surface = font.render(text_line, True, white)
                screen.blit(text_surface, (1140, 50 + row * 50))

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
                0,
                None,
            )

            # Get variables which are affected by maze fidelity
            level_speeds, game_tick, maze_grid = perform_factoring(
                maze_width, maze_height, block_width, maze_path, maze_factor
            )

            # Display title text
            # title_text = "Snack Attack"
            # author_text = "Programmed in Python by Tim Roble"
            # version_text = "Version 1.0.0, September 2025"
            # proceed_text = "Press Spacebar to Start Game"

            text_surface = font_large.render(title_text, True, white)
            screen.blit(text_surface, (275, 200))
            text_surface = font.render(author_text, True, white)
            screen.blit(text_surface, (300, 320))
            text_surface = font.render(version_text, True, white)
            screen.blit(text_surface, (325, 370))
            text_surface = font_medium.render(proceed_text, True, white)
            screen.blit(text_surface, (260, 450))

            # Save subsurface for game loop re-draw
            rect_area = pygame.Rect(0, 0, width, height)
            temp_surf = screen.subsurface(rect_area)
            area_surf = temp_surf.copy()

            # save relevant metadata
            level_speed = maze_metadata.get("level_speed")
            num_corn = ast.literal_eval(maze_metadata.get("corn_quantity"))
            num_tomato = ast.literal_eval(maze_metadata.get("tomato_quantity"))
            num_pumpkin = ast.literal_eval(maze_metadata.get("pumpkin_quantity"))

            # Assign appropriate enemy respawn speed, defaulting to slow
            if level_speed in spawn_speeds.keys():
                seconds_to_spawn = spawn_speeds.get(level_speed)
            else:
                seconds_to_spawn = spawn_speeds.get("slow")

            # Set flags
            create_sprites = True
            maze_draw = False

        # Create Sprite objects
        if create_sprites:
            # Assign appropriate sprite speed, defaulting to slow
            if level_speed in level_speeds.keys():
                pixels_per_second = level_speeds.get(level_speed)
            else:
                pixels_per_second = level_speeds.get("slow")

            # Asset coordinates
            asset_coord = {}
            for dict in maze_assets:
                asset_coord[dict.get("letter")] = ast.literal_eval(dict.get("location"))
                # Scale based on maze fidelity
                asset_coord[dict.get("letter")] = (
                    int(asset_coord[dict.get("letter")][0] / maze_factor),
                    int(asset_coord[dict.get("letter")][1] / maze_factor),
                )

            # Initialize items
            items = {}
            for key, value in asset_coord.items():
                if key in item_image_defs:
                    items[key] = Sprite(
                        key,
                        images[item_image_defs.get(key)],
                        asset_coord.get(key),
                        0,
                        False,
                        int(block_width / (maze_factor * 6)),
                        int(block_width / maze_factor),
                    )

            # Initialize enemies
            corns = []
            tomatoes = []
            pumpkins = []
            for i in range(num_corn):
                corns.append(
                    Enemy(
                        "corn",
                        images["corn"],
                        asset_coord.get("E"),
                        pixels_per_second,
                        False,
                        int(block_width / (maze_factor * 2)),
                        int(block_width / maze_factor),
                    )
                )
            for i in range(num_tomato):
                tomatoes.append(
                    Enemy(
                        "tomato",
                        images["tomato"],
                        asset_coord.get("E"),
                        pixels_per_second,
                        False,
                        int(block_width / (maze_factor * 2)),
                        int(block_width / maze_factor),
                    )
                )
            for i in range(num_pumpkin):
                pumpkins.append(
                    Enemy(
                        "pumpkin",
                        images["pumpkin"],
                        asset_coord.get("E"),
                        pixels_per_second,
                        False,
                        int(block_width / (maze_factor * 2)),
                        int(block_width / maze_factor),
                    )
                )

            # Update screen, set flags and variables
            game_time = pygame.time.Clock()
            start_time = time.time()
            rungame = True
            screen_change = True
            create_sprites = False
            spawned_enemies = 0
        # Primary game loop
        elif rungame:
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
            respawn_time = time.time() - start_time
            if respawn_time >= (spawned_enemies + 1) * seconds_to_spawn:
                spawned_enemies += 1
                if spawned_enemies <= len(alive_corns):
                    index = spawned_enemies - 1
                    if not alive_corns[index].is_destroyed():
                        alive_corns[index].toggle_spawn()
                elif spawned_enemies - len(alive_corns) <= len(alive_tomatoes):
                    index = spawned_enemies - len(alive_corns) - 1
                    if not alive_tomatoes[index].is_destroyed():
                        alive_tomatoes[index].toggle_spawn()
                elif spawned_enemies - len(alive_corns) - len(alive_tomatoes) <= len(
                    alive_pumpkins
                ):
                    index = spawned_enemies - len(alive_corns) - len(alive_tomatoes) - 1
                    if not alive_pumpkins[index].is_destroyed():
                        alive_pumpkins[index].toggle_spawn()

            active_corns = [corn for corn in alive_corns if corn.can_spawn()]
            active_tomatoes = [
                tomato for tomato in alive_tomatoes if tomato.can_spawn()
            ]
            active_pumpkins = [
                pumpkin for pumpkin in alive_pumpkins if pumpkin.can_spawn()
            ]

            # Move player, projectiles, and enemies
            corn_move = False
            tomato_move = False
            pumpkin_move = False

            for corn in active_corns:
                corn.set_navigate_direction(None, maze_grid, game_tick)
                corn_move = corn.perform_move(maze_grid, game_tick)
            for tomato in active_tomatoes:
                tomato.set_navigate_direction(None, maze_grid, game_tick)
                tomato_move = tomato.perform_move(maze_grid, game_tick)
            for pumpkin in active_pumpkins:
                pumpkin.set_navigate_direction(None, maze_grid, game_tick)
                pumpkin_move = pumpkin.perform_move(maze_grid, game_tick)

            if any([corn_move, tomato_move, pumpkin_move]):
                screen_change = True

            # Draw item and enemy sprites
            [
                sprite_image_data.append(
                    items[item].draw(
                        draw_image_x, draw_image_y, image_boundary, maze_factor
                    )
                )
                for item in items
            ]
            [
                sprite_image_data.append(
                    corn.draw(draw_image_x, draw_image_y, image_boundary, maze_factor)
                )
                for corn in corns
                if corn.can_spawn()
            ]
            [
                sprite_image_data.append(
                    tomato.draw(draw_image_x, draw_image_y, image_boundary, maze_factor)
                )
                for tomato in tomatoes
                if tomato.can_spawn()
            ]
            [
                sprite_image_data.append(
                    pumpkin.draw(
                        draw_image_x, draw_image_y, image_boundary, maze_factor
                    )
                )
                for pumpkin in pumpkins
                if pumpkin.can_spawn()
            ]

            # Update screen if necessasry
            if screen_change:
                # Clear screen and re-draw background
                screen.fill(black)
                screen.blit(area_surf, (0, 0))

                black_rect = pygame.Rect(1130, 240, 300, 50)
                screen.fill(black, black_rect)
                # Print animation information
                # Print animation information
                for row, text_line in enumerate(info_strings):
                    if row == 4:
                        text_surface = font.render(maze_fidelity, True, yellow)
                    else:
                        text_surface = font.render(text_line, True, white)
                    screen.blit(text_surface, (1140, 50 + row * 50))

                # Print sprites
                for item in sprite_image_data:
                    screen.blit(item[0], item[1])

                pygame.display.flip()
                screen_change = False

            # If game calculated tick faster than realtime clock, introduce
            # delay to ensure game doesn't run too fast. Otherwise, allow game
            # to run at the cadence of calculated tick, which may result in game
            # running slower than tick rate on slower PCs.
            game_dt = game_time.tick() / 1000
            if game_dt - game_tick < 0:
                time.sleep(game_tick - game_dt)
                game_time.tick()
