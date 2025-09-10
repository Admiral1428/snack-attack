import pygame
from asset.sprite import Sprite


# Class to define a sprite and its methods
class Player(Sprite):
    def __init__(
        self, name, image, center_position, speed, can_rotate, hitbox_width, path_width
    ):
        super().__init__(
            name, image, center_position, speed, can_rotate, hitbox_width, path_width
        )

    # Assign direction based on user input
    def control_direction(self, keys, key_order, controls_option):
        if controls_option == 0:
            if (
                not keys[pygame.K_d]
                and not keys[pygame.K_a]
                and not keys[pygame.K_w]
                and not keys[pygame.K_s]
            ):
                self.set_desired_direction(0, 0)  # stop
            elif key_order and key_order[-1] == pygame.K_d:
                self.set_desired_direction(1, 0)  # right
            elif key_order and key_order[-1] == pygame.K_a:
                self.set_desired_direction(-1, 0)  # left
            elif key_order and key_order[-1] == pygame.K_w:
                self.set_desired_direction(0, -1)  # up
            elif key_order and key_order[-1] == pygame.K_s:
                self.set_desired_direction(0, 1)  # down
        elif controls_option == 1:
            if (
                not keys[pygame.K_l]
                and not keys[pygame.K_j]
                and not keys[pygame.K_i]
                and not keys[pygame.K_k]
            ):
                self.set_desired_direction(0, 0)  # stop
            elif key_order and key_order[-1] == pygame.K_l:
                self.set_desired_direction(1, 0)  # right
            elif key_order and key_order[-1] == pygame.K_j:
                self.set_desired_direction(-1, 0)  # left
            elif key_order and key_order[-1] == pygame.K_i:
                self.set_desired_direction(0, -1)  # up
            elif key_order and key_order[-1] == pygame.K_k:
                self.set_desired_direction(0, 1)  # down
        elif controls_option == 2:
            if keys[pygame.K_d]:
                self.set_desired_direction(1, 0)  # right
            elif keys[pygame.K_a]:
                self.set_desired_direction(-1, 0)  # left
            elif keys[pygame.K_w]:
                self.set_desired_direction(0, -1)  # up
            elif keys[pygame.K_s]:
                self.set_desired_direction(0, 1)  # down
            elif keys[pygame.K_SPACE]:
                self.set_desired_direction(0, 0)  # stop
        else:
            if keys[pygame.K_l]:
                self.set_desired_direction(1, 0)  # right
            elif keys[pygame.K_j]:
                self.set_desired_direction(-1, 0)  # left
            elif keys[pygame.K_i]:
                self.set_desired_direction(0, -1)  # up
            elif keys[pygame.K_k]:
                self.set_desired_direction(0, 1)  # down
            elif keys[pygame.K_SPACE]:
                self.set_desired_direction(0, 0)  # stop
