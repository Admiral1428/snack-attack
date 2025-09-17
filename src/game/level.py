import ast
from settings import config as cfg
from utils.exceptions import CustomError
from grid.utils import invert_maze_to_grid


# Function to print text next to maze
def print_level_text(screen, levels, level_index, fonts, flags, controls_option):
    # Print level info
    for row, text_line in enumerate(cfg.INFO_STRINGS):
        text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["white"])
        locs = cfg.TEXT_LOC["level_score_lives"]
        screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))
    # Trim level name
    folder_name = levels[level_index].get("folder")
    if len(folder_name) > 8:
        folder_name = folder_name[:8] + "..."
    if flags.reached_last_level:
        text_surface = fonts["normal"].render(
            folder_name + " (reprise)", True, cfg.COLORS["red"]
        )
    else:
        text_surface = fonts["normal"].render(folder_name, True, cfg.COLORS["white"])
    locs = cfg.TEXT_LOC["level_value"]
    screen.blit(text_surface, (locs[0], locs[1]))

    # Print instructions
    for row, text_line in enumerate(cfg.HOW_TO_STRINGS):
        text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["white"])
        locs = cfg.TEXT_LOC["instructions"]
        screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))

    # Print controls
    for row, text_line in enumerate(cfg.CONTROLS_TEXT[controls_option]):
        text_surface = fonts["normal"].render(text_line, True, cfg.COLORS["white"])
        locs = cfg.TEXT_LOC["controls"]
        screen.blit(text_surface, (locs[0], locs[1] + row * locs[2]))


# Function to create maze grid based on chosen fidelity
def create_grid(maze_width, maze_height, block_width, maze_factor, maze_path):
    # Scale inputs prior to creating maze grid, based on chosen fidelity
    maze_width_scaled = int(maze_width / maze_factor)
    maze_height_scaled = int(maze_height / maze_factor)
    block_width_scaled = int(block_width / maze_factor)
    coords_scaled = []
    for coord in maze_path:
        coords_scaled.append((int(coord[0] / maze_factor), int(coord[1] / maze_factor)))

    # Get maze grid
    maze_grid = invert_maze_to_grid(
        coords_scaled,
        maze_width_scaled,
        maze_height_scaled,
        0,
        0,
        0,
        block_width_scaled,
    )

    return maze_grid


# Determine level speed, enemy quantity, speed, asset locations
def get_level_data(flags, maze_factor, maze_metadata, maze_assets):
    # Hardcode speed and enemy quantity if repeated levels
    if flags.reached_last_level:
        level_speed = "frantic"
        num_corn = 2
        num_tomato = 4
        num_pumpkin = 4
    # Otherwise save relevant metadata
    else:
        level_speed = maze_metadata.get("level_speed")
        num_corn = ast.literal_eval(maze_metadata.get("corn_quantity"))
        num_tomato = ast.literal_eval(maze_metadata.get("tomato_quantity"))
        num_pumpkin = ast.literal_eval(maze_metadata.get("pumpkin_quantity"))

    # Assign appropriate sprite speed, defaulting to slow,
    # while accounting for animation smoothness
    if level_speed in cfg.LEVEL_SPEEDS.keys():
        pixels_per_second = int(cfg.LEVEL_SPEEDS.get(level_speed) / maze_factor)
    else:
        pixels_per_second = int(cfg.LEVEL_SPEEDS.get("slow") / maze_factor)

    # Assign appropriate enemy respawn speed, defaulting to slow
    if level_speed in cfg.SPAWN_SPEEDS.keys():
        seconds_to_spawn = cfg.SPAWN_SPEEDS.get(level_speed)
    else:
        seconds_to_spawn = cfg.SPAWN_SPEEDS.get("slow")

    # Save maze asset coordinates into a single dictionary and check validity
    # of asset coordinates with error handling
    asset_coord = {}
    for dict in maze_assets:
        asset_coord[dict.get("letter")] = ast.literal_eval(dict.get("location"))
        # Scale based on maze fidelity
        asset_coord[dict.get("letter")] = (
            int(asset_coord[dict.get("letter")][0] / maze_factor),
            int(asset_coord[dict.get("letter")][1] / maze_factor),
        )
    if (
        len(asset_coord) != len(cfg.ALLOWABLE_LETTERS)
        or any(
            not isinstance(value, tuple) or not value for value in asset_coord.values()
        )
        or any(key not in cfg.ALLOWABLE_LETTERS for key in asset_coord.keys())
    ):
        raise CustomError(
            cfg.ERROR_STRINGS["asset_letter"] + str(cfg.ALLOWABLE_LETTERS)
        )

    return (
        num_corn,
        num_tomato,
        num_pumpkin,
        pixels_per_second,
        seconds_to_spawn,
        asset_coord,
    )


# Initialize flags after maze draw
def set_maze_flags(next_level_key, flags, levels, level_index):
    # Skip to next level if pressed during draw
    if next_level_key:
        if level_index >= len(levels) - 1:
            level_index = 0
            flags.reached_last_level = True
        else:
            level_index += 1
        flags.maze_draw = True
        flags.f10_pressed = False
    else:
        flags.create_sprites = True
        flags.exit_created = False
        flags.exit_found = False
        flags.exit_opening = False
        flags.exit_closing = False
        flags.maze_draw = False

    return flags, level_index
