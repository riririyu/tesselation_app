import pygame
import json
import math
import config
import tile
import util
import import_pattern
from pathlib import Path
import numpy as np

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
    screen = pygame.display.set_mode(config.SCREEN_SIZE)
    under_lay = pygame.Surface(config.SCREEN_SIZE)
    under_lay.fill((255,255,255))
    import_pattern.draw_panels(under_lay, data,config.PATTERN_SCALE)
    tiles=[tile.HexTile(200,200,config.TILE_SIZE) for i in range(200)]
    spawner_tiles=[]
    need_update=False

    selected_tile = None
    offset_x, offset_y =0,0
    running = True
    clock = pygame.time.Clock()
    while running:

        screen.fill((255,255,255))
        screen.blit(under_lay, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for t in reversed(tiles):
                    if t.is_clicked(event.pos):
                        selected_tile = t
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_tile:
                    for other in tiles:
                        if other !=selected_tile:
                            if selected_tile.snap_to_grid(other):
                                break
                selected_tile = None
            
            elif event.type== pygame.MOUSEMOTION:
                if selected_tile:
                    selected_tile.move(event.rel[0], event.rel[1])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    util.export_to_dxf("puzzle.dxf",screen,tiles)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button ==4:
                    print("Mouse wheel up")
                    scale*=1.1
                    need_update=True
                elif event.button ==5:
                    print("Mouse wheel down")
                    scale*=0.9
                    need_update=True
        if need_update:
            print("Updating pattern with scale:", scale)
            import_pattern.draw_panels(under_lay, data,scale)

        for t in tiles:
            t.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()

