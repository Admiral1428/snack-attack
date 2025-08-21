import pygame
import csv
import time


# Function to define pygame.Rect object based on the mouse position
def define_rect(current_mouse_pos, block_width):
    # Define Rect, which is a square with block_width
    # Using central coordinate for mouse position (x, y) as reference point
    my_rect = pygame.Rect(0, 0, block_width, block_width)
    my_rect.center = current_mouse_pos
    return my_rect


# Function to draw square onto the screen where mouse is pressed
def draw_square(my_rect, selected_color, dirty_rects):
    draw_rect = pygame.draw.rect(screen, selected_color, my_rect)

    dirty_rects.append(draw_rect)

    # Update necessary portion of the screen
    pygame.display.update(dirty_rects)
    dirty_rects.clear()


# Function to determine if adjusted rect position is within legal boundary for drawing
def rect_within_boundary(
    my_rect,
    draw_image_x,
    draw_image_y,
    image_boundary,
    maze_width,
    maze_height,
    block_width,
):
    # Get corners of square that would be drawn
    top_left = my_rect.topleft
    bottom_right = my_rect.bottomright

    # Define rect outside legal area (within teal region)
    legal_rect = pygame.Rect(
        draw_image_x + image_boundary,
        draw_image_y + image_boundary,
        maze_width,
        maze_height,
    )

    # Determine if within teal region
    within_bounds = (
        top_left[0] >= legal_rect.left
        and top_left[1] >= legal_rect.top
        and bottom_right[0] <= legal_rect.right
        and bottom_right[1] <= legal_rect.bottom
    )

    return within_bounds

# Function to check path diagonal width
# Only need to check edges, not corners
def edge_diagonals_legal(subset_grid, maze_height, maze_width, block_width):
    for row in range(maze_height):
        for col in range(maze_width):
            # Diagonal must be equal to least block_width (since grid, no need for square root)
            # Lower left edge
            #    /
            # 0,0
            # 1,0
            if (
                subset_grid[row][col] == 0
                and row < maze_height - 1
                and col > 0
                and subset_grid[row][col - 1] == 0
                and subset_grid[row + 1][col] == 0
                and subset_grid[row + 1][col - 1] == 1
            ):
                diag_width = 1
                found_boundary = False
                found_wall = False
                while not found_wall and not found_boundary:     
                    if row - diag_width < 0 or col + diag_width == maze_width:
                        found_boundary = True
                    elif subset_grid[row - diag_width][col + diag_width] == 0:
                        diag_width += 1
                    else:
                        found_wall = True
                if diag_width < block_width:
                    # Found instance of non-compliant diagonal
                    return False
                elif diag_width > block_width and not found_boundary:
                    # Determine if opposing edge
                    #  0,1
                    #  0,0
                    # /
                    if (
                        subset_grid[row - diag_width][col + diag_width] == 0
                        and row - diag_width > 0
                        and col + diag_width < maze_width - 1
                        and subset_grid[row - diag_width][col + diag_width + 1] == 0
                        and subset_grid[row - diag_width - 1][col + diag_width] == 0
                        and subset_grid[row - diag_width - 1][col + diag_width + 1] == 1
                    ):
                        # Found instance of non-compliant diagonal
                        return False
            # Upper left edge
            # 1,0
            # 0,0
            #    \
            if (
                subset_grid[row][col] == 0
                and row > 0
                and col > 0
                and subset_grid[row][col - 1] == 0
                and subset_grid[row - 1][col] == 0
                and subset_grid[row - 1][col - 1] == 1
            ):
                diag_width = 1
                found_boundary = False
                found_wall = False
                while not found_wall and not found_boundary:     
                    if row + diag_width == maze_height or col + diag_width == maze_width:
                        found_boundary = True
                    elif subset_grid[row + diag_width][col + diag_width] == 0:
                        diag_width += 1
                    else:
                        found_wall = True
                if diag_width < block_width:
                    # Found instance of non-compliant diagonal
                    return False
                elif diag_width > block_width and not found_boundary:
                    # Determine if opposing edge
                    # \
                    #  0,0
                    #  0,1
                    if (
                        subset_grid[row + diag_width][col + diag_width] == 0
                        and row + diag_width < maze_height - 1
                        and col + diag_width < maze_width - 1
                        and subset_grid[row + diag_width][col + diag_width + 1] == 0
                        and subset_grid[row + diag_width + 1][col + diag_width] == 0
                        and subset_grid[row + diag_width + 1][col + diag_width + 1] == 1
                    ):
                        # Found instance of non-compliant diagonal
                        return False
            # Lower right edge
            # \
            #  0,0
            #  0,1
            if (
                subset_grid[row][col] == 0
                and row < maze_height - 1
                and col < maze_width - 1
                and subset_grid[row][col + 1] == 0
                and subset_grid[row + 1][col] == 0
                and subset_grid[row + 1][col + 1] == 1
            ):
                diag_width = 1
                found_boundary = False
                found_wall = False
                while not found_wall and not found_boundary:     
                    if row - diag_width < 0 or col - diag_width < 0:
                        found_boundary = True
                    elif subset_grid[row - diag_width][col - diag_width] == 0:
                        diag_width += 1
                    else:
                        found_wall = True                    
                if diag_width < block_width:
                    # Found instance of non-compliant diagonal
                    return False
                elif diag_width > block_width and not found_boundary:
                    # Determine if opposing edge
                    # 1,0
                    # 0,0
                    #    \
                    if (
                        subset_grid[row - diag_width][col - diag_width] == 0
                        and row - diag_width > 0
                        and col - diag_width > 0
                        and subset_grid[row - diag_width][col - diag_width - 1] == 0
                        and subset_grid[row - diag_width - 1][col - diag_width] == 0
                        and subset_grid[row - diag_width - 1][col - diag_width - 1] == 1
                    ):
                        # Found instance of non-compliant diagonal
                        return False
            # Upper right edge
            #  0,1
            #  0,0
            # /
            if (
                subset_grid[row][col] == 0
                and row > 0
                and col < maze_width - 1
                and subset_grid[row][col + 1] == 0
                and subset_grid[row - 1][col] == 0
                and subset_grid[row - 1][col + 1] == 1
            ):
                diag_width = 1
                found_boundary = False
                found_wall = False
                while not found_wall and not found_boundary:     
                    if row + diag_width == maze_height or col - diag_width < 0:
                        found_boundary = True
                    elif subset_grid[row + diag_width][col - diag_width] == 0:
                        diag_width += 1
                    else:
                        found_wall = True
                if diag_width < block_width:
                    # Found instance of non-compliant diagonal                 
                    return False
                elif diag_width > block_width and not found_boundary:
                    # Determine if opposing edge
                    #    /
                    # 0,0
                    # 1,0
                    if (
                        subset_grid[row + diag_width][col - diag_width] == 0
                        and row + diag_width < maze_height - 1
                        and col - diag_width > 0
                        and subset_grid[row + diag_width][col - diag_width - 1] == 0
                        and subset_grid[row + diag_width + 1][col - diag_width] == 0
                        and subset_grid[row + diag_width + 1][col - diag_width - 1] == 1
                    ):
                        # Found instance of non-compliant diagonal
                        return False                        
    return True

