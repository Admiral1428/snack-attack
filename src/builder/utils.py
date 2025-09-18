from settings import config as cfg

# Function to scale coordinates
def scale_coords(coords, image_boundary):
    coords_scaled = []
    for coord in coords:
        coords_scaled.append(
            (
                int((coord[0] - cfg.DRAW_IMAGE_X - image_boundary) / cfg.SCALE_FACTOR),
                int((coord[1] - cfg.DRAW_IMAGE_Y - image_boundary) / cfg.SCALE_FACTOR),
            )
        )
    return coords_scaled