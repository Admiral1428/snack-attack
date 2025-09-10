import os
import pygame
import time
import tkinter as tk
from tkinter import messagebox, filedialog
from settings import config as cfg
from rect.utils import define_rect, shift_rect_to_divisible_pos
from rect.draw import draw_square, draw_asset, draw_maze
from grid.utils import invert_maze_to_grid, grid_space
from fileio.load import import_image_dir
from fileio.export import (
    export_path_coords_to_csv,
    export_asset_coords_to_csv,
    export_metadata,
    move_files,
)
from path.utils import (
    rect_within_boundary,
    rect_gives_uniform_path,
)


# Clear terminal (Windows syntax)
if os.name == "nt":
    os.system("cls")

# Create the main application window for messages and hide it
root = tk.Tk()
root.withdraw()

# Initialize pygame modules
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

# Use Arial text
font = pygame.font.SysFont("Arial", 30)
font_small = pygame.font.SysFont("Arial", 26)

# Dimensions for window
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT), vsync=1)

# Set window title
pygame.display.set_caption("Level Builder")

# Create a list of colors to be used for selecting maze wall color
maze_colors = []
maze_color_index = 0
for key, value in cfg.COLORS.items():
    if key not in ["white", "black", "ltgray"]:
        maze_colors.append(value)

# Scale variables
maze_width = cfg.MAZE_WIDTH * cfg.SCALE_FACTOR
maze_height = cfg.MAZE_HEIGHT * cfg.SCALE_FACTOR
block_width = cfg.BLOCK_WIDTH * cfg.SCALE_FACTOR
image_boundary = cfg.IMAGE_BOUNDARY * cfg.SCALE_FACTOR
min_block_spacing = cfg.MIN_BLOCK_SPACING * cfg.SCALE_FACTOR

# Fill background with white color
screen.fill(cfg.COLORS["white"])

# Draw empty maze onto screen, with a gray boundary
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
)
draw_maze(
    cfg.DRAW_IMAGE_X + image_boundary,
    cfg.DRAW_IMAGE_Y + image_boundary,
    0,
    maze_width,
    maze_height,
    block_width,
    cfg.COLORS["teal"],
    cfg.COLORS["teal"],
    [],
    screen,
    0,
    None,
)

# Display instruction text
for row, text_line in enumerate(cfg.DRAW_STRINGS):
    if row <= 7:
        selected_color = cfg.COLORS["black"]
    elif row == 8:
        selected_color = cfg.COLORS["dkgreen"]
    elif row == 9:
        selected_color = cfg.COLORS["red"]
    else:
        selected_color = cfg.COLORS["orange"]
    text_surface = font.render(text_line, True, selected_color)
    loc = cfg.TEXT_LOC["maze_draw"]
    screen.blit(text_surface, (loc[0], loc[1] + row * loc[2]))


# Initialize number of enemies
corn_quantities = range(cfg.MAX_CORN + 1)
tomato_quantities = range(cfg.MAX_TOMATO + 1)
pumpkin_quantities = range(cfg.MAX_PUMPKIN + 1)
corn_index = 0
tomato_index = 0
pumpkin_index = 0


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

corn_image = images["corn"]
tomato_image = images["tomato"]
pumpkin_image = images["pumpkin"]

# Initialize level speed
level_speed_index = 0

# Display level speed in blue color
# Display new number
text_surface = font.render(
    str(cfg.LEVEL_SPEED_ORDER[level_speed_index]), True, cfg.COLORS["blue"]
)
loc = cfg.TEXT_LOC["level_speed"]
screen.blit(text_surface, (loc[0], loc[1]))

# Display enemy images
screen.blit(corn_image, cfg.IMAGE_LOC["corn"])
screen.blit(tomato_image, cfg.IMAGE_LOC["tomato"])
screen.blit(pumpkin_image, cfg.IMAGE_LOC["pumpkin"])

# Display number of enemies below each image
text_surface = font.render(
    str(corn_quantities[corn_index]), True, cfg.COLORS["dkgreen"]
)
screen.blit(text_surface, cfg.TEXT_LOC["corns"])
text_surface = font.render(
    str(tomato_quantities[tomato_index]), True, cfg.COLORS["red"]
)
screen.blit(text_surface, cfg.TEXT_LOC["tomatoes"])
text_surface = font.render(
    str(pumpkin_quantities[pumpkin_index]), True, cfg.COLORS["orange"]
)
screen.blit(text_surface, cfg.TEXT_LOC["pumpkins"])

# Update initial display
pygame.display.update()

# List of dirty rectangles, representing areas of screen to be updated
dirty_rects = []

# List of mouse coordinates that have been added
chosen_coords = []

# Track previous shifted coordinate history
shifted_coords_history = []

