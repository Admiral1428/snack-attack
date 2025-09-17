import ast
import pygame
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
        )

        # Create maze grid based on fidelity
        maze_grid = create_grid(
            maze_width, maze_height, block_width, maze_factor, maze_path
        )

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

    # Create Sprite objects
    elif flags.create_sprites:
        # Initialize items
        items = init_items(asset_coord, images, block_width, maze_factor)

        # Initialize player
        player = Player(
            "player",
            images["combine"],
            asset_coord.get("S"),
            pixels_per_second,
            True,
            int(block_width / (maze_factor * 2)),
            int(block_width / maze_factor),
        )

        # Initialize enemies
        corns = init_enemies(
            "corn",
            num_corn,
            images[cfg.IMAGE_SERIES["corn"][0]],
            asset_coord.get("E"),
            pixels_per_second,
            int((3 / 4) * block_width / maze_factor),
            int(block_width / maze_factor),
            False,
        )
        tomatoes = init_enemies(
            "tomato",
            num_tomato,
            images[cfg.IMAGE_SERIES["tomato"][0]],
            asset_coord.get("E"),
            pixels_per_second,
            int((3 / 4) * block_width / maze_factor),
            int(block_width / maze_factor),
            False,
        )
        pumpkins = init_enemies(
            "pumpkin",
            num_pumpkin,
            images[cfg.IMAGE_SERIES["pumpkin"][0]],
            asset_coord.get("E"),
            pixels_per_second,
            int((3 / 4) * block_width / maze_factor),
            int(block_width / maze_factor),
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
            start_time, spawned_enemies, projectile, blast = reset_actors(
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
                images,
                sounds,
                pixels_per_second,
            )

        # Move player, projectiles, and enemies
        if not flags.exit_found:
            flags = move_sprites(
                player, projectile, active_enemies, flags, maze_grid, game_tick
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
                projectile, sounds, flags, images, block_width, maze_factor
            )
        elif blast and not blast.is_animating():
            # Remove blasts which have finished animating
            blast = []
            flags.screen_change = True

        # Detect enemy collision with player and projectile
        for enemy in active_enemies:
            lives, score, spawned_enemies, start_time, flags = check_enemy_collision(
                enemy,
                player,
                projectile,
                flags,
                sounds,
                images,
                spawned_enemies,
                seconds_to_spawn,
                score,
                lives,
                start_time,
            )

        all_enemies = corns + tomatoes + pumpkins
        if not player.can_spawn():
            # Remove items if appropriate
            items, flags, score, all_destroyed = remove_items(
                all_enemies, flags, items, player, score, sounds
            )

            # If no more items, draw exit
            if not items and not flags.exit_created:
                exit, flags, lives = init_exit(
                    flags,
                    all_destroyed,
                    sounds,
                    lives,
                    images,
                    asset_coord,
                    block_width,
                    maze_factor,
                )

        # Draw exit and animate
        if flags.exit_created:
            sprite_image_data.append(
                exit.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
            # Proceed to next level if collision with exit
            if player.collide_check(exit):
                flags = animate_exit(flags, exit, images)

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
