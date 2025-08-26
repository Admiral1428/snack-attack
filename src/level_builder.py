import os
import pygame
import tkinter as tk
from tkinter import messagebox
from rect.utils import define_rect, shift_rect_to_divisible_pos
from rect.draw import draw_square, draw_asset
from grid.utils import invert_maze_to_grid, grid_space
from fileio.export import (
    export_path_coords_to_csv,
    export_asset_coords_to_csv,
    export_maze_grid_to_txt,
    export_metadata,
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

# Use Arial text
font = pygame.font.SysFont("Arial", 30)
font_small = pygame.font.SysFont("Arial", 26)

# Dimensions for window
width, height = (1600, 900)
screen = pygame.display.set_mode((width, height))

# Define maze properties
maze_width = 256
maze_height = 192
block_width = 12
min_block_spacing = 4
draw_image_x = 20
draw_image_y = 20
image_boundary = 4

# Set window title
pygame.display.set_caption("Level Builder")

# Load template image used for defining drawable area
original_image = pygame.image.load("../assets/outline_template.png").convert_alpha()

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
maze_color_index = 0

# Scale template image and variables
scale_factor = 4
scaled_image = pygame.transform.scale(
    original_image,
    (
        int(original_image.get_width() * scale_factor),
        int(original_image.get_height() * scale_factor),
    ),
)
maze_width *= scale_factor
maze_height *= scale_factor
block_width *= scale_factor
min_block_spacing *= scale_factor
image_boundary *= scale_factor

# Fill background with white color
screen.fill(white)

# Blit the scaled image onto the original screen
screen.blit(scaled_image, (draw_image_x, draw_image_y))

# Display instruction text
text_strings = [
    "Left click to draw maze",
    "Right click to undo",
    "W to cycle wall color",
    "A to end maze and place assets",
    "P to save screenshot",
    "C to export maze to file",
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
    screen.blit(text_surface, (1140, 100 + row * 50))


# Initialize number of enemies
corn_quantities = range(9)
tomato_quantities = range(7)
pumpkin_quantities = range(5)
corn_index = 0
tomato_index = 0
pumpkin_index = 0

# Load enemy images and scale them
corn_image = pygame.image.load("../assets/sprites/corn.png").convert_alpha()
tomato_image = pygame.image.load("../assets/sprites/tomato.png").convert_alpha()
pumpkin_image = pygame.image.load("../assets/sprites/pumpkin.png").convert_alpha()
corn_image = pygame.transform.scale(
    corn_image,
    (
        int(corn_image.get_width() * scale_factor),
        int(corn_image.get_height() * scale_factor),
    ),
)
tomato_image = pygame.transform.scale(
    tomato_image,
    (
        int(tomato_image.get_width() * scale_factor),
        int(tomato_image.get_height() * scale_factor),
    ),
)
pumpkin_image = pygame.transform.scale(
    pumpkin_image,
    (
        int(pumpkin_image.get_width() * scale_factor),
        int(pumpkin_image.get_height() * scale_factor),
    ),
)

# Initialize level speed (slow, medium, fast)
level_speeds = ["slow", "medium", "fast"]
level_speed_index = 0

# Display level speed in blue color
# Display new number
text_surface = font.render(str(level_speeds[level_speed_index]), True, blue)
screen.blit(text_surface, (1450, 400))

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

# List of assets and asset coordinates that have been added
asset_defs = []
asset_coords = []


# Game loop
mouse_left_held = False
mouse_right_click = False
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
            if event.key == pygame.K_p:
                screenshot_rect = pygame.Rect(
                    draw_image_x,
                    draw_image_y,
                    maze_width + 2 * image_boundary,
                    maze_height + 2 * image_boundary,
                )
                sub_surface = screen.subsurface(screenshot_rect)
                pygame.image.save(sub_surface, "level_screenshot.png")
                print("Screenshot saved as level_screenshot.png")
            elif event.key == pygame.K_c:
                # Warning to user that final export will need assets
                if maze_draw:
                     messagebox.showinfo("Warning", "Ensure all assets are placed before final export! Click OK then click back onto Level Builder window.")
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
                # Create maze grid and export to text file
                my_maze = invert_maze_to_grid(
                    chosen_coords,
                    maze_width,
                    maze_height,
                    draw_image_x,
                    draw_image_y,
                    image_boundary,
                    block_width,
                )
                export_maze_grid_to_txt(my_maze)
                print("Level grid saved as level_grid.txt")
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
                temp_rect = pygame.Rect(1450, 400, 400, 100)
                draw_square(temp_rect, screen, white, dirty_rects)
                # Display new number
                text_surface = font.render(
                    str(level_speeds[level_speed_index]), True, blue
                )
                screen.blit(text_surface, (1450, 400))
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
                # Create maze grid
                my_maze = invert_maze_to_grid(
                    chosen_coords,
                    maze_width,
                    maze_height,
                    draw_image_x,
                    draw_image_y,
                    image_boundary,
                    block_width,
                )
                # Determine how many full squares reside in maze
                num_maze_squares = grid_space(my_maze)/(block_width ** 2)
                # Create warning message if path space deemed too sparse
                if num_maze_squares < 8:
                     messagebox.showinfo("Warning", "Maze has insufficient space for assets, so a re-draw may be required. Click OK then click back onto Level Builder window.")
                # Flag for discontinuing maze drawing
                maze_draw = False
                # Overwrite old text
                right_rect = pygame.Rect(1140, 100, width - 1140, height - 100)
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

    # Check if the left mouse is currently held down (outside of event loop)
    # If so, draw a new square at that location, if shifted to nearest nth
    # coordinate is deemed legal (based on min_block_spacing)
    if mouse_left_held and maze_draw:
        current_mouse_pos = pygame.mouse.get_pos()

        my_rect = define_rect(current_mouse_pos, block_width)
        my_rect = shift_rect_to_divisible_pos(
            my_rect, draw_image_x, draw_image_y, min_block_spacing, image_boundary
        )

        if (
            my_rect.center not in chosen_coords
            and rect_within_boundary(
                my_rect,
                draw_image_x,
                draw_image_y,
                image_boundary,
                maze_width,
                maze_height,
                block_width,
            )
            and rect_gives_uniform_path(
                chosen_coords,
                my_rect,
                maze_width,
                maze_height,
                draw_image_x,
                draw_image_y,
                image_boundary,
                block_width,
            )
        ):
            # Add updated mouse position to list of previous points
            chosen_coords.append((my_rect.center))
            draw_square(my_rect, screen, black, dirty_rects)

    # Perform undo operation, which requires re-drawing overlapping squares
    elif mouse_right_click and len(chosen_coords) > 0 and maze_draw:
        # Remove last coordinate (undo)
        last_coord = chosen_coords.pop()
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
