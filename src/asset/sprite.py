import pygame
import time
import random
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
        self.hitbox_width = hitbox_width
        self.path_width = path_width

        # Additional attributes
        self.orig_image = image
        self.move_dist = 0
        self.facing = "right"
        self.spawn = False
        self._initialize_attributes()

    # Initialization of more attributes
    def _initialize_attributes(self):
        self.hitbox_rect = define_rect(self.center_position, self.hitbox_width)
        self.path_rect = define_rect(self.center_position, self.path_width)
        self.rotation_angle = 0  # + counterclockwise
        self.mirror = False
        self.destroyed = False
        self.direction = (0, 0)
        self.desired_direction = ()
        self.motion_vector = (0, 0)
        self.animation_start_time = None
        self.animation_sequence = []
        self.animation_index = 0

    # Method to perform reset to absolulte location
    def reset(self, x, y):
        self.center_position = (x, y)
        self._initialize_attributes()

    # Method to perform shifting to desired location
    def shift(self, delta_x, delta_y):
        self.hitbox_rect.move_ip(delta_x, delta_y)
        self.path_rect.move_ip(delta_x, delta_y)
        self.center_position = (
            self.center_position[0] + delta_x,
            self.center_position[1] + delta_y,
        )

    # Method to move the asset with associated motion vector and orientation operations
    def move(self, delta_x, delta_y):
        if delta_x != 0 or delta_y != 0:
            # Initialize flag, only to be used if motion vector changes
            orientation_check = False
            # Determine signs of deltas
            delta_signs = [0, 0]
            delta_signs[0] = 1 if delta_x > 0 else (-1 if delta_x < 0 else 0)
            delta_signs[1] = 1 if delta_y > 0 else (-1 if delta_y < 0 else 0)
            # Check orientation if new motion is different
            if (
                self.motion_vector[0] != delta_signs[0]
                or self.motion_vector[1] != delta_signs[1]
            ):
                orientation_check = True
            # Shift Rect objects and position
            self.shift(delta_x, delta_y)
            # Set new motion vector
            self.motion_vector = (delta_signs[0], delta_signs[1])
            # Determine new orientation if motion vector changed
            if self.can_rotate and orientation_check:
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
        # Determine how far item has traveled in the game_dt game tick
        self.move_dist += self.speed * game_dt

        # If threshold of 1 pixel reached, do move
        if self.move_dist >= 1:
            delta_dist = int(self.move_dist)
            self.move_dist = 0
            do_move = True
        elif self.move_dist < 1:
            do_move = False

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
                if do_move:
                    # Move delta_dist, or max possible if that is too far
                    for i in range(delta_dist, 0, -1):
                        max_dist = i
                        if self.can_move(
                            i * self.direction[0], i * self.direction[1], maze_grid
                        ):
                            break
                    self.move(
                        max_dist * self.direction[0], max_dist * self.direction[1]
                    )
        # If current direction is possible, keep moving that way
        elif do_move and self.can_move(self.direction[0], self.direction[1], maze_grid):
            # Move delta_dist, or max possible if that is too far
            for i in range(delta_dist, 0, -1):
                max_dist = i
                if self.can_move(
                    i * self.direction[0], i * self.direction[1], maze_grid
                ):
                    break
            self.move(max_dist * self.direction[0], max_dist * self.direction[1])
        else:
            # No movement possible, so update motion vector with 0, 0
            self.motion_vector = (0, 0)

    # Define orientation based on current and previous direction
    def set_orientation(self):
        # Moving right
        if self.motion_vector[0] > 0:
            self.rotation_angle = 0
            self.mirror = False
            self.facing = "right"
        # Moving left
        elif self.motion_vector[0] < 0:
            self.rotation_angle = 0
            self.mirror = True
            self.facing = "left"
        # Moving up, where previously facing right, or wheels to the right
        elif self.motion_vector[1] < 0 and (
            self.facing == "right" or self.facing == "wheels_right"
        ):
            self.rotation_angle = 90  # rotate ccw
            self.mirror = False
            self.facing = "wheels_right"
        # Moving up, where previously facing left, or wheels to the left
        elif self.motion_vector[1] < 0 and (
            self.facing == "left" or self.facing == "wheels_left"
        ):
            self.rotation_angle = 90  # rotate ccw
            self.mirror = True  # then mirror horizontally
            self.facing = "wheels_left"
        # Moving down, where previously facing right, or wheels to the left
        elif self.motion_vector[1] > 0 and (
            self.facing == "right" or self.facing == "wheels_left"
        ):
            self.rotation_angle = -90  # rotate cw
            self.mirror = False
            self.facing = "wheels_left"
        # Moving down, where previously facing left, or wheels to the right
        elif self.motion_vector[1] > 0 and (
            self.facing == "left" or self.facing == "wheels_right"
        ):
            self.rotation_angle = -90  # rotate cw
            self.mirror = True  # then mirror horizontally
            self.facing = "wheels_right"

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

    # Move towards player if direction possible,
    # otherwise random navigation, only backtracking if needed
    def set_navigate_direction(self, second_sprite: "Sprite", maze_grid, game_dt):
        # Determine how far item has traveled in the game_dt game tick
        if self.move_dist + self.speed * game_dt >= 1:
            # Possible directions: Right, Left, Up, Down
            dirs = [(1, 0), (-1, 0), (0, -1), (0, 1)]

            aligned_second_sprite = False
            # If aligned vertically with second sprite
            if self.center_position[1] == second_sprite.center_position[1]:
                # Move towards second sprite either right or left
                aligned_second_sprite = True
                if self.path_rect.right < second_sprite.path_rect.left:
                    self.set_direction(dirs[0][0], dirs[0][1])
                elif self.path_rect.left > second_sprite.path_rect.right:
                    self.set_direction(dirs[1][0], dirs[1][1])

            # If aligned horizontally with second sprite
            elif self.center_position[0] == second_sprite.center_position[0]:
                # Move towards second sprite either up or down
                aligned_second_sprite = True
                if self.path_rect.top > second_sprite.path_rect.bottom:
                    self.set_direction(dirs[2][0], dirs[2][1])
                elif self.path_rect.bottom < second_sprite.path_rect.top:
                    self.set_direction(dirs[3][0], dirs[3][1])

            # If current direction is 0, 0, choose a random direction
            if self.desired_direction == (0, 0) or not self.desired_direction:
                rand_direction = dirs[random.randint(0, 3)]
                self.set_direction(rand_direction[0], rand_direction[1])

            # Check current direction, then orthogonal directions, then reverse
            reverse_direction = (-1 * self.desired_direction[0], -1 * self.desired_direction[1])
            orthog_direction_1 = (self.desired_direction[1], self.desired_direction[0])
            orthog_direction_2 = (-1 * self.desired_direction[1], -1 * self.desired_direction[0])

            directions_to_check = [
                self.desired_direction,
                orthog_direction_1,
                orthog_direction_2,
                reverse_direction,
            ]
            valid_indices = []
            for index, direction in enumerate(directions_to_check):
                if self.can_move(
                    direction[0], direction[1], maze_grid
                ):
                    valid_indices.append(index)

            # If no directions are possible or only reverse possible, these take precedent.
            # Otherwise, pick a random direction of the remaining possibilities if not 
            # aligned with the second sprite (go in player direction if it's possible).
            if not valid_indices:
                self.set_direction(0, 0)
            elif valid_indices == [3]:
                self.set_direction(directions_to_check[3][0], directions_to_check[3][1])
            elif aligned_second_sprite and 0 in valid_indices:
                pass
            else:
                non_reverse_dirs = [i for i in valid_indices if i != 3]
                chosen_index = random.choice(non_reverse_dirs)
                self.set_direction(
                    directions_to_check[chosen_index][0],
                    directions_to_check[chosen_index][1],
                )

    # Perform collision check with another sprite
    def collide_check(self, second_sprite: "Sprite"):
        return self.hitbox_rect.colliderect(second_sprite.hitbox_rect)

    # Set sprite speed to input value
    def set_speed(self, new_speed):
        self.speed = new_speed

    # Set sprite image to original, and reset animation
    def reset_image(self):
        self.image = self.orig_image
        self.animation_sequence = []
        self.animation_index = 0
        self.animation_start_time = None

    # Set flag to destroy asset
    def toggle_destroy(self):
        self.destroyed = not self.destroyed

    # Return flag of whether sprite destroyed
    def is_destroyed(self):
        return self.destroyed

    # Set flag to prevent respawn
    def toggle_spawn(self):
        self.spawn = not self.spawn

    # Return flag of whether sprite respawn active
    def can_spawn(self):
        return self.spawn

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
