import pygame
import util
import tkinter as tk
from tkinter import filedialog
import config
import math
import part

root = tk.Tk()
root.withdraw()


class InputHandler:
    def __init__(self,rect):
        self.rect=rect
        self.is_left_constrained = False
        self.current_type = 1

    def handle_event(self, event, tiles, cvh):
        mouse_pos = getattr(event, "pos", None)
        is_inside = mouse_pos and self.rect.collidepoint(mouse_pos)
        mods = pygame.key.get_mods()
        is_ctrl_pressed = mods & pygame.KMOD_CTRL

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._clear_all_tiles(tiles)
            if event.key == pygame.K_e:
                directory_name = tiles[0].__class__.__name__.lower()
                import os

                directory_path = os.path.join(config.SVG_OUTPUT_DIR, directory_name)
                width_str, height_str = util.get_svg_dimensions(
                    config.SVG_PATH, mode="str"
                )
                width, height = util.get_svg_dimensions(config.SVG_PATH, mode="float")

                screen_size = (
                    width * config.PIXEL_PER_CM,
                    height * config.PIXEL_PER_CM,
                )

                util.save_as_svg(
                    directory_path, tiles, width_str, height_str, screen_size
                )
            if pygame.K_0 <= event.key <= pygame.K_9:
                self.current_type = event.key - pygame.K_0
            if event.key == pygame.K_s:
                util.save_data( tiles)
            if event.key == pygame.K_l:
                tiles = util.load_data(tiles)

            if event.key == pygame.K_o:
                print("o pushed")
                if self.current_type:
                    print("current_type:", self.current_type)
                    type_tiles = [t for t in tiles if t.type == self.current_type]
                    if type_tiles:
                        centers = []
                        for t in type_tiles:
                            centers.append([t.center[0], t.center[1]])
                        CanvasHandler.add_parts(cvh,centers=centers,type=self.current_type)

        if event.type == pygame.MOUSEBUTTONDOWN and is_inside:
            if event.button == 1:
                self.is_left_constrained = True
                state = self.current_type if is_ctrl_pressed else None
                self._toggle_tile_at_pos(event.pos, tiles, force_state=state)

        # 2. ボタンを離した瞬間
        elif event.type == pygame.MOUSEBUTTONUP and is_inside:
            if event.button == 1:
                self.is_left_constrained = False

        # 3. マウス移動中（ドラッグ中）
        elif event.type == pygame.MOUSEMOTION and is_inside:
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


    def _clear_all_tiles(self, tiles):
        for t in tiles:
            t.type = 0


class CanvasHandler:
    def __init__(self, rect):
        self.rect = rect
        self.parts = []
        self.selected_part = None
        self.current_type = 0
        self.camera_y = 0
        

    def handle_event(self, event):
        mouse_pos = getattr(event, "pos", None)
        is_inside = mouse_pos and self.rect.collidepoint(mouse_pos)
        if event.type == pygame.KEYDOWN:
                if pygame.K_0 <= event.key <= pygame.K_9:
                    self.current_type = event.key - pygame.K_0

        if event.type == pygame.MOUSEBUTTONDOWN and is_inside:
            if event.button == 1:
                print("Mouse button down at:", event.pos)
                for part in reversed(self.parts):
                    print("Checking part:", part.type)
                    adjusted_pos=(event.pos[0]-self.rect.x, event.pos[1] -self.rect.y - self.camera_y)
                    if part.is_clicked(adjusted_pos):
                        print("Part clicked:", part.type)
                        self.selected_part = part
                        part.is_dragging = True
                        break

        elif event.type == pygame.MOUSEBUTTONUP and is_inside:
            if event.button == 1:
                if self.selected_part:
                    self.selected_part.is_selected = False
                    self.selected_part = None

        elif event.type == pygame.MOUSEMOTION and is_inside:
            if self.selected_part and self.selected_part.is_dragging:
                self.selected_part.move(event.rel[0], event.rel[1])
        
        elif event.type==pygame.MOUSEWHEEL:
            self.camera_y+=5*event.y

    def add_parts(self,centers,type):
        self.parts.append(part.Part(centers, type))

    def draw(self, screen):
        for part in self.parts:
            part.draw(screen,self.camera_y)
    