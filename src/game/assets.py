import time
from settings import config as cfg
from asset.sprite import Sprite
from asset.enemy import Enemy


# Function to initialize and return items
def init_items(asset_coord, images, block_width, maze_factor):
    items = {}
    for key, value in asset_coord.items():
        if key in cfg.ITEM_IMAGE_DEFS:
            items[key] = Sprite(
                key,
                images[cfg.ITEM_IMAGE_DEFS.get(key)],
                asset_coord.get(key),
                0,
                False,
                int(block_width / (maze_factor * 6)),
                int(block_width / maze_factor),
            )
    return items


# Function to initialize enemies
def init_enemies(
    name,
    quantity,
    image,
    location,
    pixels_per_second,
    hitbox_size,
    path_size,
    is_invincible,
):
    enemy_list = []
    for i in range(quantity):
        enemy_list.append(
            Enemy(
                name,
                image,
                location,
                pixels_per_second,
                False,
                hitbox_size,
                path_size,
                is_invincible,
            )
        )
    return enemy_list


# Function to initialize variables and flags after creating assets
def set_asset_flags(flags):
    start_time = time.time()
    projectile = []
    blast = []
    spawned_enemies = 0
    flags.rungame = True
    flags.exit_found = False
    flags.screen_change = True
    flags.create_sprites = False
    flags.exit_sound_played = False

    return start_time, projectile, blast, spawned_enemies, flags
