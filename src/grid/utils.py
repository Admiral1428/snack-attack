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
        # Adjust for the offset due to image position and boundary, and the
        # height of each block
        grid_x = x - (draw_image_x + image_boundary)
        grid_y = y - (draw_image_y + image_boundary)

        # Mark empty space (0s) where path is defined, using entire block width
        half_width = int(block_width / 2)
        for row in range(grid_y - half_width, grid_y + half_width):
            maze_grid[row][(grid_x - half_width) : (grid_x + half_width)] = [
                0
            ] * block_width

    return maze_grid
