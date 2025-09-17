import pygame
from grid.utils import invert_maze_to_grid


# Function to determine if adjusted rect position is within legal boundary
# for drawing
def rect_within_boundary(
    my_rect,
    draw_image_x,
    draw_image_y,
    image_boundary,
    maze_width,
    maze_height,
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
            # Diagonal must be equal to least block_width
            # (since grid, no need for square root)
            # Lower left edge
            #    /
            # 0,0
            # 1,0
            if is_edge(subset_grid, row, col, maze_height, maze_width, (-1, 1)):
                if not diag_direction_legal(subset_grid, row, col, maze_width, maze_height, block_width, (1, -1)):
                    return False

            # Upper left edge
            # 1,0
            # 0,0
            #    \
            elif is_edge(subset_grid, row, col, maze_height, maze_width, (-1, -1)):
                if not diag_direction_legal(subset_grid, row, col, maze_width, maze_height, block_width, (1, 1)):
                    return False
            
            # Lower right edge
            # \
            #  0,0
            #  0,1
            elif is_edge(subset_grid, row, col, maze_height, maze_width, (1, 1)):
                if not diag_direction_legal(subset_grid, row, col, maze_width, maze_height, block_width, (-1, -1)):
                    return False
                
            # Upper right edge
            #  0,1
            #  0,0
            # /
            elif is_edge(subset_grid, row, col, maze_height, maze_width, (1, -1)):
                if not diag_direction_legal(subset_grid, row, col, maze_width, maze_height, block_width, (-1, 1)):
                    return False
    return True

# Helper function for edge_diagonals_legal to check if diagonal path starting from an edge is legal
# diag_direction is (x, y) where +x is right and +y is down
def diag_direction_legal(subset_grid, row, col, maze_width, maze_height, block_width, diag_direction):
    diag_width = 1
    found_boundary = False
    found_wall = False
    while not found_wall and not found_boundary:
        if row - diag_width < 0 or col - diag_width < 0 or row + diag_width == maze_height or col + diag_width == maze_width:
            found_boundary = True
        elif subset_grid[row + diag_width*diag_direction[1]][col + diag_width*diag_direction[0]] == 0:
            diag_width += 1
        else:
            found_wall = True
    if diag_width < block_width:
        # Found instance of non-compliant diagonal
        return False
    elif diag_width > block_width and not found_boundary:
        # If opposing edge
        if is_edge(subset_grid, row + diag_width*diag_direction[1], col + diag_width*diag_direction[0], maze_height, maze_width, diag_direction):
            # Found instance of non-compliant diagonal
            return False
    return True
                
# Helper function for diag_direction_legal to check if row, col
# is the first 0 along a diagonal, starting from a wall edge
# (where wall forms a convex 90 degree turn)
# The diag direction points towards the wall edge
def is_edge(subset_grid, row, col, maze_height, maze_width, diag_direction):
    if (
        subset_grid[row][col] == 0
        and row < maze_height - 1
        and row > 0
        and col < maze_width - 1
        and col > 0
        and subset_grid[row][col + diag_direction[0]] == 0
        and subset_grid[row + diag_direction[1]][col] == 0
        and subset_grid[row + diag_direction[1]][col + diag_direction[0]] == 1
    ):
        return True
    return False


# Function to check if path width larger than necessary
# by looking for squares larger than standard block width
def overlayed_squares_legal(subset_grid, block_width):
    if not subset_grid or not subset_grid[0]:
        return False

    rows, cols = len(subset_grid), len(subset_grid[0])

    # dp[i][j] stores the side length of the largest square of 0s
    # with its bottom-right corner at (i, j).
    dp = [[0] * cols for _ in range(rows)]

    # Iterate through the grid to fill the dp table
    for i in range(rows):
        for j in range(cols):
            if subset_grid[i][j] == 0:
                # For the first row and column, the side length is 1
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    # The side length is 1 plus the minimum of the
                    # three adjacent squares' side lengths.
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

                if dp[i][j] > block_width:
                    return False
    return True


# Wrapper function to determine if adjusted rect position will result in a uniform path
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
        overlayed_squares_check = overlayed_squares_legal(subset_grid, block_width)
        # Check diagonal dimensions between edges if the first check passed
        if overlayed_squares_check:
            return edge_diagonals_legal(
                subset_grid, maze_height, maze_width, block_width
            )
        return False

    # No colliding or tangent rects, so nothing to check
    return True
