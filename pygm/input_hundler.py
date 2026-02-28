import pygame
import util
import tkinter as tk
from tkinter import filedialog
import config
import math

root = tk.Tk()
root.withdraw()


class InputHandler:
    def __init__(self):
        self.is_left_constrained = False
        self.current_type = 1

    def handle_event(self, event, tiles, screen):
        mods = pygame.key.get_mods()
        is_ctrl_pressed = mods & pygame.KMOD_CTRL

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._clear_all_tiles(tiles)
            if event.key == pygame.K_s:
                directory_name = tiles[0].__class__.__name__.lower()
                import os

                directory_path = os.path.join(config.SVG_OUTPUT_DIR, directory_name)
                width_str, height_str = util.get_svg_dimensions(config.SVG_PATH, mode="str")
                width, height = util.get_svg_dimensions(config.SVG_PATH, mode="float")
                
                screen_size = (width*config.PIXEL_PER_CM, height*config.PIXEL_PER_CM)
                
                util.save_as_svg(directory_path, tiles, width_str, height_str, screen_size)
            if pygame.K_0 <= event.key <= pygame.K_9:
                self.current_type = event.key - pygame.K_0
            if event.key==pygame.K_l:
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

            

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_left_constrained = True
                state = self.current_type if is_ctrl_pressed else None
                self._toggle_tile_at_pos(event.pos, tiles, force_state=state)

        # 2. ボタンを離した瞬間
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_left_constrained = False

        # 3. マウス移動中（ドラッグ中）
        elif event.type == pygame.MOUSEMOTION:
            if self.is_left_constrained and is_ctrl_pressed:
                self._toggle_tile_at_pos(
                    event.pos, tiles, force_state=self.current_type
                )

    def _toggle_tile_at_pos(self, pos, tiles, force_state=None):
        """指定座標にあるタイルの状態を切り替える"""
        for t in tiles:
            if t.is_clicked(pos):
                if force_state is not None:
                    t.type = force_state
                else:
                    if t.type == self.current_type:
                        t.type = 0
                    else:
                        t.type = self.current_type

                break

    def snap_near_tile(self, tiles):

        if selected_tile:
            for other in tiles:
                if other != selected_tile:
                    if selected_tile.snap_to_grid(other):
                        break
                selected_tile = None

    def move_selected_tile(selected_tile, dx, dy):
        if selected_tile:
            selected_tile.move(0, 0)
            # selected_tile.move(event.rel[0], event.rel[1])

    def _clear_all_tiles(self, tiles):
        for t in tiles:
            t.type = 0
