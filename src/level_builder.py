import os
import pygame
import time
import tkinter as tk
from tkinter import messagebox, filedialog
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
width, height = (1600, 900)
screen = pygame.display.set_mode((width, height))

# Define maze properties
maze_width_unscaled = 256
maze_height_unscaled = 192
block_width_unscaled = 12
min_block_spacing = 4
draw_image_x = 20
draw_image_y = 20
image_boundary = 4

# Set window title
pygame.display.set_caption("Level Builder")

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
ltgray = (212, 212, 212)

# Create a list of colors to be used for selecting maze wall color
maze_colors = [teal, yellow, orange, green, dkgreen, purple, magenta, red, blue, gray]
maze_color_index = 0

# Scale variables
scale_factor = 4
maze_width = maze_width_unscaled * scale_factor
maze_height = maze_height_unscaled * scale_factor
block_width = block_width_unscaled * scale_factor
min_block_spacing *= scale_factor
image_boundary *= scale_factor

# Fill background with white color
screen.fill(white)

# Draw empty maze onto screen, with a gray boundary
# and inside drawable teal area
draw_maze(
    draw_image_x,
    draw_image_y,
    image_boundary,
    maze_width,
    maze_height,
    block_width,
    ltgray,
    ltgray,
    [],
    screen,
    0,
)
draw_maze(
    draw_image_x + image_boundary,
    draw_image_y + image_boundary,
    0,
    maze_width,
    maze_height,
    block_width,
    teal,
    teal,
    [],
    screen,
    0,
)

# Display instruction text
text_strings = [
    "Left click or use arrow keys to",
    "draw maze. Right click to undo.",
    "",
    "W to cycle wall color",
    "A to end maze and place assets",
    "P to save screenshot",
    "F to cycle level speed:",
    "",
    "J to cycle # corn enemies",
    "K to cycle # tomato enemies",
    "L to cycle # pumpkin enemies",
]
for row, text_line in enumerate(text_strings):
    if row <= 7:
        selected_color = black
    elif row == 8:
        selected_color = dkgreen
    elif row == 9:
        selected_color = red
    else:
        selected_color = orange
    text_surface = font.render(text_line, True, selected_color)
    screen.blit(text_surface, (1140, 50 + row * 50))


# Initialize number of enemies
corn_quantities = range(9)
tomato_quantities = range(7)
pumpkin_quantities = range(5)
corn_index = 0
tomato_index = 0
pumpkin_index = 0


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

corn_image = images["corn"]
tomato_image = images["tomato"]
pumpkin_image = images["pumpkin"]

# Initialize level speed (slow, medium, fast, frantic)
level_speeds = ["slow", "medium", "fast", "frantic"]
level_speed_index = 0

# Display level speed in blue color
# Display new number
text_surface = font.render(str(level_speeds[level_speed_index]), True, blue)
screen.blit(text_surface, (1450, 350))

# Display enemy images
screen.blit(corn_image, (1150, 700))
screen.blit(tomato_image, (1290, 700))
screen.blit(pumpkin_image, (1430, 700))

