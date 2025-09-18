import pygame
from tkinter import messagebox, filedialog
from settings import config as cfg
from rect.utils import define_rect
from rect.draw import draw_square, draw_asset, draw_maze
from grid.utils import invert_maze_to_grid, grid_space
from fileio.load import read_csv_path
from fileio.export import (
    export_path_coords_to_csv,
    export_asset_coords_to_csv,
    export_metadata,
    move_files,
)


# Function to export screenshot
def export_screenshot(maze_width, maze_height, image_boundary, screen, filename):
    screenshot_rect = pygame.Rect(
        cfg.DRAW_IMAGE_X,
        cfg.DRAW_IMAGE_Y,
        maze_width + 2 * image_boundary,
        maze_height + 2 * image_boundary,
    )
    sub_surface = screen.subsurface(screenshot_rect)
    pygame.image.save(sub_surface, filename)
    print(f"Screenshot saved as {filename}")


# Function to export maze files
def export_maze_files(
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
):
    # Warning to user that final export will need all assets
    if len(asset_coords) < 8:
        messagebox.showinfo("Warning", cfg.MSG_STRING["all_assets"])
    else:
        # Export screenshot with assets
        export_screenshot(
            maze_width,
            maze_height,
            image_boundary,
            screen,
            cfg.FILES["screenshot_assets"],
        )

        # Export path coordinates to csv
        export_path_coords_to_csv(
            chosen_coords,
            cfg.DRAW_IMAGE_X,
            cfg.DRAW_IMAGE_Y,
            image_boundary,
        )
        print("Level coordinates saved as " + cfg.FILES["path_coordinates"])

        # Export asset coordinates to csv if applicable
        if asset_coords:
            export_asset_coords_to_csv(
                asset_defs,
                cfg.DRAW_IMAGE_X,
                cfg.DRAW_IMAGE_Y,
                image_boundary,
            )
            print("Asset coordinates saved as " + cfg.FILES["asset_coordinates"])

        # Export maze metadata to csv
        # Maze metadata
        maze_metadata = {
            "maze_color": maze_colors[maze_color_index],
            "level_speed": cfg.LEVEL_SPEED_ORDER[level_speed_index],
            "corn_quantity": enemy_quantity["corn"][enemy_index["corn"]],
            "tomato_quantity": enemy_quantity["tomato"][enemy_index["tomato"]],
            "pumpkin_quantity": enemy_quantity["pumpkin"][enemy_index["pumpkin"]],
        }
        export_metadata(maze_metadata)
        print("Maze metadata saved as " + cfg.FILES["metadata"])

        # Move maze files to a selected directory
        messagebox.showinfo("Instructions", cfg.MSG_STRING["maze_folder"])
        selected_directory = filedialog.askdirectory(
            initialdir="../assets/levels/", title="Select a Directory"
        )
        move_files(".", selected_directory)


# Function to change color of maze
def change_maze_color(
    screen, maze_color_index, maze_colors, image_boundary, maze_width, maze_height
):
    maze_color_index_old = maze_color_index
    if maze_color_index >= len(maze_colors) - 1:
        maze_color_index = 0
    else:
        maze_color_index += 1
    maze_rect = pygame.Rect(
        cfg.DRAW_IMAGE_X + image_boundary,
        cfg.DRAW_IMAGE_X + image_boundary,
        maze_width,
        maze_height,
    )
    sub_surface = screen.subsurface(maze_rect)
    pixel_array = pygame.PixelArray(sub_surface)
    pixel_array.replace(
        maze_colors[maze_color_index_old], maze_colors[maze_color_index]
    )
    del pixel_array
    pygame.display.update()

    return maze_color_index


# Function to cycle level speed
def cycle_level_speed(level_speed_index, screen, dirty_rects, fonts):
    if level_speed_index >= len(cfg.LEVEL_SPEED_ORDER) - 1:
        level_speed_index = 0
    else:
        level_speed_index += 1

    # Erase displayed speed
    temp_rect = pygame.Rect(cfg.WHITE_RECTS["speed"])
    draw_square(temp_rect, screen, cfg.COLORS["white"], dirty_rects)

    # Display new number
    text_surface = fonts["normal"].render(
        str(cfg.LEVEL_SPEED_ORDER[level_speed_index]),
        True,
        cfg.COLORS["blue"],
    )
    loc = cfg.TEXT_LOC["level_speed"]
    screen.blit(text_surface, (loc[0], loc[1]))
    pygame.display.update()

    return level_speed_index


# Function to cycle enemy quantity
def cycle_enemy_quantity(
    enemy_name, enemy_index, enemy_quantity, screen, fonts, dirty_rects
):
    if enemy_index[enemy_name] >= len(enemy_quantity[enemy_name]) - 1:
        enemy_index[enemy_name] = 0
    else:
        enemy_index[enemy_name] += 1

    # Erase displayed number
    loc = cfg.WHITE_RECTS[enemy_name]
    temp_rect = define_rect((loc[0], loc[1]), loc[2])
    draw_square(temp_rect, screen, cfg.COLORS["white"], dirty_rects)

    match enemy_name:
        case "corn":
            text_color = "dkgreen"
        case "tomato":
            text_color = "red"
        case "pumpkin":
            text_color = "orange"

    # Display new number
    text_surface = fonts["normal"].render(
        str(enemy_quantity[enemy_name][enemy_index[enemy_name]]),
        True,
        cfg.COLORS[text_color],
    )
    loc = cfg.TEXT_LOC[enemy_name]
    screen.blit(text_surface, (loc[0], loc[1]))
    pygame.display.update()

    return enemy_index


