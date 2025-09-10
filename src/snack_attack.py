import os
import ast
import time
import pygame
from settings import config as cfg
from collections import deque
from title.intro import run_title_screen
from utils.exceptions import CustomError
from rect.draw import draw_maze
from asset.sprite import Sprite
from asset.player import Player
from asset.enemy import Enemy
from grid.utils import invert_maze_to_grid
from fileio.export import export_settings, move_one_file
from fileio.load import (
    import_image_dir,
    import_sound_dir,
    get_levels,
    read_csv_dict,
    read_csv_path,
)

# Clear terminal (Windows syntax)
if os.name == "nt":
    os.system("cls")

# Initialize pygame modules
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Use lucidaconsole text for retro look
font = pygame.font.SysFont("lucidaconsole", 26)

# Load game settings
maze_fidelity = ""
controls_option = None
settings = read_csv_dict(cfg.DIRS["settings"] + cfg.FILES["settings"])
for dict in settings:
    for key, value in dict.items():
        if key == "maze_fidelity":
            maze_fidelity = value
        elif key == "controls_option":
            controls_option = ast.literal_eval(value)

if controls_option not in range(4):
    raise CustomError(cfg.ERROR_STRINGS["controls"])

# Get maze fidelity options
maze_fidelity_index = None
maze_factor = None
for index, opt in enumerate(cfg.MAZE_FIDELITY_OPTS):
    if maze_fidelity == opt:
        maze_fidelity_index = index
        maze_factor = cfg.MAZE_FIDELITY_FACTORS[index]
if maze_fidelity_index == None or maze_factor == None:
    raise CustomError(cfg.ERROR_STRINGS["maze_fidelity"])

# Dimensions for window
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), vsync=1)

# Set window title
pygame.display.set_caption(cfg.TITLE_TEXT)

# Scale variables
maze_width = cfg.MAZE_WIDTH * cfg.SCALE_FACTOR
maze_height = cfg.MAZE_HEIGHT * cfg.SCALE_FACTOR
block_width = cfg.BLOCK_WIDTH * cfg.SCALE_FACTOR
image_boundary = cfg.IMAGE_BOUNDARY * cfg.SCALE_FACTOR

# Fill background with black color
screen.fill(cfg.COLORS["black"])

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

# Get sound effects
sounds = import_sound_dir(cfg.DIRS["sounds"])

# Get levels and their supporting file paths
level_dir = cfg.DIRS["levels"]
levels = get_levels(level_dir)

if not levels:
    raise CustomError(f"Could not load any level folders at {level_dir}")
else:
    level_index = 0

# Update initial display
pygame.display.update()

