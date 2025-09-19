import time
import pygame
from settings import config as cfg
from asset.sprite import Sprite
from path.pathfind import create_flow_field


# Function to reset player and enemies after player destroyed
def reset_actors(flags, player, corns, tomatoes, pumpkins, asset_coord):
    # Move player and enemies to respawn if player collided with enemy
    flags.screen_change = True
    player.reset(asset_coord.get("R")[0], asset_coord.get("R")[1])
    player.toggle_spawn()
    start_time = time.time()
    spawned_enemies = 0
    enemies = corns + tomatoes + pumpkins
    for enemy in enemies:
        enemy.reset(asset_coord.get("E")[0], asset_coord.get("E")[1])
        if enemy.can_spawn():
            enemy.toggle_spawn()
        if enemy.is_invincible:
            enemy.reset_image()
        if enemy.has_seen_player():
            enemy.toggle_seen_player()
    projectile = []
    blast = []
    flow_field = None

    return start_time, spawned_enemies, projectile, blast, flow_field


# Function to determine whether to respawn enemy based on current time
def determine_spawn(start_time, spawned_enemies, seconds_to_spawn, enemies):
    # Determine if it's time to spawn a new enemy
    respawn_time = time.time() - start_time
    if respawn_time >= (spawned_enemies + 1) * seconds_to_spawn:
        # Check if there are still enemies to spawn
        if spawned_enemies < len(enemies):
            index = spawned_enemies
            enemy_to_spawn = enemies[index]
            # Only spawn the enemy if it has not been destroyed
            if not enemy_to_spawn.is_destroyed():
                enemy_to_spawn.toggle_spawn()
            spawned_enemies += 1
    return spawned_enemies


# Function to initialize projectile
def init_projectile(
    flags,
    player,
    block_width,
    maze_factor,
    images,
    sounds,
    pixels_per_second,
    rotate_image,
):
    flags.screen_change = True
    flags.fire_pressed = False
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
        rotate_image,
    )
    projectile.set_desired_direction(projectile_direction[0], projectile_direction[1])
    sounds["proj_fire"].play()

    return projectile


# Function to move sprites
def move_sprites(
    player,
    projectile,
    enemies,
    flags,
    maze_grid,
    game_tick,
    maze_graph,
    maze_graph_coords,
    maze_factor,
    flow_field,
    barrier_sprites,
):
    player_move = False
    proj_move = False
    enemy_move = False

    if player:
        old_location = player.get_center_position()
        player_move = player.perform_move(maze_grid, game_tick)
        player_graph_coord = player.get_center_position()
        if old_location != player_graph_coord:
            player_graph_coord = tuple(
                int(element * maze_factor / cfg.SCALE_FACTOR)
                for element in player_graph_coord
            )
            if player_graph_coord in maze_graph_coords:
                flow_field = create_flow_field(
                    maze_graph, maze_graph_coords, player_graph_coord
                )
    if projectile:
        proj_move = projectile.perform_move(maze_grid, game_tick)
    for enemy in enemies:
        # If collision with barrier sprite, turn enemy around
        for sprite in barrier_sprites:
            if (
                barrier_sprites[sprite].collide_check(enemy)
                and (enemy.move_dist + enemy.speed * game_tick) >= 1
            ):
                cur_direction = enemy.get_direction()
                enemy.set_desired_direction(
                    -1 * cur_direction[0], -1 * cur_direction[1]
                )
                if enemy.has_seen_player():
                    enemy.toggle_seen_player()
                if enemy.is_path_finding():
                    enemy.toggle_path_finding()

        # Perform pathfinding if flow field has been computed
        # and if the enemy has seen the player with an unobscured path
        if flow_field and enemy.has_seen_player():
            enemy_graph_coord = enemy.get_center_position()
            enemy_graph_coord = tuple(
                int(element * maze_factor / cfg.SCALE_FACTOR)
                for element in enemy_graph_coord
            )
            if enemy_graph_coord in maze_graph_coords:
                enemy.set_pathfind_direction(flow_field, enemy_graph_coord)
            elif not enemy.is_path_finding():
                enemy.set_navigate_direction(
                    player, barrier_sprites, maze_grid, game_tick
                )
        else:
            enemy.set_navigate_direction(player, barrier_sprites, maze_grid, game_tick)
        cur_enemy_move = enemy.perform_move(maze_grid, game_tick)
        if not enemy_move:
            enemy_move = cur_enemy_move

    if any([player_move, proj_move, enemy_move]):
        flags.screen_change = True

    return flags, flow_field