# Function to check if path width larger than necessary
# by looking for squares larger than standard block width
def overlayed_squares_legal(subset_grid, maze_height, maze_width, block_width):
    for row in range(maze_height - block_width):
        for col in range(maze_width - block_width):
            if subset_grid[row][col:col+block_width+1] == [0] * (block_width + 1):
                found_wall = False
                calc_height = 1
                while not found_wall and (row + calc_height) < maze_height and calc_height <= block_width:
                    # Since we are iterating from 0th row and 0th col, just check downwards
                    if subset_grid[row + calc_height][col:col+block_width+1] == [0] * (block_width + 1):
                        # This section should not be considered again in next search, so fill it in
                        subset_grid[row + calc_height][col:col+block_width+1] == [1] * (block_width + 1)
                        # Since zeros found, increment height of the discovered path area
                        calc_height += 1                    
                    else:
                        found_wall = True
                if calc_height > block_width:
                    # Found instance of square fitting into path which is too large
                    return False
    return True

# Function to determine if adjusted rect position will result in a uniform path
def rect_gives_uniform_path(
    coords,
    my_rect,
    maze_width,
    maze_height,
    draw_image_x,
    draw_image_y,
    image_boundary,
    block_width,
):
    # Use blocks which collide with or are tangent to desired block
    # Determine tangency by increasing size of current block temporarily
    my_rect_tangent = pygame.Rect(0, 0, block_width + 2, block_width + 2)
    my_rect_tangent.center = my_rect.center

    colliding_rects = [my_rect.center]
    for coord in coords:
        temp_rect = pygame.Rect(0, 0, block_width, block_width)
        temp_rect.center = coord
        if my_rect_tangent.colliderect(temp_rect):
            colliding_rects.append(coord)

    # If colliding or tangent rects were detected:
    if len(colliding_rects) > 1:
        subset_grid = invert_maze_to_grid(
            colliding_rects,
            maze_width,
            maze_height,
            draw_image_x,
            draw_image_y,
            image_boundary,
            block_width,
        )

        # Check if rectangular regions exist which exceed block width
        overlayed_squares_check = overlayed_squares_legal(subset_grid, maze_height, maze_width, block_width)
        # Check diagonal dimensions between edges if the first check passed
        if overlayed_squares_check:
            return edge_diagonals_legal(subset_grid, maze_height, maze_width, block_width)
        return False
        # start_time = time.time()

        # end_time = time.time()
        # elapsed_time = end_time - start_time

        # print(f"Time elapsed: {elapsed_time:.4f} seconds")

    # No colliding or tangent rects, so nothing to check
    return True


