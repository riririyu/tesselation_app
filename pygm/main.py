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
from input_hundler import CanvasHandler



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
    SCREEN_SIZE=(w*config.PIXEL_PER_CM, h*config.PIXEL_PER_CM+config.UI_PANEL_HEIGHT)
    screen = pygame.display.set_mode((SCREEN_SIZE[0], 2*SCREEN_SIZE[1]))
    manager = pygame_gui.UIManager(SCREEN_SIZE)
    main_rect=pygame.Rect(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])
    canvas_rect=pygame.Rect(0, SCREEN_SIZE[1], SCREEN_SIZE[0], SCREEN_SIZE[1])
    main_handler = InputHandler(main_rect)
    canvas_handler = CanvasHandler(canvas_rect)
    
    
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
    parts=[]

    selected_tile = None
    running = True
    clock = pygame.time.Clock()
    while running:
        main=screen.subsurface(main_rect)
        canvas=screen.subsurface(canvas_rect)
        time_delta = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == save_btn:
                    util.save_data( tiles)
                elif event.ui_element == load_btn:
                    tiles = util.load_data(tiles)

            manager.process_events(event)
            main_handler.handle_event(event, tiles,canvas_handler)
            canvas_handler.handle_event(event)

        manager.update(time_delta)

        # main
        main.fill((255, 255, 255))  # draw background
        main.blit(under_lay, (0, 0))  # draw underlay
        for t in tiles:
            t.draw(main)
        # canvas
        canvas.fill((255, 255, 255))  # draw background
        canvas_handler.draw(canvas)
        
        manager.draw_ui(screen)
        util.draw_calibration_ruler(main, SCREEN_SIZE)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