# List of assets and asset coordinates that have been added
asset_defs = []
asset_coords = []


# Game loop
mouse_left_held = False
mouse_right_click = False
arrow_pressed = False
arrow_index = -1
maze_draw = True
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos  # Get the absolute coordinates
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_left_held = True
            elif event.button == 3:  # Right mouse button
                mouse_right_click = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                mouse_left_held = False
        elif event.type == pygame.KEYDOWN:
            if maze_draw and event.key in [
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_RIGHT,
            ]:
                arrow_pressed = True
                current_arrow = event.key
            elif event.key == pygame.K_c and not maze_draw:
                # Warning to user that final export will need all assets
                if len(asset_coords) < 8:
                    messagebox.showinfo("Warning", cfg.MSG_STRING["all_assets"])
                else:
                    # Export screenshot with assets
                    screenshot_rect = pygame.Rect(
                        cfg.DRAW_IMAGE_X,
                        cfg.DRAW_IMAGE_Y,
                        maze_width + 2 * image_boundary,
                        maze_height + 2 * image_boundary,
                    )
                    sub_surface = screen.subsurface(screenshot_rect)
                    pygame.image.save(sub_surface, cfg.FILES["screenshot_assets"])
                    print(f"Screenshot saved as {cfg.FILES["screenshot_assets"]}")

                    # Export path coordinates to csv
                    export_path_coords_to_csv(
                        chosen_coords,
                        cfg.DRAW_IMAGE_X,
                        cfg.DRAW_IMAGE_Y,
                        image_boundary,
                    )
                    print("Level coordinates saved as " + cfg.FILES["path_coordinates"])

                    # Export asset coordinates to csv if applicable
                    if asset_defs:
                        export_asset_coords_to_csv(
                            asset_defs,
                            cfg.DRAW_IMAGE_X,
                            cfg.DRAW_IMAGE_Y,
                            image_boundary,
                        )
                        print(
                            "Asset coordinates saved as "
                            + cfg.FILES["asset_coordinates"]
                        )

                    # Export maze metadata to csv
                    # Maze metadata
                    maze_metadata = {
                        "maze_color": maze_colors[maze_color_index],
                        "level_speed": cfg.LEVEL_SPEED_ORDER[level_speed_index],
                        "corn_quantity": corn_quantities[corn_index],
                        "tomato_quantity": tomato_quantities[tomato_index],
                        "pumpkin_quantity": pumpkin_quantities[pumpkin_index],
                    }
                    export_metadata(maze_metadata)
                    print("Maze metadata saved as " + cfg.FILES["metadata"])

                    # Move maze files to a selected directory
                    messagebox.showinfo("Instructions", cfg.MSG_STRING["maze_folder"])
                    selected_directory = filedialog.askdirectory(
                        initialdir="../assets/levels/", title="Select a Directory"
                    )
                    move_files(".", selected_directory)
            elif event.key == pygame.K_w and maze_draw:
                # Change the color of the maze
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
            elif event.key == pygame.K_f and maze_draw:
                # Cycle level speed
                if level_speed_index >= len(cfg.LEVEL_SPEED_ORDER) - 1:
                    level_speed_index = 0
                else:
                    level_speed_index += 1

                # Erase displayed speed
                temp_rect = pygame.Rect(cfg.WHITE_RECTS["speed"])
                draw_square(temp_rect, screen, cfg.COLORS["white"], dirty_rects)

                # Display new number
                text_surface = font.render(
                    str(cfg.LEVEL_SPEED_ORDER[level_speed_index]),
                    True,
                    cfg.COLORS["blue"],
                )
                loc = cfg.TEXT_LOC["level_speed"]
                screen.blit(text_surface, (loc[0], loc[1]))
                pygame.display.update()
            elif event.key == pygame.K_j and maze_draw:
                # Cycle corn quantity
                if corn_index >= len(corn_quantities) - 1:
                    corn_index = 0
                else:
                    corn_index += 1

                # Erase displayed number
                loc = cfg.WHITE_RECTS["corns"]
                temp_rect = define_rect((loc[0], loc[1]), loc[2])
                draw_square(temp_rect, screen, cfg.COLORS["white"], dirty_rects)

                # Display new number
                text_surface = font.render(
                    str(corn_quantities[corn_index]), True, cfg.COLORS["dkgreen"]
                )
                loc = cfg.TEXT_LOC["corns"]
                screen.blit(text_surface, (loc[0], loc[1]))
                pygame.display.update()
            elif event.key == pygame.K_k and maze_draw:
                # Cycle tomato quantity
                if tomato_index >= len(tomato_quantities) - 1:
                    tomato_index = 0
                else:
                    tomato_index += 1

                # Erase displayed number
                loc = cfg.WHITE_RECTS["tomatoes"]
                temp_rect = define_rect((loc[0], loc[1]), loc[2])
                draw_square(temp_rect, screen, cfg.COLORS["white"], dirty_rects)

                # Display new number
                text_surface = font.render(
                    str(tomato_quantities[tomato_index]), True, cfg.COLORS["red"]
                )
                loc = cfg.TEXT_LOC["tomatoes"]
                screen.blit(text_surface, (loc[0], loc[1]))
                pygame.display.update()
            elif event.key == pygame.K_l and maze_draw:
                # Cycle pumpkin quantity
                if pumpkin_index >= len(pumpkin_quantities) - 1:
                    pumpkin_index = 0
                else:
                    pumpkin_index += 1

                # Erase displayed number
                loc = cfg.WHITE_RECTS["pumpkins"]
                temp_rect = define_rect((loc[0], loc[1]), loc[2])
                draw_square(temp_rect, screen, cfg.COLORS["white"], dirty_rects)

                # Display new number
                text_surface = font.render(
                    str(pumpkin_quantities[pumpkin_index]), True, cfg.COLORS["orange"]
                )
                loc = cfg.TEXT_LOC["pumpkins"]
                screen.blit(text_surface, (loc[0], loc[1]))
                pygame.display.update()
            elif event.key == pygame.K_a:
                # Coarsen inputs prior to creating maze grid to optimize runtime
                coords_scaled = []
                for coord in chosen_coords:
                    coords_scaled.append(
                        (
                            int(
                                (coord[0] - cfg.DRAW_IMAGE_X - image_boundary)
                                / cfg.SCALE_FACTOR
                            ),
                            int(
                                (coord[1] - cfg.DRAW_IMAGE_Y - image_boundary)
                                / cfg.SCALE_FACTOR
                            ),
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
                    screenshot_rect = pygame.Rect(
                        cfg.DRAW_IMAGE_X,
                        cfg.DRAW_IMAGE_Y,
                        maze_width + 2 * image_boundary,
                        maze_height + 2 * image_boundary,
                    )
                    sub_surface = screen.subsurface(screenshot_rect)
                    pygame.image.save(sub_surface, cfg.FILES["screenshot_no_assets"])
                    print(f"Screenshot saved as {cfg.FILES["screenshot_no_assets"]}")

                    # Flag for discontinuing maze drawing
                    maze_draw = False

                    # Overwrite old text
                    right_rect = pygame.Rect(cfg.WHITE_RECTS["assets"])
                    screen.fill(cfg.COLORS["white"], right_rect)

                    # Display instruction text
                    for row, text_line in enumerate(cfg.ASSET_STRINGS):
                        text_surface = font.render(text_line, True, cfg.COLORS["black"])
                        if row == 1:
                            loc = cfg.TEXT_LOC["place_assets_row_1"]
                        else:
                            loc = cfg.TEXT_LOC["place_assets"]
                        screen.blit(text_surface, (loc[0], loc[1] + row * loc[2]))

                    # List of asset choices
                    black_rect = pygame.Rect(1130, 390, 330, 260)
                    screen.fill(cfg.COLORS["black"], black_rect)
                    asset_defs = cfg.ASSET_DEFS
                    asset_letters = [asset["letter"].lower() for asset in asset_defs]
                    loc = cfg.TEXT_LOC["assets"]
                    for index, asset in enumerate(asset_defs):
                        screen.blit(
                            font_small.render(
                                asset["letter"] + ": " + asset["description"],
                                True,
                                asset["color"],
                            ),
                            (loc[0], loc[1] + index * loc[2]),
                        )
                    pygame.display.update()
            # If asset key is pressed once this mode chosen, draw asset
            elif not maze_draw and event.unicode.lower() in asset_letters:
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
                        font_small,
                    )

                    # Assign coordinates to asset in dictionary
                    if asset_coord_result:
                        for asset in asset_defs:
                            if asset.get("letter") == matching_asset[0].get("letter"):
                                asset["location"] = asset_coord_result

    # Limit input collection to 60 hz to limit CPU overhead
    clock.tick(60)

    # Check if an arrow key was pressed, or if left mouse is currently held
    # down (outside of event loop) If so, draw a new square at that location,
    # if shifted to nearest nth coordinate is deemed legal (based on
    # min_block_spacing)
    if (arrow_pressed or mouse_left_held) and maze_draw:
        if arrow_pressed:
            if not chosen_coords:
                # If no previous points chosen with mouse, start at upper left corner
                current_selected_pos = (
                    cfg.DRAW_IMAGE_X + image_boundary + int(block_width / 2),
                    cfg.DRAW_IMAGE_Y + image_boundary + int(block_width / 2),
                )
            else:
                try:
                    if current_arrow == pygame.K_UP:
                        current_selected_pos = (
                            chosen_coords[arrow_index][0],
                            chosen_coords[arrow_index][1] - min_block_spacing,
                        )
                    elif current_arrow == pygame.K_DOWN:
                        current_selected_pos = (
                            chosen_coords[arrow_index][0],
                            chosen_coords[arrow_index][1] + min_block_spacing,
                        )
                    elif current_arrow == pygame.K_LEFT:
                        current_selected_pos = (
                            chosen_coords[arrow_index][0] - min_block_spacing,
                            chosen_coords[arrow_index][1],
                        )
                    else:
                        current_selected_pos = (
                            chosen_coords[arrow_index][0] + min_block_spacing,
                            chosen_coords[arrow_index][1],
                        )
                except:
                    # Catching case where index may be out of bounds
                    current_selected_pos = chosen_coords[-1]
        else:
            current_selected_pos = pygame.mouse.get_pos()

        my_rect = define_rect(current_selected_pos, block_width)
        my_rect = shift_rect_to_divisible_pos(
            my_rect,
            cfg.DRAW_IMAGE_X,
            cfg.DRAW_IMAGE_Y,
            min_block_spacing,
            image_boundary,
        )

        # If chosen coordinate from arrow keys is already in chosen coordinates,
        # save that space so that user can backtrack.
        # Subsequently highlight the block with flashing so that they know where
        # they are for context.
        if arrow_pressed and my_rect.center in chosen_coords:
            arrow_index = chosen_coords.index(my_rect.center)
            for i in range(3):
                draw_square(my_rect, screen, cfg.COLORS["white"], dirty_rects)
                time.sleep(1 / 30)
                draw_square(my_rect, screen, cfg.COLORS["black"], dirty_rects)
                time.sleep(1 / 30)
        else:
            arrow_index = -1

        # Reset flag for arrow key press
        arrow_pressed = False

        # Coarsen inputs prior to checking maze grid to optimize runtime
        coords_scaled = []
        for coord in chosen_coords:
            coords_scaled.append(
                (
                    int(
                        (coord[0] - cfg.DRAW_IMAGE_X - image_boundary)
                        / cfg.SCALE_FACTOR
                    ),
                    int(
                        (coord[1] - cfg.DRAW_IMAGE_Y - image_boundary)
                        / cfg.SCALE_FACTOR
                    ),
                )
            )
        new_center = (
            int(
                (my_rect.center[0] - cfg.DRAW_IMAGE_X - image_boundary)
                / cfg.SCALE_FACTOR
            ),
            int(
                (my_rect.center[1] - cfg.DRAW_IMAGE_Y - image_boundary)
                / cfg.SCALE_FACTOR
            ),
        )
        my_rect_scaled = define_rect(new_center, cfg.BLOCK_WIDTH)

        # Check to make sure the current shifted position is not the same as
        # the last, and that it's not in chosen coords. If all criteria met,
        # draw the new path square
        if (
            not shifted_coords_history or my_rect.center != shifted_coords_history[-1]
        ) and my_rect.center not in chosen_coords:
            shifted_coords_history.append(my_rect.center)

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
                # Add updated mouse position to list of previous points
                chosen_coords.append((my_rect.center))
                draw_square(my_rect, screen, cfg.COLORS["black"], dirty_rects)

    # Perform undo operation, which requires re-drawing overlapping squares
    elif mouse_right_click and len(chosen_coords) > 0 and maze_draw:
        # Remove last coordinate (undo)
        last_coord = chosen_coords.pop()

        # Remove last shifted coordinate from history
        shifted_coords_history.pop()

        # Draw a block overtop the old coordinate
        my_rect = define_rect(last_coord, block_width)
        selected_color = maze_colors[maze_color_index]
        draw_square(my_rect, screen, selected_color, dirty_rects)

        # Draw previous coordinates which were overlapping erased square
        for coord in chosen_coords:
            temp_rect = define_rect(coord, block_width)
            if temp_rect.colliderect(my_rect):
                draw_square(temp_rect, screen, cfg.COLORS["black"], dirty_rects)

        # Reset flag for right click
        mouse_right_click = False

    # Perform undo operation for asset drawing
    elif mouse_right_click and len(asset_coords) > 0 and not maze_draw:
        # Get last coordinate
        remove_asset_coord = asset_coords.pop()

        # Set asset coordinate in dictionary to ()
        for asset in asset_defs:
            if asset.get("location") == remove_asset_coord:
                asset["location"] = ()
                break

        # Erase asset on maze by drawing black square
        temp_rect = define_rect(remove_asset_coord, block_width)
        draw_square(temp_rect, screen, cfg.COLORS["black"], dirty_rects)

        # Reset flag for right click
        mouse_right_click = False


# Quit
pygame.quit()
