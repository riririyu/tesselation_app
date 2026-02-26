import ezdxf
import pygame
from config import CURRENT_DIR
import svgwrite
import json
import math

DATA_TO_LOAD = CURRENT_DIR/"data.json"

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

def save_as_svg(filename, tiles):
    dwg=svgwrite.Drawing(filename, profile='tiny')

    for t in tiles:
        vertices=[(int(p[0]), int(p[1])) for p in t.points]
        dwg.add(dwg.polygon(points=vertices,
                            fill=None,
                            stroke='black',
                            stroke_width=1
                            ))
    
    dwg.save()
    print(f"SVG file saved as {filename}")

def save_data(filename, tiles):
    data=[{"x":t.center[0], "y":t.center[1]} for t in tiles]
    with open(filename,"w")as f:
        json.dump(data,f,indent=4)
    print(f"Data saved as {filename}")
def load_data(filename):
    target_file = CURRENT_DIR / filename
    if not target_file.exists():
        print(f"File {filename} does not exist.")
        return None
    with open(target_file, "r") as f:
        data = json.load(f)

    return data

def create_grid(width, height, tile_size,Tile):
    tiles = []
    w_step = tile_size * math.sqrt(3)/2
    h_step = tile_size * 3
    for i in range(int(height/w_step)+1):
        for j in range(int(width/h_step)+1):
            x = i * w_step
            y = j * h_step
            if i % 2 == 1:
                y += h_step / 2
            tiles.append(Tile(x, y, tile_size))
    return tiles