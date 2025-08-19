import pygame


# Function to define pygame.Rect object based on the mouse position
def define_rect(current_mouse_pos):
    # Define Rect, which is 48 pixels by 48 pixels
    # Using central coordinate for mouse position (x, y) as reference point
    my_rect = pygame.Rect(current_mouse_pos[0] - 23, current_mouse_pos[1] - 23, 48, 48)
    return my_rect


# Function to draw square onto the screen where mouse is pressed
def draw_square(my_rect, selected_color):
    pygame.draw.rect(screen, selected_color, my_rect)
    return my_rect


# Function to determine if mouse position results in block within legal boundary
def mouse_position_legal(my_rect):
    # Get corners of square that would be drawn
    top_left = my_rect.topleft
    bottom_right = my_rect.bottomright

    # Define one outside legal area (within cyan region)
    legal_rect = pygame.Rect(20 + 16, 20 + 16, 256 * 4, 192 * 4)

    # Determine if within cyan region
    within_bounds = (
        top_left[0] >= legal_rect.left
        and top_left[1] >= legal_rect.top
        and bottom_right[0] <= legal_rect.right
        and bottom_right[1] <= legal_rect.bottom
    )
    return within_bounds


# Function to move desired block to a position which gives a maze coordinate divisible by 16
# This reduced granularity makes maze navigation simpler (e.g., stairstep turns)
def shift_rect_to_divisible_pos(my_rect):
    # Get corners of square that would be drawn
    top_left = my_rect.topleft

    # Determine remainder to get vertical shift.
    vert_shift = (top_left[1] - 20 - 16) % 16

    # Determine remainder to get horizontal shift.
    horz_shift = (top_left[0] - 20 - 16) % 16

    # Perform shift based on calculated remainders
    shifted_rect = my_rect.move(-horz_shift, -vert_shift)
    return shifted_rect


# Initialize pygame modules
pygame.init()
pygame.font.init()

# Use Arial text
font = pygame.font.SysFont("Arial", 30)

# Dimensions for window
width, height = (1600, 900)
screen = pygame.display.set_mode((width, height))

# Set window title
pygame.display.set_caption("Level Builder")

# Load template image used for defining drawable area
original_image = pygame.image.load("images/outline_template.png").convert_alpha()

# Scale template image
scale_factor = 4
scaled_image = pygame.transform.scale(
    original_image,
    (
        int(original_image.get_width() * scale_factor),
        int(original_image.get_height() * scale_factor),
    ),
)

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
teal = (0, 168, 168)

# Fill background with white color
screen.fill(white)

# Blit the scaled image onto the original screen
screen.blit(scaled_image, (20, 20))

# Display instruction text
text_strings = [
    "Left click to draw maze",
    "Right click to erase",
    "P to save screenshot",
]
for row, text_line in enumerate(text_strings):
    text_surface = font.render(text_line, True, black)
    screen.blit(text_surface, (1200, 100 + row * 50))

# Update initial display
pygame.display.update()

# Game loop
mouse_left_held = False  # Flag to track if left mouse currently held down
mouse_right_held = False  # Flag to track if right mouse currently held down
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
                mouse_right_held = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                mouse_left_held = False
            elif event.button == 3:  # Right mouse button
                mouse_right_held = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Check if 'p' key is pressed
                screenshot_rect = pygame.Rect(20, 20, 264 * 4, 200 * 4)
                sub_surface = screen.subsurface(screenshot_rect)
                pygame.image.save(sub_surface, "level_screenshot.png")
                print("Screenshot saved as level_screenshot.png")

    # List of dirty rectangles, representing areas of screen to be updated
    dirty_rects = []

    # Check if the mouse is currently held down (outside of event loop)
    if mouse_left_held or mouse_right_held:
        current_mouse_pos = pygame.mouse.get_pos()

        my_rect = define_rect(current_mouse_pos)
        my_rect = shift_rect_to_divisible_pos(my_rect)

        if mouse_position_legal(my_rect):
            # Print clicked mouse position for debugging purposes
            # print(f"Mouse held at: {current_mouse_pos}")

            # Draw black path if left mouse (draw) or cyan path if right mouse (erase)
            selected_color = (
                black if mouse_left_held else teal if mouse_right_held else None
            )

            draw_rect = draw_square(my_rect, selected_color)
            dirty_rects.append(draw_rect)

            # Update necessary portion of the screen
            pygame.display.update(dirty_rects)
            dirty_rects.clear()

# Quit
pygame.quit()
