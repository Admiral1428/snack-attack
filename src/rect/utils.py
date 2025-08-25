import pygame


# Function to define pygame.Rect object based on a center coordinate
def define_rect(current_mouse_pos, block_width):
    # Define pygame.Rect, which is a square with block_width
    # Using central coordinate (x, y) as reference point
    my_rect = pygame.Rect(0, 0, block_width, block_width)
    my_rect.center = current_mouse_pos
    return my_rect


# Function to move desired square to a position which gives a maze
# coordinate divisible by min_block_spacing. This reduced granularity
# makes maze navigation simpler (e.g., stairstep turns) and enables a
# desired maze aesthetic.
def shift_rect_to_divisible_pos(
    my_rect, draw_image_x, draw_image_y, min_block_spacing, image_boundary
):
    top_left = my_rect.topleft
    horz_rem = (top_left[0] - (draw_image_x + image_boundary)) % min_block_spacing
    vert_rem = (top_left[1] - (draw_image_y + image_boundary)) % min_block_spacing

    # If the remainder is less than or equal to half of the spacing,
    # round down to the nearest multiple. Otherwise, round up to the
    # nearest multiple. Finsh by performing shift.

    if horz_rem <= min_block_spacing / 2:
        horz_shift = -horz_rem
    else:
        horz_shift = min_block_spacing - horz_rem

    if vert_rem <= min_block_spacing / 2:
        vert_shift = -vert_rem
    else:
        vert_shift = min_block_spacing - vert_rem

    shifted_rect = my_rect.move(horz_shift, vert_shift)
    return shifted_rect
