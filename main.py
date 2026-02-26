import pygame
import json
import pygame_gui
import config
import tile
import util
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
        data=pattern_data["pattern"]
    import_pattern.unify_edge_data(data["panels"])

    pygame.init()
    screen = pygame.display.set_mode(config.SCREEN_SIZE,pygame.RESIZABLE)
    manager = pygame_gui.UIManager(config.SCREEN_SIZE)

    save_btn=pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(config.SAVE_BUTTON_POS, config.BUTTON_SIZE),
        text="SAVE",
        manager=manager
    )

    load_btn=pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(config.LOAD_BUTTON_POS, config.BUTTON_SIZE),
        text="LOAD",
        manager=manager
    )
    under_lay_original = import_pattern.load_pdf_as_surface(config.PDF_PATH, 0,scale=2.0)
    under_lay = pygame.transform.smoothscale(under_lay_original, config.SCREEN_SIZE)
    
    tiles = util.create_grid(config.SCREEN_SIZE[1], config.SCREEN_SIZE[0], config.TILE_SIZE, tile.HexTile)

    selected_tile = None
    running = True
    clock = pygame.time.Clock()
    while running:
        time_delta=clock.tick(60)/1000.0



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type==pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == save_btn:
                    util.save_data("data.json",tiles)
                    print("Save button pressed")
                elif event.ui_element == load_btn:
                    loaded_coords=util.load_data("data.json")
                    for t in tiles:
                        t.is_active = False
                    for coord in loaded_coords:
                        for t in tiles:
                            if t.center[0] == coord["x"] and t.center[1] == coord["y"]:
                                t.is_active = True
                                break

                    
                    print("Load button pressed")
            if event.type==pygame.VIDEORESIZE:
                new_size=event.size
                screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
                manager.set_window_resolution(new_size)
                under_lay = pygame.Surface(new_size)
                under_lay.fill((255,255,255))
                import_pattern.draw_panels(under_lay, data,config.PATTERN_SCALE)

            
            manager.process_events(event)
            handler.handle_event( event, tiles,screen)


            
        manager.update(time_delta)

        screen.fill((255,255,255))
        screen.blit(under_lay, (0, 0))
        for t in tiles:
            t.draw(screen)
        manager.draw_ui(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()

