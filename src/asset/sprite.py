import pygame
import time
from collections import deque
from rect.utils import define_rect


# Class to define a sprite and its methods
class Sprite:
    def __init__(
        self, name, image, center_position, speed, can_rotate, hitbox_width, path_width
    ):
        self.name = name
        self.image = image
        self.center_position = center_position
        self.speed = speed  # pixels per second
        self.can_rotate = can_rotate
        self.hitbox_rect = define_rect(center_position, hitbox_width)
        self.path_rect = define_rect(center_position, path_width)

        self.rotation_angle = 0  # + counterclockwise
        self.mirror = False
        self.destroyed = False
        self.center_pos_decimal = center_position
        self.direction = (0, 0)
        self.desired_direction = ()
        self.motion_vector = (0, 0)
        self.motion_vector_history = deque(maxlen=1)
        self.animation_start_time = None
        self.animation_sequence = []
        self.animation_index = 0

    # Method to perform shifting to desired location
    def shift(self, delta_x, delta_y):
        self.hitbox_rect.move_ip(delta_x, delta_y)
        self.path_rect.move_ip(delta_x, delta_y)
        self.center_position = (
            self.center_position[0] + delta_x,
            self.center_position[1] + delta_y,
        )
        # Set the partial position equal to the new position
        self.center_pos_decimal = (self.center_position[0], self.center_position[1])

    # Method to move the asset with associated motion vector and orientation operations
    def move(self, delta_x, delta_y):
        if delta_x != 0 or delta_y != 0:
            # Initialize flag, only to be used if motion vector changes
            orientation_check = False
            # Store current motion vector if new one is different
            if not self.motion_vector_history or self.motion_vector != (
                delta_x,
                delta_y,
            ):
                self.motion_vector_history.append(self.motion_vector)
                orientation_check = True
            # Shift Rect objects and position
            self.shift(delta_x, delta_y)
            # Set new motion vector
            self.motion_vector = (delta_x, delta_y)
            # Determine new orientation if motion vector changed
            if orientation_check:
                self.set_orientation()

    # Method to check if the asset can move within maze
    # Note that pygame.Rect not inclusive of bottom or right
    def can_move(self, delta_x, delta_y, maze_grid):
        temp_rect = self.path_rect.move(delta_x, delta_y)
        topleft = temp_rect.topleft
        botright = temp_rect.bottomright
        # Check if within bounds of maze
        if (
            topleft[0] < 0
            or (botright[0] - 1) > (len(maze_grid[0]) - 1)
            or topleft[1] < 0
            or (botright[1] - 1) > (len(maze_grid) - 1)
        ):
            return False
        # Check if rect intersects with maze wall
        for col in range(topleft[0], botright[0]):
            for row in range(topleft[1], botright[1]):
                if maze_grid[row][col] == 1:
                    return False
        return True

    # Determine and perform move based on direction, move check, time, and speed
    def perform_move(self, maze_grid, game_dt):
        # If nonzero direction was commanded and is possible, move
        if self.desired_direction and self.can_move(
            self.desired_direction[0], self.desired_direction[1], maze_grid
        ):
            # Don't override current direction if commanded was (0, 0),
            # that way previous direction can be attempted if the next
            # commanded direction is not possible
            if self.desired_direction == (0, 0):
                self.move(0, 0)
            else:
                self.direction = (self.desired_direction[0], self.desired_direction[1])
                # Perform move if the new position rounds to the nearest pixel
                if self.shift_threshold_met(game_dt):
                    self.move(self.direction[0], self.direction[1])
        # If current direction is possible, keep moving that way
        elif self.can_move(self.direction[0], self.direction[1], maze_grid):
            # Perform move if the new position rounds to the nearest pixel
            if self.shift_threshold_met(game_dt):
                self.move(self.direction[0], self.direction[1])
        else:
            # No movement possible, so update motion vector with 0, 0
            self.motion_vector = (0, 0)

    # Define orientation based on current and previous direction
    def set_orientation(self):
        # Moving right
        if self.motion_vector[0] > 0:
            self.rotation_angle = 0
            self.mirror = False
        # Moving left
        elif self.motion_vector[0] < 0:
            self.rotation_angle = 0
            self.mirror = True
        # Moving up, where previous motion was right
        elif self.motion_vector[1] < 0 and self.motion_vector_history[-1][0] > 0:
            self.rotation_angle = 90  # rotate ccw
            self.mirror = False
        # Moving up, where previous motion was left
        elif self.motion_vector[1] < 0 and self.motion_vector_history[-1][0] < 0:
            self.rotation_angle = 90  # rotate ccw
            self.mirror = True  # then mirror horizontally
        # Moving up, where previous motion was down
        elif self.motion_vector[1] < 0 and self.motion_vector_history[-1][1] > 0:
            if self.mirror:
                self.rotation_angle = 90  # rotate ccw
                self.mirror = False
            else:
                self.rotation_angle = 90  # rotate ccw
                self.mirror = True  # then mirror horizontally
        # Covering remaining cases for moving up
        elif self.motion_vector[1] < 0:
            self.rotation_angle = 90  # rotate ccw
            self.mirror = False
        # Moving down, where previous motion was right
        elif self.motion_vector[1] > 0 and self.motion_vector_history[-1][0] > 0:
            self.rotation_angle = -90  # rotate cw
            self.mirror = False
        # Moving down, where previous motion was left
        elif self.motion_vector[1] > 0 and self.motion_vector_history[-1][0] < 0:
            self.rotation_angle = -90  # rotate cw
            self.mirror = True  # then mirror horizontally
        # Moving down, where previous motion was up
        elif self.motion_vector[1] > 0 and self.motion_vector_history[-1][1] < 0:
            if self.mirror:
                self.rotation_angle = -90  # rotate cw
                self.mirror = False
            else:
                self.rotation_angle = -90  # rotate cw
                self.mirror = True  # then mirror horizontally
        # Covering remaining cases for moving down
        elif self.motion_vector[1] > 0:
            self.rotation_angle = -90  # rotate cw
            self.mirror = False

    # Method to draw onto screen at its position, with screen offsets as needed
    def draw(self, draw_image_x, draw_image_y, image_boundary, screen):
        self.get_image()
        draw_image = self.image
        if self.rotation_angle != 0:
            draw_image = pygame.transform.rotate(draw_image, self.rotation_angle)
        if self.mirror:
            draw_image = pygame.transform.flip(draw_image, True, False)
        image_rect = draw_image.get_rect()
        image_rect.center = self.center_position
        image_rect.move_ip(draw_image_x + image_boundary, draw_image_y + image_boundary)
        screen.blit(draw_image, image_rect)
        # If animation finished, reset variables
        if (
            self.animation_start_time
            and self.animation_index == len(self.animation_sequence) - 1
        ):
            self.animation_sequence = []
            self.animation_index = 0
            self.animation_start_time = None

    # Method to initialize animation
    def animate(self, images, time_delays):
        keys = ["image", "time_delay"]
        for image, time_delay in zip(images, time_delays):
            self.animation_sequence.append(dict(zip(keys, [image, time_delay])))
        self.animation_start_time = time.time()

    # Method to get correct animation frame at a given time
    def get_image(self):
        if self.animation_sequence:
            for index, frame in enumerate(self.animation_sequence):
                if time.time() - self.animation_start_time >= frame.get("time_delay"):
                    self.image = frame.get("image")
                    self.animation_index = index

    # Set sprite commanded direction to input values
    def set_direction(self, x_direction, y_direction):
        self.desired_direction = (x_direction, y_direction)

    # Perform collision check with another sprite
    def collide_check(self, second_sprite: "Sprite"):
        return self.hitbox_rect.colliderect(second_sprite.hitbox_rect)

    # Check if the fractional shift performed warrants shifting the block by a pixel
    def shift_threshold_met(self, game_dt):
        delta_dist = self.speed * game_dt
        self.center_pos_decimal = (
            self.center_pos_decimal[0] + delta_dist * self.direction[0],
            self.center_pos_decimal[1] + delta_dist * self.direction[1],
        )
        return (
            abs(self.center_pos_decimal[0] - self.center_position[0]) > 0.5
            or abs(self.center_pos_decimal[1] - self.center_position[1]) > 0.5
        )

    # Set sprite speed to input value
    def set_speed(self, new_speed):
        self.speed = new_speed

    # Set flag to destroy asset
    def destroy(self):
        self.destroyed = True

    # Return flag of whether sprite destroyed
    def is_destroyed(self):
        return self.destroyed

    # Return rect containing path box
    def get_path_rect(self):
        return self.path_rect

    # Return rect containing hit box
    def get_hit_rect(self):
        return self.hitbox_rect

    # Return center position coordinates
    def get_center_position(self):
        return self.center_position

    # Return whether animation is occuring
    def is_animating(self):
        return bool(self.animation_start_time)

    # Return motion vector
    def get_motion_vector(self):
        return self.motion_vector
