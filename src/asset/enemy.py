import pygame
import random
from asset.sprite import Sprite


# Class to define a sprite and its methods
class Enemy(Sprite):
    def __init__(
        self, name, image, center_position, speed, can_rotate, hitbox_width, path_width
    ):
        super().__init__(
            name, image, center_position, speed, can_rotate, hitbox_width, path_width
        )

    # Method to check if the enemy can move within maze
    # in the direction of a second sprite, and that a clear
    # path exists between the two. If true, returns the direction
    # to be traversed by the enemy.
    def can_move_towards(self, second_sprite: "Sprite", maze_grid):
        aligned_horz = False
        aligned_vert = False
        # Check if aligned horizontally with second sprite (same y)
        if self.center_position[1] == second_sprite.center_position[1]:
            # Move towards second sprite either right or left
            aligned_horz = True
            if self.center_position[0] < second_sprite.center_position[0]:
                move_direction = (1, 0)
            elif self.center_position[0] > second_sprite.center_position[0]:
                move_direction = (-1, 0)
        # Otherwise check if aligned vertically with second sprite (same x)
        elif self.center_position[0] == second_sprite.center_position[0]:
            # Move towards second sprite either up or down
            aligned_vert = True
            if self.center_position[1] > second_sprite.center_position[1]:
                move_direction = (0, -1)
            elif self.center_position[1] < second_sprite.center_position[1]:
                move_direction = (0, 1)

        # Form a horizontal rect between the two for checking
        if aligned_horz:
            temp_topleft_x = min(
                self.path_rect.topleft[0], second_sprite.path_rect.topleft[0]
            ) + int(self.path_width / 2)
            temp_topleft_y = self.path_rect.topleft[1]
            temp_width = abs(
                self.path_rect.center[0] - second_sprite.path_rect.center[0]
            )
            temp_height = self.path_rect.height
        # Form a vertical rect between the two for checking
        elif aligned_vert:
            temp_topleft_x = self.path_rect.topleft[0]
            temp_topleft_y = min(
                self.path_rect.topleft[1], second_sprite.path_rect.topleft[1]
            ) + int(self.path_width / 2)
            temp_width = self.path_rect.width
            temp_height = abs(
                self.path_rect.center[1] - second_sprite.path_rect.center[1]
            )

        if not (aligned_horz or aligned_vert):
            return ()

        # Check if temp rect resides within a clear space within maze path
        temp_rect = pygame.Rect(temp_topleft_x, temp_topleft_y, temp_width, temp_height)
        if Sprite.is_path_clear(temp_rect, maze_grid):
            return move_direction
        return ()

    # Move towards second sprite if direction possible,
    # otherwise random navigation, only backtracking if needed
    def set_navigate_direction(self, second_sprite: "Sprite", maze_grid, game_tick):
        # Determine how far item has traveled in the game tick
        if self.move_dist + self.speed * game_tick >= 1:
            # Possible directions: Right, Left, Up, Down
            dirs = [(1, 0), (-1, 0), (0, -1), (0, 1)]

            # Check if possible to move towards second sprite with clear path
            move_direction = ()
            aligned_second_sprite = False
            if second_sprite:
                move_direction = self.can_move_towards(second_sprite, maze_grid)
            if move_direction:
                aligned_second_sprite = True
                self.set_desired_direction(move_direction[0], move_direction[1])

            # If current direction is 0, 0, choose a random direction
            if self.desired_direction == (0, 0) or not self.desired_direction:
                rand_direction = dirs[random.randint(0, 3)]
                self.set_desired_direction(rand_direction[0], rand_direction[1])

            # Check current direction, then orthogonal directions, then reverse
            reverse_direction = (
                -1 * self.desired_direction[0],
                -1 * self.desired_direction[1],
            )
            orthog_direction_1 = (self.desired_direction[1], self.desired_direction[0])
            orthog_direction_2 = (
                -1 * self.desired_direction[1],
                -1 * self.desired_direction[0],
            )

            directions_to_check = [
                self.desired_direction,
                orthog_direction_1,
                orthog_direction_2,
                reverse_direction,
            ]
            valid_indices = []
            for index, direction in enumerate(directions_to_check):
                if self.can_move(direction[0], direction[1], maze_grid):
                    valid_indices.append(index)

            # If no directions are possible or only reverse possible, these take precedent.
            # Otherwise, pick a random direction of the remaining possibilities if not
            # aligned with the second sprite (go in second sprite direction if it's possible).
            if not valid_indices:
                self.set_desired_direction(0, 0)
            elif valid_indices == [3]:
                self.set_desired_direction(
                    directions_to_check[3][0], directions_to_check[3][1]
                )
            elif aligned_second_sprite and 0 in valid_indices:
                pass
            else:
                non_reverse_dirs = [i for i in valid_indices if i != 3]
                chosen_index = random.choice(non_reverse_dirs)
                self.set_desired_direction(
                    directions_to_check[chosen_index][0],
                    directions_to_check[chosen_index][1],
                )
