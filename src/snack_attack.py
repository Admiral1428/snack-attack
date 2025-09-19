import ast
import pygame
import time
from settings import config as cfg
from title.intro import run_title_screen
from rect.draw import draw_maze
from asset.player import Player
from fileio.load import (
    read_csv_dict,
    read_csv_path,
)
from game.start import load_settings, load_resources, game_init, Flags
from game.input import process_input
from game.level import print_level_text, create_grid, get_level_data, set_maze_flags
from game.assets import init_items, init_enemies, set_asset_flags
from game.play import (
    reset_actors,
    determine_spawn,
    init_projectile,
    move_sprites,
    move_to_exit,
    init_blast,
    check_enemy_collision,
    remove_items,
    init_exit,
    animate_exit,
    draw_sprites,
    screen_update,
    check_game_tick,
    player_collide_pause,
    exit_level,
    end_game,
    pause_game,
)
from path.pathfind import create_graph

# Initialize pygame, screen, and starting variables
(
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
) = game_init()

# Load images, sounds, and levels
images, sounds, levels, level_index = load_resources()

# Game loop flags and variables
flags = Flags()


while flags.running:
    # Show game intro screen
    if flags.game_intro:
        flags = Flags()
        flags.running = run_title_screen(
            flags,
            fonts,
            screen,
            images,
            sounds,
            maze_width,
            maze_height,
            block_width,
            image_boundary,
        )

        # Load game settings
        maze_fidelity, maze_fidelity_index, maze_factor, controls_option = (
            load_settings()
        )

        # Scale game tick based on animation smoothness
        game_tick = cfg.GAME_TICK * maze_factor

        if flags.running:
            flags.maze_draw = True
        else:
            break
        flags.game_intro = False

    for event in pygame.event.get():
        (
            score,
            lives,
            level_index,
            key_order,
            controls_option,
            flags,
            start_time,
            pause_start,
            pause_delta,
        ) = process_input(
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
        )

    # Draw maze and instructions on screen
    if flags.maze_draw:
        maze_assets = read_csv_dict(levels[level_index].get("assets"))
        maze_metadata = read_csv_dict(levels[level_index].get("metadata"))[0]
        maze_path = read_csv_path(levels[level_index].get("path"))

        # Perform clearing of screen to remove old maze and clear up memory
        screen.fill(cfg.COLORS["black"])
        pygame.display.flip()

        # Print text to right of maze
        print_level_text(screen, levels, level_index, fonts, flags, controls_option)

        # Draw maze
        next_level_key = draw_maze(
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
            0.003,
            pygame.K_F10,
            None,
        )

        # Create maze grid based on fidelity
        maze_grid = create_grid(
            maze_width, maze_height, block_width, maze_factor, maze_path
        )

        # Create maze graph using chosen coordinates
        maze_graph, maze_graph_coords = create_graph(
            maze_path, cfg.SCALE_FACTOR, cfg.BLOCK_WIDTH
        )
        flow_field = None

        # Save subsurface for game loop re-draw
        rect_area = pygame.Rect(0, 0, cfg.WIDTH, cfg.HEIGHT)
        temp_surf = screen.subsurface(rect_area)
        area_surf = temp_surf.copy()

        # Determine level characteristics
        (
            num_corn,
            num_tomato,
            num_pumpkin,
            pixels_per_second,
            seconds_to_spawn,
            asset_coord,
        ) = get_level_data(flags, maze_factor, maze_metadata, maze_assets)

        # Set flags and variables after maze draw
        flags, level_index = set_maze_flags(next_level_key, flags, levels, level_index)
        pause_delta = 0

        # Colorize images based on sprite_colors.csv
        sprite_metadata = {}
        try:
            sprite_metadata = read_csv_dict(levels[level_index].get("sprite_colors"))[0]
        except:
            sprite_metadata["first_color"] = "blue"
            sprite_metadata["second_color"] = "red"

        colorized_images = {}
        for image in images:
            image_copy = images[image].copy()
            pixel_array = pygame.PixelArray(image_copy)
            pixel_array.replace(cfg.COLORS["blue"], cfg.COLORS["replace_blue"])
            pixel_array.replace(cfg.COLORS["red"], cfg.COLORS["replace_red"])
            pixel_array.replace(
                cfg.COLORS["replace_blue"], cfg.COLORS[sprite_metadata["first_color"]]
            )
            pixel_array.replace(
                cfg.COLORS["replace_red"], cfg.COLORS[sprite_metadata["second_color"]]
            )
            del pixel_array
            colorized_images[image] = image_copy

    # Create Sprite objects
    elif flags.create_sprites:
        # Initialize items
        items = init_items(asset_coord, colorized_images, block_width, maze_factor)
        barrier_sprites = {}

        # Determine barrier items for sightline checks
        if items:
            for key, value in items.items():
                barrier_sprites[key] = value

        # Initialize player
        player = Player(
            "player",
            colorized_images["combine"],
            asset_coord.get("S"),
            pixels_per_second,
            True,
            int(block_width / (maze_factor * 2)),
            int(block_width / maze_factor),
            None,
        )

        # Initialize enemies
        corns = init_enemies(
            "corn",
            num_corn,
            colorized_images[cfg.IMAGE_SERIES["corn"][0]],
            asset_coord.get("E"),
            pixels_per_second,
            int(0.9 * block_width / maze_factor),
            int(block_width / maze_factor),
            None,
            False,
        )
        tomatoes = init_enemies(
            "tomato",
            num_tomato,
            colorized_images[cfg.IMAGE_SERIES["tomato"][0]],
            asset_coord.get("E"),
            pixels_per_second,
            int(0.9 * block_width / maze_factor),
            int(block_width / maze_factor),
            None,
            False,
        )
        pumpkins = init_enemies(
            "pumpkin",
            num_pumpkin,
            colorized_images[cfg.IMAGE_SERIES["pumpkin"][0]],
            asset_coord.get("E"),
            pixels_per_second,
            int(0.9 * block_width / maze_factor),
            int(block_width / maze_factor),
            None,
            True,
        )

        # Update screen, set flags and variables
        start_time, projectile, blast, spawned_enemies, flags = set_asset_flags(flags)

    # Primary game loop
    elif flags.rungame and not flags.paused:
        # Clear images and Rects for screen blit
        sprite_image_data = []

        # Get alive enemies
        alive_corns = [corn for corn in corns if not corn.is_destroyed()]
        alive_tomatoes = [tomato for tomato in tomatoes if not tomato.is_destroyed()]
        alive_pumpkins = [pumpkin for pumpkin in pumpkins if not pumpkin.is_destroyed()]

        if player.can_spawn():
            start_time, spawned_enemies, projectile, blast, flow_field = reset_actors(
                flags, player, alive_corns, alive_tomatoes, alive_pumpkins, asset_coord
            )

        # Determine whether to spawn enemies based on time and their state
        alive_enemies = alive_corns + alive_tomatoes + alive_pumpkins
        spawned_enemies = determine_spawn(
            start_time, spawned_enemies, seconds_to_spawn, alive_enemies
        )
        active_enemies = [enemy for enemy in alive_enemies if enemy.can_spawn()]

        # Player movement input
        keys = pygame.key.get_pressed()
        player.control_direction(keys, key_order, controls_option)

        # Save history of direction for use with exit animation
        if player.get_direction() != (0, 0):
            direction_order.append(player.get_direction())

        # Create projectile if fire command pressed (one projectile at a time)
        if flags.fire_pressed and not (blast or projectile):
            projectile = init_projectile(
                flags,
                player,
                block_width,
                maze_factor,
                colorized_images,
                sounds,
                pixels_per_second,
                None,
            )

        # Move player, projectiles, and enemies
        if not flags.exit_found:
            flags, flow_field = move_sprites(
                player,
                projectile,
                active_enemies,
                flags,
                maze_grid,
                game_tick,
                maze_graph,
                maze_graph_coords,
                maze_factor,
                flow_field,
                barrier_sprites,
            )
        else:
            # If player not coincident with exit and moving towards it,
            # allow movement to get closer
            flags = move_to_exit(
                player,
                exit,
                direction_order,
                key_order,
                maze_grid,
                game_tick,
                flags,
                sounds,
            )

        # Remove projectiles which hit an enemy or a wall, then draw blast
        if projectile and (projectile.is_destroyed() or projectile.is_stopped()):
            # Initialize_blast
            projectile, blast, flags = init_blast(
                projectile,
                sounds,
                flags,
                colorized_images,
                block_width,
                maze_factor,
                None,
            )
        elif blast and not blast.is_animating():
            # Remove blasts which have finished animating
            blast = []
            flags.screen_change = True

        # Detect enemy collision with player and projectile
        for enemy in active_enemies:
            if flags.exit_created:
                exit_sprite = exit
            else:
                exit_sprite = None
            lives, score, spawned_enemies, start_time, flags = check_enemy_collision(
                enemy,
                player,
                projectile,
                flags,
                sounds,
                colorized_images,
                spawned_enemies,
                seconds_to_spawn,
                score,
                lives,
                start_time,
            )

        all_enemies = corns + tomatoes + pumpkins
        if not player.can_spawn():
            # Remove items if appropriate
            items, flags, score, all_destroyed, barrier_sprites = remove_items(
                all_enemies, flags, items, player, score, sounds, barrier_sprites
            )

            # If no more items, draw exit
            if not items and not flags.exit_created:
                exit, flags, lives = init_exit(
                    flags,
                    all_destroyed,
                    sounds,
                    lives,
                    colorized_images,
                    asset_coord,
                    block_width,
                    maze_factor,
                    None,
                )

        # Draw exit and animate
        if flags.exit_created:
            if "exit" not in barrier_sprites:
                enemy_collide_exit = False
                for enemy in all_enemies:
                    if enemy.collide_check(exit):
                        enemy_collide_exit = True
                        break
                if not enemy_collide_exit:
                    barrier_sprites["exit"] = exit

            sprite_image_data.append(
                exit.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
            # Proceed to next level if collision with exit
            if player.collide_check(exit):
                flags = animate_exit(flags, exit, colorized_images)
        else:
            exit = None

        # Draw item, projectile, blast, player, enemy, and exit sprites
        sprite_image_data, pause_delta = draw_sprites(
            sprite_image_data,
            flags,
            items,
            all_enemies,
            player,
            projectile,
            blast,
            exit,
            image_boundary,
            maze_factor,
            pause_delta,
        )

        # Update screen if necessasry
        if flags.screen_change:
            flags = screen_update(
                screen,
                area_surf,
                fonts,
                score,
                lives,
                controls_option,
                sprite_image_data,
                flags,
            )

        # Check game tick versus actual time
        check_game_tick(game_time, game_tick)

        # Brief pause once the player has collided with an enemy
        if player.can_spawn():
            player_collide_pause(lives, sounds, game_time)

        # Change to the next level if door closing animation finished
        if flags.exit_closing and not exit.is_animating():
            flags, level_index = exit_level(level_index, levels, flags)

        # Restart game if lives expended
        if lives < 0:
            flags, level_index, score, lives = end_game(flags, fonts, screen, sounds)

    elif flags.paused:
        flags = pause_game(flags, fonts, screen)

# Quit
pygame.quit()
