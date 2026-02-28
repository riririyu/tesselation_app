import pygame
import json
import pygame_gui
import config
import tile
import util
import math
import import_pattern
from pathlib import Path
import numpy as np


from input_hundler import InputHandler

handler = InputHandler()


def main():
    print(type(config.JSONPATH))
    if not config.JSONPATH.exists():
        print(f"Error: JSON file not found at {config.JSONPATH}")
        return
    with config.JSONPATH.open("r", encoding="utf-8") as f:
        pattern_data = json.load(f)
        data = pattern_data["pattern"]
    import_pattern.unify_edge_data(data["panels"])

    pygame.init()
    w, h = util.get_svg_dimensions(config.SVG_PATH, mode="float")
    SCREEN_SIZE=(config.SCREEN_SIZE_WIDTH, int(config.SCREEN_SIZE_WIDTH * h / w))

    screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
    manager = pygame_gui.UIManager(SCREEN_SIZE)
    SAVE_BUTTON_RECT = pygame.Rect(
    int(config.button_space_width /2),
    int(SCREEN_SIZE[1] -config.UI_PANEL_HEIGHT + config.button_space_height // 2),
    config.BUTTON_SIZE[0],
    config.BUTTON_SIZE[1]
    )
    LOAD_BUTTON_RECT = pygame.Rect(
    int(config.button_space_width /2 + config.button_space_width),
    int(SCREEN_SIZE[1] -config.UI_PANEL_HEIGHT + config.button_space_height // 2),
    config.BUTTON_SIZE[0],
    config.BUTTON_SIZE[1]
    )
    save_btn = pygame_gui.elements.UIButton(
        relative_rect=SAVE_BUTTON_RECT,
        text="SAVE",
        manager=manager,
    )

    load_btn = pygame_gui.elements.UIButton(
        relative_rect=LOAD_BUTTON_RECT,
        text="LOAD",
        manager=manager,
    )

    under_lay = import_pattern.load_svg_as_surface_with_scale(config.SVG_PATH)

    tiles = util.create_grid(
        SCREEN_SIZE[1]-config.UI_PANEL_HEIGHT, SCREEN_SIZE[0], config.TILE_SIZE_PIX, tile.HexTile
    )

    selected_tile = None
    running = True
    clock = pygame.time.Clock()
    while running:
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == save_btn:
                    util.save_data("data.json", tiles)
                elif event.ui_element == load_btn:
                    loaded_coords = util.load_data("data.json")
                    for t in tiles:
                        t.type = 0
                    for coord in loaded_coords:
                        for t in tiles:
                            p1 = (coord["x"], coord["y"])
                            p2 = (t.center[0], t.center[1])
                            distance = math.dist(p1, p2)
                            if distance < config.TILE_SIZE_PIX * 0.2:
                                t.type = coord["type"]
                                break

            manager.process_events(event)
            handler.handle_event(event, tiles, screen)

        manager.update(time_delta)

        screen.fill((255, 255, 255))  # draw background
        screen.blit(under_lay, (0, 0))  # draw underlay
        for t in tiles:
            t.draw(screen)
        manager.draw_ui(screen)
        util.draw_calibration_ruler(screen, SCREEN_SIZE)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
