import os
import ast
import time
import pygame
from collections import deque
from utils.exceptions import CustomError
from rect.draw import draw_maze
from asset.sprite import Sprite
from fileio.load import (
    import_image_dir,
    get_levels,
    read_csv_dict,
    read_csv_path,
    import_maze_grid_from_txt,
)


# Clear terminal (Windows syntax)
if os.name == "nt":
    os.system("cls")

# Initialize pygame modules
pygame.init()
pygame.font.init()

# Use lucidaconsole text for retro look
font = pygame.font.SysFont("lucidaconsole", 26)

# Dimensions for window
width, height = (1600, 900)
screen = pygame.display.set_mode((width, height), vsync=1)

# Define maze properties
maze_width = 256
maze_height = 192
block_width = 12
min_block_spacing = 4
draw_image_x = 20
draw_image_y = 20
image_boundary = 4

# Set window title
pygame.display.set_caption("Snack Attack")

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
maze_colors = [teal, yellow, orange, green, dkgreen, purple, magenta, red, blue, gray]

# Scale variables
scale_factor = 4
maze_width *= scale_factor
maze_height *= scale_factor
block_width *= scale_factor
min_block_spacing *= scale_factor
image_boundary *= scale_factor

# Fill background with black color
screen.fill(black)

# Display instruction text
text_strings = [
    "I = Move up",
    "K = Move down",
    "J = Move left",
    "L = Move right",
    "Space = Stop movement",
    "F = Fire weapon",
    "************************",
    "Pause = Pause game",
    "S = Skip level",
]

# Load enemy images and scale them
images = import_image_dir("../assets/sprites/")
for image in images:
    images[image] = pygame.transform.scale(
        images[image],
        (
            int(images[image].get_width() * scale_factor),
            int(images[image].get_height() * scale_factor),
        ),
    )
    # Make teal the transparent color
    images[image].set_colorkey(teal)

# Store dictionary with item image definitions
item_image_defs = {"1": "strawberry", "2": "cherry", "3": "banana", "4": "grape"}

# Get levels and their supporting file paths
level_dir = "../assets/levels/"
levels = get_levels(level_dir)

if not levels:
    raise CustomError(f"Could not load any level folders at {level_dir}")
else:
    level_index = 0

# Level speed definitions (pixels per second for moving sprites)
level_speeds = {"slow": 90, "medium": 120, "fast": 180, "frantic": 270}
# Enemy spawn frequency speed definitions (seconds between spawns)
spawn_speeds = {"slow": 1, "medium": 0.75, "fast": 0.5, "frantic": 0.25}

# Update initial display
pygame.display.update()

