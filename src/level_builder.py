import os
import pygame
from rect.utils import define_rect, shift_rect_to_divisible_pos
from rect.draw import draw_square, draw_asset
from grid.utils import invert_maze_to_grid
from fileio.export import (
    export_path_coords_to_csv,
    export_asset_coords_to_csv,
    export_maze_grid_to_txt,
)
from path.utils import (
    rect_within_boundary,
    edge_diagonals_legal,
    overlayed_squares_legal,
    rect_gives_uniform_path,
)


# Clear terminal (Windows syntax)
if os.name == "nt":
    os.system("cls")

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
blue = (0, 0, 255)
magenta = (253, 61, 181)
orange = (255, 128, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
dkgreen = (0, 102, 0)
red = (255, 0, 0)
teal = (0, 168, 168)

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
    "A to end maze and place assets",
    "P to save screenshot",
    "C to export maze to file",
]
for row, text_line in enumerate(text_strings):
    text_surface = font.render(text_line, True, black)
    screen.blit(text_surface, (1140, 100 + row * 50))

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
mouse_left_held = False  # Flag to track if left mouse currently held down
mouse_right_click = False  # Flag to track if right mouse clicked
maze_draw = True  # Flag to track whether maze drawing active
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
            if event.key == pygame.K_p:  # Check if 'p' key is pressed
                screenshot_rect = pygame.Rect(
                    draw_image_x, draw_image_y, 264 * 4, 200 * 4
                )
                sub_surface = screen.subsurface(screenshot_rect)
                pygame.image.save(sub_surface, "level_screenshot.png")
                print("Screenshot saved as level_screenshot.png")
            elif event.key == pygame.K_c:  # Check if 'c' key is pressed
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
            elif event.key == pygame.K_a:  # Check if 'a' key is pressed
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
            selected_color = black
            draw_square(my_rect, screen, selected_color, dirty_rects)

    # Perform undo operation, which requires re-drawing overlapping squares
    elif mouse_right_click and len(chosen_coords) > 0 and maze_draw:
        # Remove last coordinate (undo)
        last_coord = chosen_coords.pop()
        my_rect = define_rect(last_coord, block_width)
        selected_color = teal
        draw_square(my_rect, screen, selected_color, dirty_rects)

        # Draw previous coordinates which were overlapping erased square
        for coord in chosen_coords:
            temp_rect = define_rect(coord, block_width)
            if temp_rect.colliderect(my_rect):
                selected_color = black
                draw_square(temp_rect, screen, selected_color, dirty_rects)
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
        selected_color = black
        draw_square(temp_rect, screen, selected_color, dirty_rects)
        # Reset flag for right click
        mouse_right_click = False


# Quit
pygame.quit()