# Function to initialize asset placement:
def init_asset_placement(
    chosen_coords,
    image_boundary,
    maze_width,
    maze_height,
    screen,
    flags,
    fonts,
    asset_letters,
    asset_defs,
):
    # Coarsen inputs prior to creating maze grid to optimize runtime
    coords_scaled = []
    for coord in chosen_coords:
        coords_scaled.append(
            (
                int((coord[0] - cfg.DRAW_IMAGE_X - image_boundary) / cfg.SCALE_FACTOR),
                int((coord[1] - cfg.DRAW_IMAGE_Y - image_boundary) / cfg.SCALE_FACTOR),
            )
        )

    # Create maze grid
    my_maze = invert_maze_to_grid(
        coords_scaled,
        cfg.MAZE_WIDTH,
        cfg.MAZE_HEIGHT,
        0,
        0,
        0,
        cfg.BLOCK_WIDTH,
    )
    # Determine how many full squares reside in maze
    num_maze_squares = grid_space(my_maze) / (cfg.BLOCK_WIDTH**2)

    # Create warning message if path space deemed too sparse
    if num_maze_squares < 8:
        messagebox.showinfo("Warning", cfg.MSG_STRING["asset_space"])
    else:
        # Export screenshot without assets
        export_screenshot(
            maze_width,
            maze_height,
            image_boundary,
            screen,
            cfg.FILES["screenshot_no_assets"],
        )

        # Flag for discontinuing maze drawing
        flags.maze_draw = False

        # Overwrite old text
        right_rect = pygame.Rect(cfg.WHITE_RECTS["assets"])
        screen.fill(cfg.COLORS["white"], right_rect)
        bottom_rect = pygame.Rect(cfg.WHITE_RECTS["maze_load"])
        screen.fill(cfg.COLORS["white"], bottom_rect)

        # Display instruction text
        for row, text_line in enumerate(cfg.ASSET_STRINGS):
            text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["black"])
            if row == 1:
                loc = cfg.TEXT_LOC["place_assets_row_1"]
            else:
                loc = cfg.TEXT_LOC["place_assets"]
            screen.blit(text_surface, (loc[0], loc[1] + row * loc[2]))

        # List of asset choices
        black_rect = pygame.Rect(cfg.BLACK_RECTS["assets"])
        screen.fill(cfg.COLORS["black"], black_rect)
        asset_letters = [asset["letter"].lower() for asset in asset_defs]
        loc = cfg.TEXT_LOC["assets"]
        for index, asset in enumerate(asset_defs):
            screen.blit(
                fonts["small"].render(
                    asset["letter"] + ": " + asset["description"],
                    True,
                    asset["color"],
                ),
                (loc[0], loc[1] + index * loc[2]),
            )
        pygame.display.update()

    return asset_letters, asset_defs


# Function to assign asset to a location
def assign_asset_loc(
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
):
    # If asset key is pressed once this mode chosen, draw asset
    matching_asset = [
        asset
        for asset in asset_defs
        if asset.get("letter").lower() == event.unicode.lower()
    ]

    # If no location already assigned
    if not matching_asset[0].get("location"):
        asset_coord_result = draw_asset(
            asset_coords,
            chosen_coords,
            dirty_rects,
            screen,
            cfg.DRAW_IMAGE_X,
            cfg.DRAW_IMAGE_Y,
            image_boundary,
            min_block_spacing,
            block_width,
            matching_asset[0].get("letter"),
            matching_asset[0].get("color"),
            cfg.COLORS["black"],
            fonts["small"],
        )

        # Assign coordinates to asset in dictionary
        if asset_coord_result:
            for asset in asset_defs:
                if asset.get("letter") == matching_asset[0].get("letter"):
                    asset["location"] = asset_coord_result

    return asset_defs


# Function to load maze from file
def import_maze_from_file(image_boundary, maze_width, maze_height, block_width, screen):
    file_path = filedialog.askopenfilename(
        title="Select a level path coordinates CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialdir="../assets/levels/",
    )

    maze_coords = read_csv_path(file_path)

    # Draw maze onto screen, with a gray boundary
    # and inside drawable teal area
    draw_maze(
        cfg.DRAW_IMAGE_X,
        cfg.DRAW_IMAGE_Y,
        image_boundary,
        maze_width,
        maze_height,
        block_width,
        cfg.COLORS["ltgray"],
        cfg.COLORS["ltgray"],
        [],
        screen,
        0,
        None,
        None,
    )
    draw_maze(
        cfg.DRAW_IMAGE_X + image_boundary,
        cfg.DRAW_IMAGE_Y + image_boundary,
        0,
        maze_width,
        maze_height,
        block_width,
        cfg.COLORS["teal"],
        cfg.COLORS["black"],
        maze_coords,
        screen,
        0,
        None,
        None,
    )

    # Apply screen offsets
    chosen_coords = [
        (x + cfg.DRAW_IMAGE_X + image_boundary, y + cfg.DRAW_IMAGE_Y + image_boundary)
        for x, y in maze_coords
    ]
    shifted_coords_history = chosen_coords.copy()

    maze_color_index = 0

    return chosen_coords, shifted_coords_history, maze_color_index