# Game loop
game_intro = True
maze_draw = False
create_sprites = False
rungame = False
paused = False
f10_pressed = False
escape_pressed = False
fire_pressed = False
need_pause_text = False
reached_last_level = False
key_order = deque(maxlen=2)
direction_order = deque(maxlen=1)
score = 0
lives = cfg.LIVES_DEFAULT
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and not game_intro:
            if event.key == pygame.K_F10:
                f10_pressed = True
            if event.key == pygame.K_ESCAPE:
                escape_pressed = True
            if event.key == pygame.K_F1:
                screen_change = True
                key_order = deque(maxlen=2)
                if controls_option == len(cfg.CONTROLS_TEXT) - 1:
                    controls_option = 0
                else:
                    controls_option += 1
                f1_pressed = True

                # Load then re-export settings file
                settings = read_csv_dict(cfg.DIRS["settings"] + cfg.FILES["settings"])
                for key, value in settings[0].items():
                    if key == "controls_option":
                        settings[0][key] = controls_option
                export_settings(settings[0])
                move_one_file(cfg.FILES["settings"], ".", cfg.DIRS["settings"])
            if event.key == pygame.K_PAUSE:
                # Adjust game loop start timer based on pause behavior
                if not paused:
                    pause_start = time.time()
                else:
                    pause_end = time.time()
                    start_time += pause_end - pause_start

                # Pause or unpause, and reset flag for printing text
                paused = not paused
                need_pause_text = True

                # Update game clock at end of pause
                game_time.tick()
            if (
                controls_option == 0
                and event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]
            ) or (
                controls_option == 1
                and event.key in [pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l]
            ):
                key_order.append(event.key)
            if (controls_option in [0, 2] and event.key == pygame.K_RETURN) or (
                controls_option in [1, 3] and event.key == pygame.K_f
            ):
                fire_pressed = True
        elif event.type == pygame.KEYUP and not game_intro:
            if event.key == pygame.K_F10 and f10_pressed:
                # Skip to next level
                if level_index >= len(levels) - 1:
                    level_index = 0
                    reached_last_level = True
                else:
                    level_index += 1
                maze_draw = True
                f10_pressed = False
            if event.key == pygame.K_ESCAPE and escape_pressed:
                escape_pressed = False
                for row, text_line in enumerate(cfg.ENDGAME_STRINGS):
                    text_surface = font.render(text_line, True, cfg.COLORS["yellow"])
                    locs = cfg.TEXT_LOC["endgame"]
                    screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))
                level_index = 0
                reached_last_level = False
                score = 0
                lives = cfg.LIVES_DEFAULT
                game_intro = True
                sounds["endgame"].play()
                pygame.display.flip()
                time.sleep(cfg.PAUSES["endgame"])
            if event.key == pygame.K_F1 and f1_pressed:
                f1_pressed = False
            if (
                (controls_option in [0, 2] and event.key == pygame.K_RETURN)
                or (controls_option in [1, 3] and event.key == pygame.K_f)
                and fire_pressed
            ):
                fire_pressed = False

    # Show game intro screen
    if game_intro:
        sounds["intro"].play()
        running = run_title_screen(screen, images, maze_fidelity)

        # Set variables once title exited
        # Load game settings
        settings = read_csv_dict(cfg.DIRS["settings"] + cfg.FILES["settings"])
        for dict in settings:
            for key, value in dict.items():
                if key == "maze_fidelity":
                    maze_fidelity = value
        if maze_fidelity == "fine":
            maze_fidelity_index = 2
            maze_factor = 1
        elif maze_fidelity == "normal":
            maze_fidelity_index = 1
            maze_factor = 2
        else:
            maze_fidelity_index = 0
            maze_factor = 4

        # Scale game tick based on animation smoothness
        game_tick = cfg.GAME_TICK * maze_factor

        if running:
            maze_draw = True
        game_intro = False
    # Draw maze and instructions on screen
    if maze_draw:
        maze_assets = read_csv_dict(levels[level_index].get("assets"))
        maze_metadata = read_csv_dict(levels[level_index].get("metadata"))[0]
        maze_path = read_csv_path(levels[level_index].get("path"))

        # Perform clearing of screen to remove old maze and clear up memory
        screen.fill(cfg.COLORS["black"])
        pygame.display.flip()

        # Print level info
        for row, text_line in enumerate(cfg.INFO_STRINGS):
            text_surface = font.render(text_line, True, cfg.COLORS["white"])
            locs = cfg.TEXT_LOC["level_score_lives"]
            screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))
        # Trim level name
        folder_name = levels[level_index].get("folder")
        if len(folder_name) > 8:
            folder_name = folder_name[:8] + "..."
        if reached_last_level:
            text_surface = font.render(
                folder_name + " (reprise)", True, cfg.COLORS["red"]
            )
        else:
            text_surface = font.render(folder_name, True, cfg.COLORS["white"])
        locs = cfg.TEXT_LOC["level_value"]
        screen.blit(text_surface, (locs[0], locs[1]))

        # Print instructions
        for row, text_line in enumerate(cfg.HOW_TO_STRINGS):
            text_surface = font.render(text_line, True, cfg.COLORS["white"])
            locs = cfg.TEXT_LOC["instructions"]
            screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))

        # Print controls
        for row, text_line in enumerate(cfg.CONTROLS_TEXT[controls_option]):
            text_surface = font.render(text_line, True, cfg.COLORS["white"])
            locs = cfg.TEXT_LOC["controls"]
            screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))

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

        # Scale inputs prior to creating maze grid, based on chosen fidelity
        maze_width_scaled = int(maze_width / maze_factor)
        maze_height_scaled = int(maze_height / maze_factor)
        block_width_scaled = int(block_width / maze_factor)
        coords_scaled = []
        for coord in maze_path:
            coords_scaled.append(
                (int(coord[0] / maze_factor), int(coord[1] / maze_factor))
            )

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

        # Save subsurface for game loop re-draw
        rect_area = pygame.Rect(0, 0, cfg.WIDTH, cfg.HEIGHT)
        temp_surf = screen.subsurface(rect_area)
        area_surf = temp_surf.copy()

        # Hardcode speed and enemy quantity if repeated levels
        if reached_last_level:
            level_speed = "frantic"
            num_corn = 2
            num_tomato = 4
            num_pumpkin = 4
        # Otherwise save relevant metadata
        else:
            level_speed = maze_metadata.get("level_speed")
            num_corn = ast.literal_eval(maze_metadata.get("corn_quantity"))
            num_tomato = ast.literal_eval(maze_metadata.get("tomato_quantity"))
            num_pumpkin = ast.literal_eval(maze_metadata.get("pumpkin_quantity"))

        # Assign appropriate sprite speed, defaulting to slow,
        # while accounting for animation smoothness
        if level_speed in cfg.LEVEL_SPEEDS.keys():
            pixels_per_second = int(cfg.LEVEL_SPEEDS.get(level_speed) / maze_factor)
        else:
            pixels_per_second = int(cfg.LEVEL_SPEEDS.get("slow") / maze_factor)

        # Assign appropriate enemy respawn speed, defaulting to slow
        if level_speed in cfg.SPAWN_SPEEDS.keys():
            seconds_to_spawn = cfg.SPAWN_SPEEDS.get(level_speed)
        else:
            seconds_to_spawn = cfg.SPAWN_SPEEDS.get("slow")

        # Save maze asset coordinates into a single dictionary and check validity
        # of asset coordinates with error handling
        asset_coord = {}
        for dict in maze_assets:
            asset_coord[dict.get("letter")] = ast.literal_eval(dict.get("location"))
            # Scale based on maze fidelity
            asset_coord[dict.get("letter")] = (
                int(asset_coord[dict.get("letter")][0] / maze_factor),
                int(asset_coord[dict.get("letter")][1] / maze_factor),
            )
        if (
            len(asset_coord) != len(cfg.ALLOWABLE_LETTERS)
            or any(
                not isinstance(value, tuple) or not value
                for value in asset_coord.values()
            )
            or any(key not in cfg.ALLOWABLE_LETTERS for key in asset_coord.keys())
        ):
            raise CustomError(
                cfg.ERROR_STRINGS["asset_letter"] + str(cfg.ALLOWABLE_LETTERS)
            )

        # Skip to next level if pressed during draw
        if next_level_key:
            if level_index >= len(levels) - 1:
                level_index = 0
                reached_last_level = True
            else:
                level_index += 1
            maze_draw = True
            f10_pressed = False
        else:
            create_sprites = True
            exit_created = False
            exit_found = False
            exit_opening = False
            exit_closing = False
            maze_draw = False

    # Create Sprite objects
    elif create_sprites:
        # Initialize items
        items = {}
        for key, value in asset_coord.items():
            if key in cfg.ITEM_IMAGE_DEFS:
                items[key] = Sprite(
                    key,
                    images[cfg.ITEM_IMAGE_DEFS.get(key)],
                    asset_coord.get(key),
                    0,
                    False,
                    int(block_width / (maze_factor * 6)),
                    int(block_width / maze_factor),
                )

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
        corns = []
        tomatoes = []
        pumpkins = []
        for i in range(num_corn):
            corns.append(
                Enemy(
                    "corn",
                    images[cfg.IMAGE_SERIES["corn"][0]],
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
                    images[cfg.IMAGE_SERIES["tomato"][0]],
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
                    images[cfg.IMAGE_SERIES["pumpkin"][0]],
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
        projectile = []
        blast = []
        rungame = True
        exit_found = False
        screen_change = True
        create_sprites = False
        exit_sound_played = False
        spawned_enemies = 0

    # Primary game loop
    elif rungame and not paused:
        # Clear images and Rects for screen blit
        sprite_image_data = []

        # Get alive enemies
        alive_corns = [corn for corn in corns if not corn.is_destroyed()]
        alive_tomatoes = [tomato for tomato in tomatoes if not tomato.is_destroyed()]
        alive_pumpkins = [pumpkin for pumpkin in pumpkins if not pumpkin.is_destroyed()]

        # Move player and enemies to respawn if player collided with enemy
        if player.can_spawn():
            screen_change = True
            player.reset(asset_coord.get("R")[0], asset_coord.get("R")[1])
            player.toggle_spawn()
            start_time = time.time()
            spawned_enemies = 0
            for corn in alive_corns:
                corn.reset(asset_coord.get("E")[0], asset_coord.get("E")[1])
                if corn.can_spawn():
                    corn.toggle_spawn()
            for tomato in alive_tomatoes:
                tomato.reset(asset_coord.get("E")[0], asset_coord.get("E")[1])
                if tomato.can_spawn():
                    tomato.toggle_spawn()
            for pumpkin in alive_pumpkins:
                pumpkin.reset(asset_coord.get("E")[0], asset_coord.get("E")[1])
                if pumpkin.can_spawn():
                    pumpkin.toggle_spawn()
                    pumpkin.reset_image()
            projectile = []
            blast = []

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
        active_tomatoes = [tomato for tomato in alive_tomatoes if tomato.can_spawn()]
        active_pumpkins = [pumpkin for pumpkin in alive_pumpkins if pumpkin.can_spawn()]

        # Player movement input
        keys = pygame.key.get_pressed()
        player.control_direction(keys, key_order, controls_option)

        # Save history of direction for use with exit animation
        if player.get_direction() != (0, 0):
            direction_order.append(player.get_direction())

        # Player fire command (only one projectile at a time)
        if fire_pressed and not (blast or projectile):
            screen_change = True
            fire_pressed = False
            projectile_direction = (1, 0)
            if player.direction != (0, 0):
                projectile_direction = player.direction
            # Initialize projectile at front end of player
            player_location = player.get_center_position()
            projectile_location = (
                player_location[0]
                + projectile_direction[0] * int(block_width / (maze_factor * 4)),
                player_location[1]
                + projectile_direction[1] * int(block_width / (maze_factor * 4)),
            )
            projectile = Sprite(
                "projectile",
                images["projectile"],
                projectile_location,
                pixels_per_second * 2,
                True,
                int(block_width / (maze_factor * 4)),
                int(block_width / (maze_factor * 4)),
            )
            projectile.set_desired_direction(
                projectile_direction[0], projectile_direction[1]
            )
            proj_delta_dist = 0
            sounds["proj_fire"].play()

        # Move player, projectiles, and enemies
        if not exit_found:
            player_move = False
            proj_move = False
            corn_move = False
            tomato_move = False
            pumpkin_move = False

            player_move = player.perform_move(maze_grid, game_tick)
            if projectile:
                proj_move = projectile.perform_move(maze_grid, game_tick)
            for corn in active_corns:
                corn.set_navigate_direction(player, maze_grid, game_tick)
                corn_move = corn.perform_move(maze_grid, game_tick)
            for tomato in active_tomatoes:
                tomato.set_navigate_direction(player, maze_grid, game_tick)
                tomato_move = tomato.perform_move(maze_grid, game_tick)
            for pumpkin in active_pumpkins:
                pumpkin.set_navigate_direction(player, maze_grid, game_tick)
                pumpkin_move = pumpkin.perform_move(maze_grid, game_tick)

            if any([player_move, proj_move, corn_move, tomato_move, pumpkin_move]):
                screen_change = True
        else:
            # If player not coincident with exit and moving towards it,
            # allow movement to get closer
            player_to_exit = (
                exit.center_position[0] - player.center_position[0],
                exit.center_position[1] - player.center_position[1],
            )
            if (
                (player_to_exit[0] > 0 and player.direction[0] > 0)
                or (player_to_exit[0] < 0 and player.direction[0] < 0)
                or (player_to_exit[1] > 0 and player.direction[1] > 0)
                or (player_to_exit[1] < 0 and player.direction[1] < 0)
            ):
                if direction_order and key_order:
                    player.set_desired_direction(
                        direction_order[-1][0], direction_order[-1][1]
                    )
                player.perform_move(maze_grid, game_tick)
                screen_change = True
            else:
                if not exit_sound_played:
                    sounds["exit"].play()
                    exit_sound_played = True

        # Remove projectiles which hit an enemy or a wall, then draw blast
        if projectile and (projectile.is_destroyed() or projectile.is_stopped()):
            if projectile.is_stopped():
                sounds["proj_hit_wall"].play()
            screen_change = True
            projectile_location = projectile.get_center_position()
            projectile = []
            blast = Sprite(
                "blast",
                images[cfg.IMAGE_SERIES["blast"][0]],
                projectile_location,
                0,
                False,
                int(block_width / (maze_factor * 4)),
                int(block_width / (maze_factor * 4)),
            )
            blast.animate(images, cfg.IMAGE_SERIES["blast"][1:], cfg.DELAYS["blast"])
        elif blast and not blast.is_animating():
            # Remove blasts which have finished animating
            blast = []
            screen_change = True

        # Detect corn collision with player and projectile
        for corn in active_corns:
            if player.collide_check(corn):
                lives -= 1
                player.toggle_spawn()
            elif (
                projectile
                and not projectile.is_destroyed()
                and projectile.collide_check(corn)
            ):
                screen_change = True
                score += cfg.SCORES["corn"]
                projectile.toggle_destroy()
                corn.toggle_destroy()
                sounds["proj_hit_enemy"].play()
                spawned_enemies -= 1
                start_time += seconds_to_spawn
                corn.animate(images, cfg.IMAGE_SERIES["corn"][1:], cfg.DELAYS["corn"])

        # Detect tomato collision with player and projectile
        if not player.can_spawn():
            for tomato in active_tomatoes:
                if player.collide_check(tomato) and not tomato.is_destroyed():
                    lives -= 1
                    player.toggle_spawn()
                elif (
                    projectile
                    and not projectile.is_destroyed()
                    and projectile.collide_check(tomato)
                ):
                    screen_change = True
                    score += cfg.SCORES["tomato"]
                    projectile.toggle_destroy()
                    tomato.toggle_destroy()
                    sounds["proj_hit_enemy"].play()
                    spawned_enemies -= 1
                    start_time += seconds_to_spawn
                    tomato.animate(
                        images, cfg.IMAGE_SERIES["tomato"][1:], cfg.DELAYS["tomato"]
                    )

        # Detect pumpkin collision with player and projectile
        if not player.can_spawn():
            for pumpkin in active_pumpkins:
                if player.collide_check(pumpkin):
                    lives -= 1
                    player.toggle_spawn()
                elif (
                    projectile
                    and not projectile.is_destroyed()
                    and projectile.collide_check(pumpkin)
                ):
                    screen_change = True
                    projectile.toggle_destroy()
                    sounds["proj_hit_pumpkin"].play()
                    pumpkin.animate(
                        images, cfg.IMAGE_SERIES["pumpkin"][1:], cfg.DELAYS["pumpkin"]
                    )

        if not player.can_spawn():
            # If no more enemies, remove remaining items
            delete_items = []
            enemy_collection = corns + tomatoes + pumpkins
            all_destroyed = all(enemy.is_destroyed() for enemy in enemy_collection)
            if all_destroyed:
                screen_change = True
                for item in items:
                    delete_items.append(item)
            else:
                # Detect item collision and delete those items
                for item in items:
                    if player.collide_check(items[item]):
                        screen_change = True
                        score += cfg.SCORES["item"]
                        delete_items.append(item)
                        if len(items) > 1:
                            sounds["item"].play()

            # Delete appropriate items
            for item in delete_items:
                del items[item]

            # If no more items, draw exit
            if not items and not exit_created:
                screen_change = True
                # Reward player with extra life if all items collected
                if not all_destroyed:
                    sounds["extra_life"].play()
                    lives += 1
                exit = Sprite(
                    "H",
                    images["door"],
                    asset_coord.get("H"),
                    0,
                    False,
                    int(block_width / (maze_factor * 12)),
                    block_width,
                )
                exit_created = True

        # Draw exit and animate
        if exit_created:
            sprite_image_data.append(
                exit.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
            # Proceed to next level if collision with exit
            if player.collide_check(exit):
                screen_change = True
                exit_found = True
                if not exit_opening:
                    # Animate door opening
                    exit.animate(
                        images, cfg.IMAGE_SERIES["door"][1:], cfg.DELAYS["door"]
                    )
                    exit_opening = True
                elif exit_opening and not exit_closing and not exit.is_animating():
                    # Animate door closing
                    exit.animate(
                        images, cfg.IMAGE_SERIES["door"][:0:-1], cfg.DELAYS["door"]
                    )
                    exit_closing = True

        # Draw item, projectile, blast, player, and enemy sprites
        [
            sprite_image_data.append(
                items[item].draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
            for item in items
        ]
        if projectile:
            sprite_image_data.append(
                projectile.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
        [
            sprite_image_data.append(
                corn.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
            for corn in corns
            if corn.can_spawn()
        ]
        [
            sprite_image_data.append(
                tomato.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
            for tomato in tomatoes
            if tomato.can_spawn()
        ]
        [
            sprite_image_data.append(
                pumpkin.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
            for pumpkin in pumpkins
            if pumpkin.can_spawn()
        ]
        if blast:
            sprite_image_data.append(
                blast.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )
        sprite_image_data.append(
            player.draw(cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor)
        )

        # Draw exit again overtop player if door closing
        if exit_closing:
            sprite_image_data.append(
                exit.draw(
                    cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor
                )
            )

        # Update screen if necessasry
        if screen_change:
            # Clear screen and re-draw background
            screen.fill(cfg.COLORS["black"])
            screen.blit(area_surf, (0, 0))

            # Print controls
            black_rect = pygame.Rect(cfg.BLACK_RECTS["controls"])
            screen.fill(cfg.COLORS["black"], black_rect)
            for row, text_line in enumerate(cfg.CONTROLS_TEXT[controls_option]):
                text_surface = font.render(text_line, True, cfg.COLORS["white"])
                locs = cfg.TEXT_LOC["controls"]
                screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))

            # Print score
            text_surface = font.render(str(score), True, cfg.COLORS["white"])
            locs = cfg.TEXT_LOC["score_value"]
            screen.blit(text_surface, (locs[0], locs[1]))

            # Print lives
            lives_color = (
                cfg.COLORS["red"]
                if lives < 2
                else (cfg.COLORS["orange"] if lives < 5 else cfg.COLORS["green"])
            )
            text_surface = font.render(str(max(0, lives)), True, lives_color)
            locs = cfg.TEXT_LOC["lives_value"]
            screen.blit(text_surface, (locs[0], locs[1]))

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

        # Brief pause once the player has collided with an enemy
        if player.can_spawn():
            if lives >= 0:
                sounds["player_hit"].play()
            time.sleep(cfg.PAUSES["player_hit_enemy"])
            # Update game clock at end of delay
            game_time.tick()

        # Change to the next level if door closing animation finished
        if exit_closing and not exit.is_animating():
            time.sleep(cfg.PAUSES["door_closed"])
            if level_index >= len(levels) - 1:
                level_index = 0
                reached_last_level = True
            else:
                level_index += 1
            maze_draw = True

        # Restart game if lives expended
        if lives < 0:
            for row, text_line in enumerate(cfg.ENDGAME_STRINGS):
                text_surface = font.render(text_line, True, cfg.COLORS["yellow"])
                locs = cfg.TEXT_LOC["endgame"]
                screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))
            level_index = 0
            reached_last_level = False
            score = 0
            lives = cfg.LIVES_DEFAULT
            game_intro = True
            sounds["endgame"].play()
            pygame.display.flip()
            time.sleep(cfg.PAUSES["endgame"])

    elif paused:
        if need_pause_text:
            text_surface = font.render(cfg.PAUSE_TEXT, True, cfg.COLORS["white"])
            locs = cfg.TEXT_LOC["pause"]
            screen.blit(text_surface, (locs[0], locs[1]))
            pygame.display.flip()
            need_pause_text = False

# Quit
pygame.quit()