# Game loop
maze_draw = True
create_sprites = False
rungame = False
paused = False
s_pressed = False
f_pressed = False
need_pause_text = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                s_pressed = True
            if event.key == pygame.K_PAUSE:
                paused = not paused
                need_pause_text = True
            if event.key == pygame.K_f:
                f_pressed = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s and s_pressed:
                # Skip to next level
                if level_index >= len(levels) - 1:
                    level_index = 0
                else:
                    level_index += 1
                maze_draw = True
                s_pressed = False
            if event.key == pygame.K_f and f_pressed:
                f_pressed = False

    # Draw maze and instructions on screen
    if maze_draw:
        maze_assets = read_csv_dict(levels[level_index].get("assets"))
        maze_metadata = read_csv_dict(levels[level_index].get("metadata"))[0]
        maze_path = read_csv_path(levels[level_index].get("path"))
        maze_grid = import_maze_grid_from_txt(levels[level_index].get("grid"))

        # Perform clearing of screen to remove old maze and clear up memory
        screen.fill(black)
        pygame.display.flip()

        # Print instructions and draw maze
        for row, text_line in enumerate(text_strings):
            text_surface = font.render(text_line, True, white)
            screen.blit(text_surface, (1140, 350 + row * 50))
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
        )

        # Save subsurface for game loop re-draw
        rect_area = pygame.Rect(0, 0, width, height)
        temp_surf = screen.subsurface(rect_area)
        area_surf = temp_surf.copy()

        # Save relevant metadata
        level_speed = maze_metadata.get("level_speed")
        num_corn = ast.literal_eval(maze_metadata.get("corn_quantity"))
        num_tomato = ast.literal_eval(maze_metadata.get("tomato_quantity"))
        num_pumpkin = ast.literal_eval(maze_metadata.get("pumpkin_quantity"))

        # Assign appropriate sprite speed, defaulting to slow
        if level_speed in level_speeds.keys():
            pixels_per_second = level_speeds.get(level_speed)
        else:
            pixels_per_second = level_speeds.get("slow")

        # Assign appropriate enemy respawn speed, defaulting to slow
        if level_speed in spawn_speeds.keys():
            seconds_to_spawn = spawn_speeds.get(level_speed)
        else:
            seconds_to_spawn = spawn_speeds.get("slow")

        # Save maze asset coordinates into a single dictionary and check validity
        # of asset coordinates with error handling
        allowable_letters = ["S", "R", "E", "1", "2", "3", "4", "H"]
        asset_coord = {}
        for dict in maze_assets:
            asset_coord[dict.get("letter")] = ast.literal_eval(dict.get("location"))
        if (
            len(asset_coord) != len(allowable_letters)
            or any(
                not isinstance(value, tuple) or not value
                for value in asset_coord.values()
            )
            or any(key not in allowable_letters for key in asset_coord.keys())
        ):
            custom_string = (
                "Level error! The asset coordinates csv must include"
                " exactly 8 unique asset locations, assigned to each of the following: "
            )
            raise CustomError(custom_string + str(allowable_letters))

        # Set flags
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
            if key in item_image_defs:
                items[key] = Sprite(
                    key,
                    images[item_image_defs.get(key)],
                    asset_coord.get(key),
                    0,
                    False,
                    int(block_width / 4),
                    block_width,
                )

        # Initialize player
        player = Sprite(
            "player",
            images["combine"],
            asset_coord.get("S"),
            pixels_per_second,
            True,
            int(block_width / 4),
            block_width,
        )

        # Initialize enemies
        corns = []
        tomatoes = []
        pumpkins = []
        for i in range(num_corn):
            corns.append(
                Sprite(
                    "corn",
                    images["corn"],
                    asset_coord.get("E"),
                    pixels_per_second,
                    False,
                    int(block_width / 2),
                    block_width,
                )
            )
        for i in range(num_tomato):
            tomatoes.append(
                Sprite(
                    "tomato",
                    images["tomato"],
                    asset_coord.get("E"),
                    pixels_per_second,
                    False,
                    int(block_width / 2),
                    block_width,
                )
            )
        for i in range(num_pumpkin):
            pumpkins.append(
                Sprite(
                    "pumpkin",
                    images["pumpkin"],
                    asset_coord.get("E"),
                    pixels_per_second,
                    False,
                    int(block_width / 2),
                    block_width,
                )
            )

        # Update screen, set flags and variables
        game_time = pygame.time.Clock()
        start_time = time.time()
        projectile = []
        blast = []
        rungame = True
        exit_found = False
        create_sprites = False
        spawned_enemies = 0

    # Primary game loop
    elif rungame and not paused:
        # Get game time delta for determining whether to move sprites
        game_dt = game_time.tick() / 1000

        # Get alive enemies
        alive_corns = [corn for corn in corns if not corn.is_destroyed()]
        alive_tomatoes = [tomato for tomato in tomatoes if not tomato.is_destroyed()]
        alive_pumpkins = [pumpkin for pumpkin in pumpkins if not pumpkin.is_destroyed()]

        # Move player and enemies to respawn if player collided with enemy
        if player.can_spawn():
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

        # Clear screen and re-draw background
        screen.fill(black)
        screen.blit(area_surf, (0, 0))

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

        # Player movement and attack input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l]:
            player.set_direction(1, 0)  # right
        elif keys[pygame.K_j]:
            player.set_direction(-1, 0)  # left
        elif keys[pygame.K_i]:
            player.set_direction(0, -1)  # up
        elif keys[pygame.K_k]:
            player.set_direction(0, 1)  # down
        elif keys[pygame.K_SPACE]:
            player.set_direction(0, 0)  # stop

        # Player fire command (only one projectile at a time)
        if f_pressed and not projectile:
            f_pressed = False
            projectile_direction = (1, 0)
            if player.direction != (0, 0):
                projectile_direction = player.direction
            # Initialize projectile at front end of player
            player_location = player.get_center_position()
            projectile_location = (
                player_location[0] + projectile_direction[0] * int(block_width / 4),
                player_location[1] + projectile_direction[1] * int(block_width / 4),
            )
            projectile = Sprite(
                "projectile",
                images["projectile"],
                projectile_location,
                pixels_per_second * 2,
                True,
                int(block_width / 4),
                int(block_width / 4),
            )
            projectile.set_direction(projectile_direction[0], projectile_direction[1])

        # Move player, projectiles, and enemies
        if not exit_found:
            player.perform_move(maze_grid, game_dt)
            if projectile:
                projectile.perform_move(maze_grid, game_dt)
            for corn in active_corns:
                corn.set_navigate_direction(player, maze_grid)
                corn.perform_move(maze_grid, game_dt)
            for tomato in active_tomatoes:
                tomato.set_navigate_direction(player, maze_grid)
                tomato.perform_move(maze_grid, game_dt)
            for pumpkin in active_pumpkins:
                pumpkin.set_navigate_direction(player, maze_grid)
                pumpkin.perform_move(maze_grid, game_dt)

        # Remove projectiles which hit an enemy or a wall, then draw blast
        if projectile and (
            projectile.is_destroyed()
            or not projectile.can_move(
                projectile_direction[0], projectile_direction[1], maze_grid
            )
        ):
            projectile_location = projectile.get_center_position()
            projectile = []
            blast = Sprite(
                "blast",
                images["projectile_hit_01"],
                projectile_location,
                0,
                False,
                int(block_width / 4),
                int(block_width / 4),
            )
            blast_images = [
                images["projectile_hit_02"],
                images["projectile_hit_03"],
                images["projectile_hit_02"],
                images["projectile_hit_01"],
            ]
            blast_delays = [0.05, 0.1, 0.15, 0.2]
            blast.animate(blast_images, blast_delays)
        elif blast and not blast.is_animating():
            # Remove blasts which have finished animating
            blast = []

        # Detect corn collision with player and projectile
        for corn in alive_corns:
            if player.collide_check(corn):
                player.toggle_spawn()
                break
            elif (
                projectile
                and not projectile.is_destroyed()
                and projectile.collide_check(corn)
            ):
                projectile.toggle_destroy()
                corn.toggle_destroy()
                corn_images = [
                    images["corn_flat_01"],
                    images["corn_flat_02"],
                    images["corn_flat_03"],
                    images["corn_flat_04"],
                    images["empty"],
                ]
                corn_delays = [0.2, 0.25, 0.3, 0.35, 0.4]
                corn.animate(corn_images, corn_delays)

        # Detect tomato collision with player and projectile
        for tomato in alive_tomatoes:
            if player.collide_check(tomato) and not tomato.is_destroyed():
                player.toggle_spawn()
                break
            elif (
                projectile
                and not projectile.is_destroyed()
                and projectile.collide_check(tomato)
            ):
                projectile.toggle_destroy()
                tomato.toggle_destroy()
                tomato_images = [
                    images["tomato_flat_01"],
                    images["tomato_flat_02"],
                    images["tomato_flat_03"],
                    images["tomato_flat_04"],
                    images["empty"],
                ]
                tomato_delays = [0.2, 0.25, 0.3, 0.35, 0.4]
                tomato.animate(tomato_images, tomato_delays)

        # Detect pumpkin collision with player and projectile
        for pumpkin in alive_pumpkins:
            if player.collide_check(pumpkin):
                player.toggle_spawn()
                break
            elif (
                projectile
                and not projectile.is_destroyed()
                and projectile.collide_check(pumpkin)
            ):
                projectile.toggle_destroy()
                pumpkin_images = [
                    images["pumpkin_fire"],
                    images["pumpkin"],
                ]
                pumpkin_delays = [0.1, 0.4]
                pumpkin.animate(pumpkin_images, pumpkin_delays)

        # Detect item collision and delete those items
        delete_items = []
        for item in items:
            if player.collide_check(items[item]):
                delete_items.append(item)
        for item in delete_items:
            del items[item]

        # If no more items, draw exit
        if not items and not exit_created:
            exit = Sprite(
                "H",
                images["door"],
                asset_coord.get("H"),
                0,
                False,
                int(block_width / 4),
                block_width,
            )
            exit_created = True

        # Draw exit and animate
        if exit_created:
            exit.draw(draw_image_x, draw_image_y, image_boundary, screen)
            # Proceed to next level if same location as exit
            if player.get_center_position() == exit.get_center_position():
                exit_found = True
                if not exit_opening:
                    # Animate door opening
                    door_images = [
                        images["door"],
                        images["door_open_01"],
                        images["door_open_02"],
                        images["door_open_03"],
                        images["door_open_04"],
                    ]
                    door_delays = [0.2, 0.4, 0.6, 0.8, 1.0]
                    exit.animate(door_images, door_delays)
                    exit_opening = True
                elif exit_opening and not exit_closing and not exit.is_animating():
                    # Animate door closing
                    door_images.reverse()
                    exit.animate(door_images, door_delays)
                    exit_closing = True

        # Draw item, projectile, blast, player, and enemy sprites
        [
            items[item].draw(draw_image_x, draw_image_y, image_boundary, screen)
            for item in items
        ]
        if projectile:
            projectile.draw(draw_image_x, draw_image_y, image_boundary, screen)
        [
            corn.draw(draw_image_x, draw_image_y, image_boundary, screen)
            for corn in corns
            if corn.can_spawn()
        ]
        [
            tomato.draw(draw_image_x, draw_image_y, image_boundary, screen)
            for tomato in tomatoes
            if tomato.can_spawn()
        ]
        [
            pumpkin.draw(draw_image_x, draw_image_y, image_boundary, screen)
            for pumpkin in pumpkins
            if pumpkin.can_spawn()
        ]
        if blast:
            blast.draw(draw_image_x, draw_image_y, image_boundary, screen)
        player.draw(draw_image_x, draw_image_y, image_boundary, screen)

        # Draw exit again overtop player if door closing
        if exit_closing:
            exit.draw(draw_image_x, draw_image_y, image_boundary, screen)

        # Update screen
        pygame.display.flip()

        # Brief pause once the player has collided with an enemy
        if player.can_spawn():
            time.sleep(0.5)

        # Change to the next level if door closing animation finished
        if exit_closing and not exit.is_animating():
            time.sleep(0.5)
            if level_index >= len(levels) - 1:
                level_index = 0
            else:
                level_index += 1
            maze_draw = True

    elif paused:
        if need_pause_text:
            text_surface = font.render(
                "Game paused. Press Pause button to resume.", True, white
            )
            screen.blit(text_surface, (500, 850))
            pygame.display.flip()
            need_pause_text = False

# Quit
pygame.quit()