# Function to move player towards exit if proximity deemed a collision
def move_to_exit(
    player, exit, direction_order, key_order, maze_grid, game_tick, flags, sounds
):
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
            player.set_desired_direction(direction_order[-1][0], direction_order[-1][1])
        player.perform_move(maze_grid, game_tick)
        flags.screen_change = True
    else:
        if not flags.exit_sound_played:
            sounds["exit"].play()
            flags.exit_sound_played = True

    return flags


# Function to initialize blast
def init_blast(
    projectile, sounds, flags, images, block_width, maze_factor, rotate_image
):
    if projectile.is_stopped():
        sounds["proj_hit_wall"].play()
    flags.screen_change = True
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
        rotate_image,
    )
    blast.animate(images, cfg.IMAGE_SERIES["blast"][1:], cfg.DELAYS["blast"])

    return projectile, blast, flags


# Function to detect enemy collision with player and projectile
def check_enemy_collision(
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
):
    if player.collide_check(enemy):
        lives -= 1
        player.toggle_spawn()
    elif (
        projectile and not projectile.is_destroyed() and projectile.collide_check(enemy)
    ):
        if not enemy.is_invincible:
            score += cfg.SCORES[enemy.name]
            enemy.toggle_destroy()
            sounds["proj_hit_enemy"].play()
            spawned_enemies -= 1
            start_time += seconds_to_spawn
        else:
            sounds["proj_hit_invincible"].play()
        flags.screen_change = True
        projectile.toggle_destroy()
        enemy.animate(images, cfg.IMAGE_SERIES[enemy.name][1:], cfg.DELAYS[enemy.name])

    return lives, score, spawned_enemies, start_time, flags


# Function to remove items
def remove_items(enemies, flags, items, player, score, sounds, barrier_sprites):
    # If no more enemies, remove remaining items
    delete_items = []
    all_destroyed = all(enemy.is_destroyed() for enemy in enemies)
    if all_destroyed:
        flags.screen_change = True
        for item in items:
            delete_items.append(item)
    else:
        # Detect item collision and delete those items
        for item in items:
            if player.collide_check(items[item]):
                flags.screen_change = True
                score += cfg.SCORES["item"]
                delete_items.append(item)
                if len(items) > 1:
                    sounds["item"].play()

    # Delete appropriate items
    for item in delete_items:
        del items[item]
        del barrier_sprites[item]

    return items, flags, score, all_destroyed, barrier_sprites


# Function to initialize exit
def init_exit(
    flags,
    all_destroyed,
    sounds,
    lives,
    images,
    asset_coord,
    block_width,
    maze_factor,
    rotate_image,
):
    flags.screen_change = True
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
        int(block_width / (maze_factor * 4)),
        block_width,
        rotate_image,
    )
    flags.exit_created = True

    return exit, flags, lives


# Function to animate exit
def animate_exit(flags, exit, images):
    flags.screen_change = True
    flags.exit_found = True
    if not flags.exit_opening:
        # Animate door opening
        exit.animate(images, cfg.IMAGE_SERIES["door"][1:], cfg.DELAYS["door"])
        flags.exit_opening = True
    elif flags.exit_opening and not flags.exit_closing and not exit.is_animating():
        # Animate door closing
        exit.animate(images, cfg.IMAGE_SERIES["door"][:0:-1], cfg.DELAYS["door"])
        flags.exit_closing = True

    return flags


