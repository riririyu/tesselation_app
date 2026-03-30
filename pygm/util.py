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

def save_tile_as_svg(directory_path, tiles, width_str, height_str, screen_size):
    import os

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    for i in range(1, config.NUM_TYPE + 1):
        type_tiles = [t for t in tiles if t.type == i]
        if not type_tiles:
            continue
        file_name = os.path.join(directory_path, f"{i}_tile.svg")
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

def save_edge_as_json(directory_path, edge_manager):
    import os

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    filename = os.path.join(directory_path, "edge.json")
    with open(filename, "w") as f:
        json.dump(edge_manager.export(), f, indent=4)
    
    print(f"JSON file saved as {filename}")

def save_part_as_svg(directory_path, parts, width_str, height_str, screen_size):
    import os

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    for p in parts:
        file_name = os.path.join(directory_path, f"{p.type}.svg")
        dwg = svgwrite.Drawing(
            file_name, profile="basic", size=((width_str, height_str))
        )
        dwg.viewbox(0, 0, screen_size[0], screen_size[1])
        for center in p.centers:
            vertices=[]
            for i in range(6):
                angle_deg = math.radians(60 * i - 30)
                x = center[0] + p.size * math.cos(angle_deg)
                y = center[1] + p.size * math.sin(angle_deg)
                vertices.append((x + p.pos[0], y + p.pos[1]))
            dwg.add(
                dwg.polygon(
                    points=vertices, fill=config.TILE_COLOR[p.type], stroke="black", stroke_width=1
                )
            )

        dwg.save()
        print(f"SVG file saved as {file_name}")


def save_data(tiles, parts, edges):
    export_data = {
        "pixel_per_cm": config.PIXEL_PER_CM,
        "size": config.TILE_SIZE_CM,
        "tiles": [],
        "parts": [],
        "edges": []
    }
    
    for t in tiles:
        if t.type is not None:
            export_data["tiles"].append(t.save())
    for p in parts:
        export_data["parts"].append(p.save())
    for e in edges:
        export_data["edges"].append(e.save())
    with open(config.SAVED_DATA_PATH, "w") as f:
        json.dump(export_data, f, indent=4)
        
    print(f"Data saved as {config.SAVED_DATA_PATH}")

   

def load_data(tiles, canvas_handler, edge_manager):
    filename = config.SAVED_DATA_PATH
    if not filename.exists():
        print(f"File {filename} does not exist.")
        return None

    with open(filename, "r") as f:
        loaded_content = json.load(f)

    old_ppcm = loaded_content.get("pixel_per_cm", config.PIXEL_PER_CM)
    scale_factor = config.PIXEL_PER_CM / old_ppcm
    loaded_tiles=sync_tiles(tiles,loaded_content["tiles"], scale_factor)
    parts=loaded_content.get("parts", [])
    canvas_handler.load_parts_data(parts, scale_factor)
    edges=loaded_content.get("edges", [])
    edge_manager.load(edges, canvas_handler.parts)
    
    return loaded_tiles

def sync_tiles(tiles, data, scale_factor):
    for t in tiles:
        t.type = 0
    for coord in data:
        adjusted_x = coord["center"][0] * scale_factor
        adjusted_y = coord["center"][1] * scale_factor
        p1 = (adjusted_x, adjusted_y)
        for t in tiles:
            p2 = (t.center[0], t.center[1])
            distance = math.dist(p1, p2)
            if distance < config.TILE_SIZE_PIX * 0.2:
                t.type = coord["type"]
                break
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

def draw_color_legend(screen,  start_x, start_y):
    font = pygame.font.Font(None, 24)
    item_height = 30  # 各項目の高さ
    for type_idx, color in config.TILE_COLOR.items():
        rect_x = start_x
        rect_y = start_y + (type_idx * item_height)
        pygame.draw.rect(screen, color, (rect_x, rect_y, 20, 20))
        pygame.draw.rect(screen, (200, 200, 200), (rect_x, rect_y, 20, 20), 1)
        
        text_surface = font.render(f"Type: {type_idx}", True, (0, 0, 0))
        screen.blit(text_surface, (rect_x + 30, rect_y))
    
