# Directories with external files
DIRS = {}
DIRS["images"] = "../assets/sprites/"
DIRS["settings"] = "../assets/settings/"
DIRS["sounds"] = "../assets/sounds/"
DIRS["levels"] = "../assets/levels/"
DIRS["title"] = "../assets/title/"

# Filenames
FILES = {}
FILES["screenshot_no_assets"] = "level_screenshot_no_assets.png"
FILES["screenshot_assets"] = "level_screenshot.png"
FILES["path_coordinates"] = "level_path_coordinates.csv"
FILES["asset_coordinates"] = "level_asset_coordinates.csv"
FILES["metadata"] = "level_metadata.csv"
FILES["settings"] = "config.csv"
FILES["grid"] = "level_grid.txt"

# User config, maze fidelity, screen dimensions
MAZE_FIDELITY_OPTS = ["coarse", "normal", "fine"]
MAZE_FIDELITY_FACTORS = [4, 2, 1]
WIDTH, HEIGHT = (1600, 900)

# Define maze properties
MAZE_WIDTH = 256
MAZE_HEIGHT = 192
BLOCK_WIDTH = 12
MIN_BLOCK_SPACING = 4
DRAW_IMAGE_X = 20
DRAW_IMAGE_Y = 20
IMAGE_BOUNDARY = 4

# Scale variables
SCALE_FACTOR = 4

# Max enemies in level builder
MAX_CORN = 8
MAX_TOMATO = 6
MAX_PUMPKIN = 4

# Define colors
COLORS = {}
COLORS["teal"] = (0, 168, 168)
COLORS["yellow"] = (255, 255, 0)
COLORS["orange"] = (255, 128, 0)
COLORS["green"] = (0, 255, 0)
COLORS["dkgreen"] = (0, 102, 0)
COLORS["purple"] = (128, 0, 128)
COLORS["magenta"] = (253, 61, 181)
COLORS["red"] = (255, 0, 0)
COLORS["blue"] = (0, 0, 255)
COLORS["gray"] = (128, 128, 128)
COLORS["white"] = (255, 255, 255)
COLORS["black"] = (0, 0, 0)
COLORS["ltgray"] = (212, 212, 212)

# Level draw instruction text
DRAW_STRINGS = [
    "Left click or use arrow keys to",
    "draw maze. Right click to erase.",
    "X to undo last drawn position.",
    "",
    "W to cycle wall color",
    "A to end maze and place assets",
    "F to cycle level speed:",
    "",
    "J to cycle # corn enemies",
    "K to cycle # tomato enemies",
    "L to cycle # pumpkin enemies",
]

# Load maze instruction text
LOAD_TEXT = "Press Escape to import an existing maze"

# Level asset placement instruction text
ASSET_STRINGS = [
    "Key (see list below) to place",
    "asset at cursor location",
    "Right click to undo",
    "C to export maze to files",
]

# Level info text
INFO_STRINGS = [
    "Level: " "",
    "Score: ",
    "Lives: ",
]

# Game over text
ENDGAME_STRINGS = [
    "GAME OVER",
    "Thank you for playing! :)",
]

# Instruction text
HOW_TO_STRINGS = [
    "************************",
    "Pause = Pause game",
    "F1 = Change controls",
    "F10 = Skip Level",
    "Escape = Title Screen",
]

# Controls option and text
CONTROLS_TEXT = []
CONTROLS_TEXT.append(
    [
        "",
        "Hold W = Move up",
        "Hold S = Move down",
        "Hold A = Move left",
        "Hold D = Move right",
        "Press Enter = Fire weapon",
    ]
)
CONTROLS_TEXT.append(
    [
        "",
        "Hold I = Move up",
        "Hold K = Move down",
        "Hold J = Move left",
        "Hold L = Move right",
        "Press F = Fire weapon",
    ]
)
CONTROLS_TEXT.append(
    [
        "Press Space = Stop",
        "Press W = Move up",
        "Press S = Move down",
        "Press A = Move left",
        "Press D = Move right",
        "Press Enter = Fire weapon",
    ]
)
CONTROLS_TEXT.append(
    [
        "Press Space = Stop",
        "Press I = Move up",
        "Press K = Move down",
        "Press J = Move left",
        "Press L = Move right",
        "Press F = Fire weapon",
    ]
)

