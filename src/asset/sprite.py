import pygame
from rect.utils import define_rect


# Class to define a sprite and its methods
class Sprite:
    def __init__(
        self, name, image, center_position, health, can_rotate, hitbox_width, path_width
    ):
        self.name = name
        self.image = image
        self.center_position = center_position
        self.health = health
        self.can_rotate = can_rotate

        self.hitbox_rect = define_rect(center_position, hitbox_width)
        self.path_rect = define_rect(center_position, path_width)
        self.rotation_angle = 0  # + counterclockwise
        self.mirror = False
        self.destroyed = False
        self.position_history = []
        self.direction = (0, 0)
        self.direction_history = []
        self.motion_vector = (0, 0)
        self.motion_vector_history = []

    # Method to move the asset
    def move(self, delta_x, delta_y, maze_grid):
        # Store current position
        self.position_history.append(self.center_position)
        # Move Rect objects and position
        self.hitbox_rect.move_ip(delta_x, delta_y)
        self.path_rect.move_ip(delta_x, delta_y)
        self.center_position = (
            self.center_position[0] + delta_x,
            self.center_position[1] + delta_y,
        )
        # Store motion vector into history and calculate new
        self.motion_vector_history.append(self.motion_vector)
        self.motion_vector = (
            self.center_position[0] - self.position_history[-1][0],
            self.center_position[1] - self.position_history[-1][1],
        )

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

    # Determine and perform move based on direction and move check
    def perform_move(self, maze_grid):
        delta_x = self.direction[0]
        delta_y = self.direction[1]
        if not (delta_x == 0 and delta_y == 0):
            if self.can_move(delta_x, delta_y, maze_grid):
                # Since current direction possible, move in that direction
                self.move(delta_x, delta_y, maze_grid)
                # Set orientation if there was a change to the motion
                if self.motion_vector_history[-1] != self.motion_vector:
                    # Set orientation based on current direction and/or position history
                    if self.can_rotate:
                        self.set_orientation()
                # Add 0, 0 to direction history
                self.direction_history.append((0, 0))
            else:
                # Otherwise try moving in the previous direction
                delta_x = self.direction_history[-1][0]
                delta_y = self.direction_history[-1][1]
                if not (delta_x == 0 and delta_y == 0) and self.can_move(
                    delta_x, delta_y, maze_grid
                ):
                    self.move(delta_x, delta_y, maze_grid)

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
        # Moving up, where previous direction was left
        elif self.motion_vector[1] < 0 and self.motion_vector_history[-1][0] < 0:
            self.rotation_angle = 90  # rotate ccw
            self.mirror = True  # then mirror horizontally
        # Moving up, covering case where previously moving down
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
        # Moving down, where previous direction was right
        elif self.motion_vector[1] > 0 and self.motion_vector_history[-1][0] > 0:
            self.rotation_angle = -90  # rotate cw
            self.mirror = False
        # Moving down, where previous direction was left
        elif self.motion_vector[1] > 0 and self.motion_vector_history[-1][0] < 0:
            self.rotation_angle = -90  # rotate cw
            self.mirror = True  # then mirror horizontally
        # Moving down, covering case where previously moving up
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
        draw_image = self.image
        if self.rotation_angle != 0:
            draw_image = pygame.transform.rotate(draw_image, self.rotation_angle)
        if self.mirror:
            draw_image = pygame.transform.flip(draw_image, True, False)
        image_rect = draw_image.get_rect()
        image_rect.center = self.center_position
        image_rect.move_ip(draw_image_x + image_boundary, draw_image_y + image_boundary)
        screen.blit(draw_image, image_rect)

    # Set sprite direction to input values
    def set_direction(self, x_direction, y_direction, maze_grid):
        # Store the previous direction since it may not be possible to move
        # in new direction yet, then change current direction
        if self.direction != (x_direction, y_direction):
            # Don't store a stopped direction in previous variable
            # since we want to know how to rotate object based on
            # previous movement. Also ensure that current direction is
            # navigable, as this check ensures we don't to stop in place
            # from changing direction twice.
            if self.direction != (0, 0) and self.can_move(
                self.direction[0], self.direction[1], maze_grid
            ):
                self.direction_history.append(self.direction)
            # Save new direction
            self.direction = (x_direction, y_direction)

    # Set sprite health to input value
    def set_health(self, new_health):
        self.health = new_health

    # Set flag to destroy asset
    def destroy(self, destroy_images):
        self.destroyed = True

    # Return flag of whether sprite destroyed
    def isdestroyed(self):
        return self.destroyed

    # Return rect containing path box
    def get_path_rect(self):
        return self.path_rect

    # Return rect containing hit box
    def get_hit_rect(self):
        return self.hitbox_rect
