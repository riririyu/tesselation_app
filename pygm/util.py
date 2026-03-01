import ezdxf
import pygame
import config
import svgwrite
import json
import math
import xml.etree.ElementTree as ET


def export_to_dxf(filename, screen, tiles):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    for tile in tiles:
        dxf_points = [(int(p[0]), int(p[1])) for p in tile.points]
        msp.add_lwpolyline(dxf_points, close=True)
    doc.saveas(filename)
    print(f"Exported {len(tiles)} tiles to {filename}")
    pygame.image.save(screen, "puzzle.png")
    print("Saved puzzle image as puzzle.png")


def get_svg_dimensions(file_path, mode: str):
    # XMLを解析
    tree = ET.parse(file_path)
    root = tree.getroot()

    # root（<svg>タグ）から属性を取得
    width_str = root.get("width")
    height_str = root.get("height")
    # viewbox_str = root.get('viewBox')
    if mode == "str":
        return width_str, height_str
    elif mode == "float":
        width = float(width_str.replace("cm", ""))
        height = float(height_str.replace("cm", ""))
        return width, height


def save_as_svg(directory_path, tiles, width_str, height_str, screen_size):
    import os

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    for i in range(1, config.NUM_TYPE + 1):
        type_tiles = [t for t in tiles if t.type == i]
        if not type_tiles:
            continue
        file_name = os.path.join(directory_path, f"{i}.svg")
        dwg = svgwrite.Drawing(
            file_name, profile="basic", size=((width_str, height_str))
        )
        dwg.viewbox(0, 0, screen_size[0], screen_size[1])
        for t in type_tiles:
            vertices = [(float(p[0]), float(p[1])) for p in t.points]
            dwg.add(
                dwg.polygon(
                    points=vertices, fill="#FFFFFF", stroke="black", stroke_width=1
                )
            )

        dwg.save()
        print(f"SVG file saved as {file_name}")


def save_data(tiles):
    # 1. 保存用の大きな辞書を作成
    export_data = {
        "pixel_per_cm": config.PIXEL_PER_CM,  # 一番最初に記述
        "tiles": []                           # タイルデータのリスト
    }
    
    # 2. タイルデータを抽出してリストに追加
    for t in tiles:
        if t.type is not None:
            export_data["tiles"].append({
                "x": t.center[0], 
                "y": t.center[1], 
                "type": t.type
            })
            
    # 3. ファイルに書き出し
    with open(config.SAVED_DATA_PATH, "w") as f:
        json.dump(export_data, f, indent=4)
        
    print(f"Data saved as {config.SAVED_DATA_PATH}")

   

def load_data(tiles):
    filename = config.SAVED_DATA_PATH
    if not filename.exists():
        print(f"File {filename} does not exist.")
        return None

    with open(filename, "r") as f:
        loaded_content = json.load(f)

    old_ppcm = loaded_content.get("pixel_per_cm", config.PIXEL_PER_CM)
    scale_factor = config.PIXEL_PER_CM / old_ppcm

    for t in tiles:
        t.type = 0

    saved_tiles = loaded_content.get("tiles", [])
    
    for coord in saved_tiles:
        adjusted_x = coord["x"] * scale_factor
        adjusted_y = coord["y"] * scale_factor
        
        p1 = (adjusted_x, adjusted_y)
        
        for t in tiles:
            p2 = (t.center[0], t.center[1])
            distance = math.dist(p1, p2)
            
            if distance < config.TILE_SIZE_PIX * 0.2:
                t.type = coord["type"]
                break 
    print(f"Data loaded from {filename} with scale factor: {scale_factor:.2f}")
    return tiles

def create_grid(width, height, tile_size, Tile):
    tiles = []
    w_step = tile_size * math.sqrt(3) / 2.0
    h_step = tile_size * 3.0

    for i in range(int(height / w_step)+1):
        for j in range(int(width / h_step)+1):
            x = i * w_step
            y = j * h_step
            if i % 2 == 1:
                y += h_step / 2
            tiles.append(Tile(x, y, tile_size))
    return tiles


def draw_calibration_ruler(screen, SCREEN_SIZE):

    ruler_length_cm = config.TILE_SIZE_CM
    pixel_length = ruler_length_cm * config.PIXEL_PER_CM
    start_pos = (20, SCREEN_SIZE[1] - config.UI_PANEL_HEIGHT // 2)
    end_pos = (
        20+ pixel_length,
        SCREEN_SIZE[1] - config.UI_PANEL_HEIGHT // 2,
    )
    pygame.draw.line(screen, (0, 0, 0), start_pos, end_pos, 2)
    font = pygame.font.Font(None, 24)
    img = font.render(f"the size of circumcircle:{ruler_length_cm} cm", True, (0, 0, 0))
    screen.blit(img, (start_pos[0], start_pos[1] + 5))

    w,h = get_svg_dimensions(config.SVG_PATH, mode="float")
    w *= config.PIXEL_PER_CM
    h *= config.PIXEL_PER_CM
    pos=[(0, h*0.99),(w*0.99, h*0.99),(w*0.99, h*0.99)]
    pygame.draw.lines(screen, (0, 0, 0), False, pos, 2)
    