# Game pause text
PAUSE_TEXT = "Game paused. Press Pause button to resume."

# Store dictionary with item image definitions
ITEM_IMAGE_DEFS = {"1": "strawberry", "2": "cherry", "3": "banana", "4": "grape"}

# Enemy spawn frequency speed definitions (seconds between spawns)
SPAWN_SPEEDS = {"slow": 1, "medium": 0.75, "fast": 0.5, "frantic": 0.25}

# Level speed definitions (coordinates per game tick for moving sprites)
LEVEL_SPEEDS = {
    "slow": 144,
    "medium": 180,
    "fast": 240,
    "frantic": 360,
}

LEVEL_SPEED_ORDER = ("slow", "medium", "fast", "frantic")

# Locations to draw text (x, y, delta-y if applicable)
TEXT_LOC = {}
# Maze draw text
TEXT_LOC["maze_draw"] = (1120, 50, 50)
TEXT_LOC["level_speed"] = (1455, 350)
TEXT_LOC["corn"] = (1168, 760)
TEXT_LOC["tomato"] = (1306, 760)
TEXT_LOC["pumpkin"] = (1448, 760)
TEXT_LOC["maze_load"] = (275, 850)
# Maze asset placement text
TEXT_LOC["place_assets_row_1"] = (1120, 100, 40)
TEXT_LOC["place_assets"] = (1120, 100, 50)
TEXT_LOC["assets"] = (1130, 400, 30)
# Title screen text
TEXT_LOC["animation_info"] = (1140, 50, 50)
TEXT_LOC["title"] = (275, 200)
TEXT_LOC["author"] = (300, 320)
TEXT_LOC["version"] = (325, 370)
TEXT_LOC["proceed"] = (260, 450)
# Game text
TEXT_LOC["level_score_lives"] = (1140, 50, 50)
TEXT_LOC["level_value"] = (1250, 50)
TEXT_LOC["score_value"] = (1250, 100)
TEXT_LOC["lives_value"] = (1250, 150)
TEXT_LOC["endgame"] = (1140, 200, 50)
TEXT_LOC["controls"] = (1140, 300, 50)
TEXT_LOC["instructions"] = (1140, 600, 50)
TEXT_LOC["pause"] = (500, 850)

# Location of images for level builder:
IMAGE_LOC = {}
IMAGE_LOC["corn"] = (1150, 700)
IMAGE_LOC["tomato"] = (1290, 700)
IMAGE_LOC["pumpkin"] = (1430, 700)


# Locations to update screen (x, y, width, height)
BLACK_RECTS = {}
BLACK_RECTS["controls"] = (1130, 290, 450, 300)
BLACK_RECTS["animation"] = (1130, 240, 300, 50)
BLACK_RECTS["assets"] = (1110, 390, 370, 260)
WHITE_RECTS = {}
WHITE_RECTS["assets"] = (1120, 50, WIDTH - 1140, HEIGHT - 50)
WHITE_RECTS["speed"] = (1450, 350, 400, 100)
WHITE_RECTS["corn"] = (1170, 780, BLOCK_WIDTH * SCALE_FACTOR)
WHITE_RECTS["tomato"] = (1310, 780, BLOCK_WIDTH * SCALE_FACTOR)
WHITE_RECTS["pumpkin"] = (1450, 780, BLOCK_WIDTH * SCALE_FACTOR)
WHITE_RECTS["maze_load"] = (250, 850, 700, 100)


# Set game tick speed to such that movement calculation is no more than one
# coordinate per tick, and defined speeds have meaningful changes to gameplay
# e.g., ticks needed to move one coordinate:
# slow:     144 * 5 = 720
# medium:   180 * 4 = 720
# fast:     240 * 3 = 720
# frantic:  360 * 2 = 720
GAME_TICK = 1 / 720

# Strings and supporting data for errors
ERROR_STRINGS = {}
ALLOWABLE_LETTERS = ["S", "R", "E", "1", "2", "3", "4", "H"]
ERROR_STRINGS["asset_letter"] = (
    "Level error! The asset coordinates csv must include exactly 8 unique asset "
    "locations, assigned to each of the following: "
)
ERROR_STRINGS["maze_fidelity"] = "Maze fidelity not a valid option."
ERROR_STRINGS["controls"] = "Controls scheme setting is not a valid option."