# Function to draw sprites by updating sprite_image_data
def draw_sprites(
    sprite_image_data,
    flags,
    items,
    enemies,
    player,
    projectile,
    blast,
    exit,
    image_boundary,
    maze_factor,
    pause_delta,
):
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
        enemy.increment_animation_start_time(pause_delta)
        for enemy in enemies
        if enemy.can_spawn() and enemy.animation_start_time and pause_delta > 0
    ]
    [
        sprite_image_data.append(
            enemy.draw(cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor)
        )
        for enemy in enemies
        if enemy.can_spawn()
    ]
    if blast:
        if blast.animation_start_time and pause_delta > 0:
            blast.increment_animation_start_time(pause_delta)
        sprite_image_data.append(
            blast.draw(cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor)
        )
    if player:
        sprite_image_data.append(
            player.draw(cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor)
        )

    # Draw exit again overtop player if door closing
    if cfg.CLOSE_EXIT_OVERTOP and flags.exit_closing:
        sprite_image_data.append(
            exit.draw(cfg.DRAW_IMAGE_X, cfg.DRAW_IMAGE_Y, image_boundary, maze_factor)
        )

    # Reset pause delta
    if pause_delta > 0:
        pause_delta = 0

    return sprite_image_data, pause_delta


# Function to update screen
def screen_update(
    screen, area_surf, fonts, score, lives, controls_option, sprite_image_data, flags
):
    # Clear screen and re-draw background
    screen.fill(cfg.COLORS["black"])
    screen.blit(area_surf, (0, 0))

    # Print controls
    black_rect = pygame.Rect(cfg.BLACK_RECTS["controls"])
    screen.fill(cfg.COLORS["black"], black_rect)
    for row, text_line in enumerate(cfg.CONTROLS_TEXT[controls_option]):
        text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["white"])
        locs = cfg.TEXT_LOC["controls"]
        screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))

    # Print score
    text_surface = fonts["normal"].render(str(score), True, cfg.COLORS["white"])
    locs = cfg.TEXT_LOC["score_value"]
    screen.blit(text_surface, (locs[0], locs[1]))

    # Print lives
    lives_color = (
        cfg.COLORS["red"]
        if lives < 2
        else (cfg.COLORS["orange"] if lives < 5 else cfg.COLORS["green"])
    )
    text_surface = fonts["normal"].render(str(max(0, lives)), True, lives_color)
    locs = cfg.TEXT_LOC["lives_value"]
    screen.blit(text_surface, (locs[0], locs[1]))

    # Print sprites
    for item in sprite_image_data:
        screen.blit(item[0], item[1])

    pygame.display.flip()
    flags.screen_change = False

    return flags


# Function for checking game tick, explained as follows:
# If game calculated tick faster than realtime clock, introduce
# delay to ensure game doesn't run too fast. Otherwise, allow game
# to run at the cadence of calculated tick, which may result in game
# flags.running slower than tick rate on slower PCs.
def check_game_tick(game_time, game_tick):
    game_dt = game_time.tick() / 1000
    if game_dt - game_tick < 0:
        time.sleep(game_tick - game_dt)
        game_time.tick()


# Function to introduce pause after player collision with enemy
def player_collide_pause(lives, sounds, game_time):
    if lives >= 0:
        sounds["player_hit"].play()
    time.sleep(cfg.PAUSES["player_hit_enemy"])
    # Update game clock at end of delay
    game_time.tick()


# Function to exit to the next level
def exit_level(level_index, levels, flags):
    time.sleep(cfg.PAUSES["door_closed"])
    if level_index >= len(levels) - 1:
        level_index = 0
        flags.reached_last_level = True
    else:
        level_index += 1
    flags.maze_draw = True

    return flags, level_index


# Function to end the game
def end_game(flags, fonts, screen, sounds):
    for row, text_line in enumerate(cfg.ENDGAME_STRINGS):
        text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["yellow"])
        locs = cfg.TEXT_LOC["endgame"]
        screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))
    flags.game_intro = True
    level_index = 0
    score = 0
    lives = cfg.LIVES_DEFAULT
    sounds["endgame"].play()
    pygame.display.flip()
    time.sleep(cfg.PAUSES["endgame"])

    return flags, level_index, score, lives


# Function to pause the game
def pause_game(flags, fonts, screen):
    if flags.need_pause_text:
        text_surface = fonts["normal"].render(cfg.PAUSE_TEXT, True, cfg.COLORS["white"])
        locs = cfg.TEXT_LOC["pause"]
        screen.blit(text_surface, (locs[0], locs[1]))
        pygame.display.flip()
        flags.need_pause_text = False

    return flags
