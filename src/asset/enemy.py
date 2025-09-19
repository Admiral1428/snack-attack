import pygame
import random
from asset.sprite import Sprite


# Class to define a sprite and its methods
class Enemy(Sprite):
    def __init__(
        self,
        name,
        image,
        center_position,
        speed,
        can_rotate,
        hitbox_width,
        path_width,
        rotate_image,
        is_invincible,
    ):
        super().__init__(
            name,
            image,
            center_position,
            speed,
            can_rotate,
            hitbox_width,
            path_width,
            rotate_image,
        )
        self.is_invincible = is_invincible

        # Additional attributes
        self.path_finding = False
        self.seen_player = False

    # Method to check if the enemy can move within maze
    # in the direction of a second sprite, and that a clear
    # path exists between the two. If true, returns the direction
    # to be traversed by the enemy.
    def can_see_player(self, second_sprite: "Sprite", barrier_sprites, maze_grid):
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
            for barrier in barrier_sprites:
                if barrier_sprites[barrier].hitbox_rect.colliderect(temp_rect):
                    return ()
            return move_direction
        return ()

    # Move towards second sprite if direction possible,
    # otherwise random navigation, only backtracking if needed
    def set_navigate_direction(
        self, second_sprite: "Sprite", barrier_sprites, maze_grid, game_tick
    ):
        # Determine how far item has traveled in the game tick
        if self.move_dist + self.speed * game_tick >= 1:
            # Possible directions: Right, Left, Up, Down
            dirs = [(1, 0), (-1, 0), (0, -1), (0, 1)]

            # Check if possible to move towards second sprite with clear path
            if second_sprite and not self.has_seen_player():
                move_dir = self.can_see_player(
                    second_sprite, barrier_sprites, maze_grid
                )
                if move_dir:
                    self.set_desired_direction(move_dir[0], move_dir[1])
                    self.seen_player = True

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
            elif self.seen_player and 0 in valid_indices:
                pass
            else:
                non_reverse_dirs = [i for i in valid_indices if i != 3]
                chosen_index = random.choice(non_reverse_dirs)
                self.set_desired_direction(
                    directions_to_check[chosen_index][0],
                    directions_to_check[chosen_index][1],
                )

    # Pathfind based on current flow field
    def set_pathfind_direction(self, flow_field, enemy_graph_coord):
        flow_field_direction = flow_field[enemy_graph_coord]
        if flow_field_direction != (0, 0):
            self.set_desired_direction(flow_field_direction[0], flow_field_direction[1])
            self.path_finding = True
        else:
            self.path_finding = False
            self.set_desired_direction(0, 1)

    # Return whether the enemy is performing pathfinding using flow field
    def is_path_finding(self):
        return self.path_finding

    # Toggle flag for whether enemy is pathfinding
    def toggle_path_finding(self):
        self.path_finding = not self.path_finding

    # Toggle flag for whether the enemy has seen the player
    def toggle_seen_player(self):
        self.seen_player = not self.seen_player

    # Return whether the enemy has seen the player
    def has_seen_player(self):
        return self.seen_player