# Strings and supporting data for messages
MSG_STRING = {}
MSG_STRING["all_assets"] = (
    "Ensure all assets are placed before final export!\n\n"
    "If there is insufficient space, it may be necessary to exit and restart the drawing.\n\n"
    "Click OK then click back onto Level Builder window."
)
MSG_STRING["asset_space"] = (
    "Maze has insufficient space for assets.\n\n"
    "Path area must equal at least 8 full squares.\n\n"
    "Click OK then click back onto Level Builder window."
)
MSG_STRING["maze_folder"] = (
    "Please create a new folder"
    " at the location shown in the next dialog box, then select that "
    "new folder.\n\nUse a folder name such as custom_map_01."
    "\n\nClick OK to proceed."
)

# Image names for sprites, used for initial draw and animation
IMAGE_SERIES = {}
IMAGE_SERIES["corn"] = (
    "corn",
    "corn_flat_01",
    "corn_flat_02",
    "corn_flat_03",
    "corn_flat_04",
    "empty",
)
IMAGE_SERIES["tomato"] = (
    "tomato",
    "tomato_flat_01",
    "tomato_flat_02",
    "tomato_flat_03",
    "tomato_flat_04",
    "empty",
)
IMAGE_SERIES["blast"] = (
    "projectile_hit_01",
    "projectile_hit_02",
    "projectile_hit_03",
    "projectile_hit_02",
    "projectile_hit_01",
)
IMAGE_SERIES["pumpkin"] = ("pumpkin", "pumpkin_fire", "pumpkin")
IMAGE_SERIES["door"] = (
    "door",
    "door",
    "door_open_01",
    "door_open_02",
    "door_open_03",
    "door_open_04",
)

# Delays for animations
DELAYS = {}
DELAYS["corn"] = [0.1, 0.15, 0.2, 0.25, 0.3]
DELAYS["tomato"] = [0.1, 0.15, 0.2, 0.25, 0.3]
DELAYS["pumpkin"] = [0.1, 0.4]
DELAYS["blast"] = [0.05, 0.1, 0.15, 0.2]
DELAYS["door"] = [0.2, 0.4, 0.6, 0.8, 1.0]

# Score amounts
SCORES = {}
SCORES["item"] = 200
SCORES["corn"] = 50
SCORES["tomato"] = 100

# Pause amounts
PAUSES = {}
PAUSES["player_hit_enemy"] = 0.5
PAUSES["door_closed"] = 0.5
PAUSES["endgame"] = 3

# Default for lives
LIVES_DEFAULT = 5

# Title text
TITLE_TEXT = "Snack Attack"
AUTHOR_TEXT = "Programmed in Python by Tim Roble"
VERSION_TEXT = "Version 1.1.1, September 2025"
PROCEED_TEXT = "Press Spacebar to Start Game"

# Animation info strings
ANIMATION_STRINGS = [
    "Press F5 to cycle",
    "animation smoothness",
    "",
    "Current option: ",
    "",
    "",
    "'normal' or 'fine' options",
    "may be laggy on slower",
    "PCs. Sprites should",
    "maintain same speed when",
    "toggling. If they appear",
    "slower, revert to a more",
    "coarse setting.",
]

# Asset definitions for level builder placement
ASSET_DEFS = [
    {
        "letter": "S",
        "description": "Player start location",
        "color": COLORS["green"],
        "location": (),
    },
    {
        "letter": "R",
        "description": "Player respawn location",
        "color": COLORS["dkgreen"],
        "location": (),
    },
    {
        "letter": "E",
        "description": "Enemy start location",
        "color": COLORS["red"],
        "location": (),
    },
    {
        "letter": "1",
        "description": "Item 1 location",
        "color": COLORS["blue"],
        "location": (),
    },
    {
        "letter": "2",
        "description": "Item 2 location",
        "color": COLORS["magenta"],
        "location": (),
    },
    {
        "letter": "3",
        "description": "Item 3 location",
        "color": COLORS["orange"],
        "location": (),
    },
    {
        "letter": "4",
        "description": "Item 4 location",
        "color": COLORS["yellow"],
        "location": (),
    },
    {
        "letter": "H",
        "description": "Exit location",
        "color": COLORS["white"],
        "location": (),
    },
]
