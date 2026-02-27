import ezdxf
import pygame
from config import CURRENT_DIR
import svgwrite
import json
import math
import config

DATA_TO_LOAD = CURRENT_DIR/"data.json"
OUTPUT_DIR = CURRENT_DIR/"output"

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

def save_as_svg(directory_path, tiles):
    import os
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    for i in range(1,config.num_Type+1):
        type_tiles=[t for t in tiles if t.type == i]
        if not type_tiles:
            continue
        file_name = os.path.join(directory_path, f"{i}.svg")
        dwg=svgwrite.Drawing(file_name, profile='tiny',size=(config.SCREEN_SIZE[0], config.SCREEN_SIZE[1]))
        for t in type_tiles:
            vertices=[(int(p[0]), int(p[1])) for p in t.points]
            dwg.add(dwg.polygon(points=vertices,
                        fill="#FFFFFF",
                        stroke='black',
                        stroke_width=1
                        ))
    
        dwg.save()
        print(f"SVG file saved as {file_name}")

def save_data(filename, tiles):
    data=[]
    for t in tiles:
        if t.type is not None:
            data.append({"x": t.center[0], "y": t.center[1], "type": t.type})
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
def draw_calibration_ruler(screen):
    ruler_length_cm=config.TILE_SIZE_CM
    pixel_length = ruler_length_cm * config.PIXEL_PER_CM
    start_pos = (10, config.SCREEN_SIZE[1] - 20)
    end_pos=(10 + pixel_length, config.SCREEN_SIZE[1] - 20
             )
    pygame.draw.line(screen, (0, 0, 0), start_pos, end_pos, 2)
    font = pygame.font.Font(None, 24)
    img = font.render(f"the size of circumcircle:{ruler_length_cm} cm", True, (0, 0, 0))
    screen.blit(img, (start_pos[0], start_pos[1]))
