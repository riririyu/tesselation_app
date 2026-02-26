import ezdxf
import pygame
import config


def export_to_dxf(filename,screen,tiles):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    for tile in tiles:
        dxf_points = [(int(p[0]), int(p[1])) for p in tile.points]
        msp.add_lwpolyline(dxf_points, close=True)
    doc.saveas(filename)
    print(f"Exported {len(tiles)} tiles to {filename}")
    pygame.image.save(screen,"puzzle.png")
    print("Saved puzzle image as puzzle.png")