from pathlib import Path
import pygame
CURRENT_DIR = Path(__file__).parent
JSONPATH = Path(CURRENT_DIR / "input"/"pattern"/"Dress.json")
PDF_PATH = Path(CURRENT_DIR / "input"/"pattern"/"Dress.pdf")

LINE_COLOR = (0, 0, 0)
TILE_COLOR = (150, 200, 200)
TILE_SIZE = 20
SCREEN_SIZE = (3600, 1600)
PATTERN_SCALE = 5.0

UI_PANEL_HEIGHT = 60
SAVE_BUTTON_POS = (10, 10)
LOAD_BUTTON_POS = (120, 10)
BUTTON_SIZE = (100, 40)

button_width=80
button_height=30
SAVE_BUTTON_RECT = pygame.Rect(
    int(SCREEN_SIZE[0] * 0.5 - button_width // 2), 
    int(SCREEN_SIZE[1] * 0.1), 
    button_width, 
    button_height
)
LOAD_BUTTON_RECT = pygame.Rect(
    int(SCREEN_SIZE[0] * 0.5 - button_width // 2), 
    int(SCREEN_SIZE[1] * 0.2), 
    button_width, 
    button_height
)