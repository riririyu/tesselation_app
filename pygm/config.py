from pathlib import Path
import pygame

PARENT_DIR = Path(__file__).parent.parent
CURRENT_DIR = Path(__file__).parent

# input
JSONPATH = Path(PARENT_DIR / "input" / "pattern" / "Dress.json")
PDF_PATH = Path(PARENT_DIR / "input" / "pattern" / "Dress.pdf")
SVG_PATH = Path(PARENT_DIR / "input" / "pattern" / "Dress.svg")
# output
SAVED_DATA_PATH = Path(CURRENT_DIR / "data.json")
SVG_OUTPUT_DIR = Path(PARENT_DIR / "svg_output")

# Tile setting
NUM_TYPE = 10
LINE_COLOR = (0, 0, 0)
TILE_COLOR = {
    0: "#FFFFFFC2",
    1: "#E0E011",  # 黄色 (Yellow)
    2: "#00FF00",  # 緑 (Green)
    3: "#0000FF",  # 青 (Blue)
    4: "#FF0000",  # 赤 (Red)
    5: "#800080",  # 紫 (Purple)
    6: "#FFA500",  # オレンジ (Orange)
    7: "#00FFFF",  # シアン (Cyan)
    8: "#FFC0CB",  # ピンク (Pink)
    9: "#A52A2A",  # 茶色 (Brown)
}
TILE_NAME = {
    "btorso_r",
    "btorso_l",
    "ftorso_r",
    "ftorso_l",
    "bsleeve_r",
    "bsleeve_l",
    "fsleeve_r",
    "fsleeve_l",
}

# scale setting
PIXEL_PER_CM = 6.0
TILE_SIZE_CM = 2.5
TILE_SIZE_PIX = float(TILE_SIZE_CM * PIXEL_PER_CM)

# PATTERN_SCALE = 5.0

# UI setting
UI_PANEL_HEIGHT = 100
BUTTON_SIZE = (100, 40)

button_space_width = 1.5 * BUTTON_SIZE[0]
button_space_height = 1.5 * BUTTON_SIZE[1]