# Display number of enemies below each image
text_surface = font.render(str(corn_quantities[corn_index]), True, dkgreen)
screen.blit(text_surface, (1165, 760))
text_surface = font.render(str(tomato_quantities[tomato_index]), True, red)
screen.blit(text_surface, (1305, 760))
text_surface = font.render(str(pumpkin_quantities[pumpkin_index]), True, orange)
screen.blit(text_surface, (1445, 760))

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
            if event.key == pygame.K_p:
                screenshot_rect = pygame.Rect(
                    draw_image_x,
                    draw_image_y,
                    maze_width + 2 * image_boundary,
                    maze_height + 2 * image_boundary,
                )
                sub_surface = screen.subsurface(screenshot_rect)
                if maze_draw:
                    screenshot_name = "level_screenshot_no_assets.png"
                else:
                    screenshot_name = "level_screenshot.png"
                pygame.image.save(sub_surface, screenshot_name)
                print(f"Screenshot saved as {screenshot_name}")
            elif event.key == pygame.K_c and not maze_draw:
                # Warning to user that final export will need all assets
                if len(asset_coords) < 8:
                    messagebox.showinfo(
                        "Warning",
                        "Ensure all assets are placed before final export!\n\n"
                        "If there is insufficient space, it may be necessary to exit and restart the drawing.\n\n"
                        "Click OK then click back onto Level Builder window.",
                    )
                else:
                    # Export path coordinates to csv
                    export_path_coords_to_csv(
                        chosen_coords, draw_image_x, draw_image_y, image_boundary
                    )
                    print("Level coordinates saved as level_path_coordinates.csv")
                    # Export asset coordinates to csv if applicable
                    if asset_defs:
                        export_asset_coords_to_csv(
                            asset_defs, draw_image_x, draw_image_y, image_boundary
                        )
                        print("Asset coordinates saved as level_asset_coordinates.csv")
                    # Export maze metadata to csv
                    # Maze metadata
                    maze_metadata = {
                        "maze_color": maze_colors[maze_color_index],
                        "level_speed": level_speeds[level_speed_index],
                        "corn_quantity": corn_quantities[corn_index],
                        "tomato_quantity": tomato_quantities[tomato_index],
                        "pumpkin_quantity": pumpkin_quantities[pumpkin_index],
                    }
                    export_metadata(maze_metadata)
                    print("Maze metadata saved as level_metadata.csv")

                    # Move maze files to a selected directory
                    messagebox.showinfo(
                        "Instructions",
                        "Please create a new folder"
                        " at the location shown in the next dialog box, then select that "
                        "new folder.\n\nUse a folder name such as custom_map_01."
                        "\n\nClick OK to proceed.",
                    )
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
                    draw_image_x + image_boundary,
                    draw_image_y + image_boundary,
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
                if level_speed_index >= len(level_speeds) - 1:
                    level_speed_index = 0
                else:
                    level_speed_index += 1
                # Erase displayed speed
                temp_rect = pygame.Rect(1450, 350, 400, 100)
                draw_square(temp_rect, screen, white, dirty_rects)
                # Display new number
                text_surface = font.render(
                    str(level_speeds[level_speed_index]), True, blue
                )
                screen.blit(text_surface, (1450, 350))
                pygame.display.update()
            elif event.key == pygame.K_j and maze_draw:
                # Cycle corn quantity
                if corn_index >= len(corn_quantities) - 1:
                    corn_index = 0
                else:
                    corn_index += 1
                # Erase displayed number
                temp_rect = define_rect((1170, 780), block_width)
                draw_square(temp_rect, screen, white, dirty_rects)
                # Display new number
                text_surface = font.render(
                    str(corn_quantities[corn_index]), True, dkgreen
                )
                screen.blit(text_surface, (1165, 760))
                pygame.display.update()
            elif event.key == pygame.K_k and maze_draw:
                # Cycle tomato quantity
                if tomato_index >= len(tomato_quantities) - 1:
                    tomato_index = 0
                else:
                    tomato_index += 1
                # Erase displayed number
                temp_rect = define_rect((1310, 780), block_width)
                draw_square(temp_rect, screen, white, dirty_rects)
                # Display new number
                text_surface = font.render(
                    str(tomato_quantities[tomato_index]), True, red
                )
                screen.blit(text_surface, (1305, 760))
                pygame.display.update()
            elif event.key == pygame.K_l and maze_draw:
                # Cycle pumpkin quantity
                if pumpkin_index >= len(pumpkin_quantities) - 1:
                    pumpkin_index = 0
                else:
                    pumpkin_index += 1
                # Erase displayed number
                temp_rect = define_rect((1450, 780), block_width)
                draw_square(temp_rect, screen, white, dirty_rects)
                # Display new number
                text_surface = font.render(
                    str(pumpkin_quantities[pumpkin_index]), True, orange
                )
                screen.blit(text_surface, (1445, 760))
                pygame.display.update()
            elif event.key == pygame.K_a:
                # Coarsen inputs prior to creating maze grid to optimize runtime
                coords_scaled = []
                for coord in chosen_coords:
                    coords_scaled.append(
                        (
                            int(
                                (coord[0] - draw_image_x - image_boundary)
                                / scale_factor
                            ),
                            int(
                                (coord[1] - draw_image_y - image_boundary)
                                / scale_factor
                            ),
                        )
                    )

                # Create maze grid
                my_maze = invert_maze_to_grid(
                    coords_scaled,
                    maze_width_unscaled,
                    maze_height_unscaled,
                    0,
                    0,
                    0,
                    block_width_unscaled,
                )
                # Determine how many full squares reside in maze
                num_maze_squares = grid_space(my_maze) / (block_width_unscaled**2)
                # Create warning message if path space deemed too sparse
                if num_maze_squares < 8:
                    messagebox.showinfo(
                        "Warning",
                        "Maze has insufficient space for assets.\n\n"
                        "Path area must equal at least 8 full squares.\n\n"
                        "Click OK then click back onto Level Builder window.",
                    )
                else:
                    # Flag for discontinuing maze drawing
                    maze_draw = False
                    # Overwrite old text
                    right_rect = pygame.Rect(1140, 50, width - 1140, height - 50)
                    screen.fill(white, right_rect)
                    # Display instruction text
                    text_strings = [
                        "Key (see list below) to place",
                        "asset at cursor location",
                        "Right click to undo",
                        "P to save screenshot",
                        "C to export maze to files",
                    ]
                    for row, text_line in enumerate(text_strings):
                        text_surface = font.render(text_line, True, black)
                        if row == 1:
                            screen.blit(text_surface, (1140, 100 + row * 40))
                        else:
                            screen.blit(text_surface, (1140, 100 + row * 50))
                    # List of asset choices
                    black_rect = pygame.Rect(1130, 390, 330, 260)
                    screen.fill(black, black_rect)
                    asset_defs = [
                        {
                            "letter": "S",
                            "description": "Player start location",
                            "color": green,
                            "location": (),
                        },
                        {
                            "letter": "R",
                            "description": "Player respawn location",
                            "color": dkgreen,
                            "location": (),
                        },
                        {
                            "letter": "E",
                            "description": "Enemy start location",
                            "color": red,
                            "location": (),
                        },
                        {
                            "letter": "1",
                            "description": "Item 1 location",
                            "color": blue,
                            "location": (),
                        },
                        {
                            "letter": "2",
                            "description": "Item 2 location",
                            "color": magenta,
                            "location": (),
                        },
                        {
                            "letter": "3",
                            "description": "Item 3 location",
                            "color": orange,
                            "location": (),
                        },
                        {
                            "letter": "4",
                            "description": "Item 4 location",
                            "color": yellow,
                            "location": (),
                        },
                        {
                            "letter": "H",
                            "description": "Exit location",
                            "color": white,
                            "location": (),
                        },
                    ]
                    asset_letters = [asset["letter"].lower() for asset in asset_defs]
                    for index, asset in enumerate(asset_defs):
                        screen.blit(
                            font_small.render(
                                asset["letter"] + ": " + asset["description"],
                                True,
                                asset["color"],
                            ),
                            (1140, 400 + index * 30),
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
                        draw_image_x,
                        draw_image_y,
                        image_boundary,
                        min_block_spacing,
                        block_width,
                        matching_asset[0].get("letter"),
                        matching_asset[0].get("color"),
                        black,
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
                    draw_image_x + image_boundary + int(block_width / 2),
                    draw_image_y + image_boundary + int(block_width / 2),
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
            my_rect, draw_image_x, draw_image_y, min_block_spacing, image_boundary
        )

        # If chosen coordinate from arrow keys is already in chosen coordinates,
        # save that space so that user can backtrack.
        # Subsequently highlight the block with flashing so that they know where
        # they are for context.
        if arrow_pressed and my_rect.center in chosen_coords:
            arrow_index = chosen_coords.index(my_rect.center)
            for i in range(3):
                draw_square(my_rect, screen, white, dirty_rects)
                time.sleep(1 / 30)
                draw_square(my_rect, screen, black, dirty_rects)
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
                    int((coord[0] - draw_image_x - image_boundary) / scale_factor),
                    int((coord[1] - draw_image_y - image_boundary) / scale_factor),
                )
            )
        new_center = (
            int((my_rect.center[0] - draw_image_x - image_boundary) / scale_factor),
            int((my_rect.center[1] - draw_image_y - image_boundary) / scale_factor),
        )
        my_rect_scaled = define_rect(new_center, block_width_unscaled)

        # Check to make sure the current shifted position is not the same as
        # the last, and that it's not in chosen coords. If all criteria met,
        # draw the new path square
        if (
            not shifted_coords_history or my_rect.center != shifted_coords_history[-1]
        ) and my_rect.center not in chosen_coords:
            shifted_coords_history.append(my_rect.center)
            
            
            if rect_within_boundary(
                my_rect,
                draw_image_x,
                draw_image_y,
                image_boundary,
                maze_width,
                maze_height,
            ) and rect_gives_uniform_path(
                coords_scaled,
                my_rect_scaled,
                maze_width_unscaled,
                maze_height_unscaled,
                0,
                0,
                0,
                block_width_unscaled,
            ):
                # Add updated mouse position to list of previous points
                chosen_coords.append((my_rect.center))
                draw_square(my_rect, screen, black, dirty_rects)

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
                draw_square(temp_rect, screen, black, dirty_rects)
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
        draw_square(temp_rect, screen, black, dirty_rects)
        # Reset flag for right click
        mouse_right_click = False


# Quit
pygame.quit()
