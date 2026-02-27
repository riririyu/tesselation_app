from pathlib import Path
import pygame

CURRENT_DIR = Path(__file__).parent
JSONPATH = Path(CURRENT_DIR / "input" / "pattern" / "Dress.json")
PDF_PATH = Path(CURRENT_DIR / "input" / "pattern" / "Dress.pdf")
num_Type = 10
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

TILE_SIZE = 20
SCREEN_SIZE = (3600, 1600)
PATTERN_SCALE = 5.0

UI_PANEL_HEIGHT = 60
SAVE_BUTTON_POS = (10, 10)
LOAD_BUTTON_POS = (120, 10)
BUTTON_SIZE = (100, 40)

button_width = 80
button_height = 30
SAVE_BUTTON_RECT = pygame.Rect(
    int(SCREEN_SIZE[0] * 0.5 - button_width // 2),
    int(SCREEN_SIZE[1] * 0.1),
    button_width,
    button_height,
)
LOAD_BUTTON_RECT = pygame.Rect(
    int(SCREEN_SIZE[0] * 0.5 - button_width // 2),
    int(SCREEN_SIZE[1] * 0.2),
    button_width,
    button_height,
)