# Function to move desired square to a position which gives a maze coordinate divisible by min_block_spacing
# This reduced granularity makes maze navigation simpler (e.g., stairstep turns)
def shift_rect_to_divisible_pos(my_rect, draw_image_x, draw_image_y, min_block_spacing):
    # Get corners of square that would be drawn
    top_left = my_rect.topleft

    # Determine remainder to get vertical shift.
    vert_shift = (top_left[1] - draw_image_y - image_boundary) % min_block_spacing

    # Determine remainder to get horizontal shift.
    horz_shift = (top_left[0] - draw_image_x - image_boundary) % min_block_spacing

    # Perform shift based on calculated remainders
    shifted_rect = my_rect.move(-horz_shift, -vert_shift)
    return shifted_rect


# Function to export coordinates to csv file
def export_path_coords_to_csv(coords):
    with open("level_coordinates.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["X", "Y"])  # Write header row
        writer.writerows(coords)


# Function to turn maze into grid (invert representation)
def invert_maze_to_grid(
    coords,
    maze_width,
    maze_height,
    draw_image_x,
    draw_image_y,
    image_boundary,
    block_width,
):
    # Initially all walls (1s)
    maze_grid = [[1] * maze_width for _ in range(maze_height)]

    for x, y in coords:
        # Adjust for the offset due to image position and boundary, and the height of each block
        grid_x = x - (draw_image_x + image_boundary)
        grid_y = y - (draw_image_y + image_boundary)

        # Mark empty space (0s) where path is defined, using entire block width
        half_width = int(block_width / 2)
        for row in range(grid_y - half_width, grid_y + half_width):
            maze_grid[row][(grid_x - half_width) : (grid_x + half_width)] = [
                0
            ] * block_width

    return maze_grid


# Funtion to draw maze grid to text file
def export_maze_grid_to_txt(maze_grid):
    f = open("level_grid.txt", "w")
    for row in maze_grid:
        row_str = ",".join(map(str, row))
        f.write(row_str + "\n")  # Add a newline after each row
    f.close()


# Initialize pygame modules
pygame.init()
pygame.font.init()

# Use Arial text
font = pygame.font.SysFont("Arial", 30)

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
    "P to save screenshot",
    "C to export coordinates to file",
]
for row, text_line in enumerate(text_strings):
    text_surface = font.render(text_line, True, black)
    screen.blit(text_surface, (1150, 100 + row * 50))

# Update initial display
pygame.display.update()

# List of dirty rectangles, representing areas of screen to be updated
dirty_rects = []

# List of mouse coordinates that have been added
chosen_coords = []

# Game loop
mouse_left_held = False  # Flag to track if left mouse currently held down
mouse_right_click = False  # Flag to track if right mouse clicked
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
                export_path_coords_to_csv(chosen_coords)
                print("Level coordinates saved as level_coordinates.csv")
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

    # Check if the left mouse is currently held down (outside of event loop)
    # If so, draw a new square at that location, if shifted to nearest nth
    # coordinate is deemed legal (based on min_block_spacing)
    if mouse_left_held:
        current_mouse_pos = pygame.mouse.get_pos()

        my_rect = define_rect(current_mouse_pos, block_width)
        my_rect = shift_rect_to_divisible_pos(
            my_rect, draw_image_x, draw_image_y, min_block_spacing
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
            draw_square(my_rect, selected_color, dirty_rects)

    # Perform undo operation, which requires re-drawing overlapping squares
    elif mouse_right_click and len(chosen_coords) > 0:
        # Remove last coordinate (undo)
        last_coord = chosen_coords.pop()
        my_rect = define_rect(last_coord, block_width)
        selected_color = teal
        draw_square(my_rect, selected_color, dirty_rects)

        # Draw previous coordinates which were overlapping erased square
        for coord in chosen_coords:
            temp_rect = define_rect(coord, block_width)
            if temp_rect.colliderect(my_rect):
                selected_color = black
                draw_square(temp_rect, selected_color, dirty_rects)

        mouse_right_click = False


# Quit
pygame.quit()
