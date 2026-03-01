import pygame
import util
import tkinter as tk
from tkinter import filedialog
import config
import numpy as np
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
                cvh.parts=[]
            if event.key == pygame.K_e:
                ("export to svg")
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

                util.save_tile_as_svg(
                    directory_path, tiles, width_str, height_str, screen_size
                )
                util.save_part_as_svg(
                    directory_path, cvh.parts, width_str, height_str, screen_size
                )
            if pygame.K_0 <= event.key <= pygame.K_9:
                self.current_type = event.key - pygame.K_0
            if event.key == pygame.K_s:
                util.save_data( tiles, cvh.parts)
            if event.key == pygame.K_l:
                tiles = util.load_data(tiles, cvh)
            if event.key == pygame.K_o:
                cvh.sync_parts_from_tiles(tiles)



        if event.type == pygame.MOUSEBUTTONDOWN and is_inside:
            if event.button == 1:
                self.is_left_constrained = True
                state = self.current_type if is_ctrl_pressed else None
                self._toggle_tile_at_pos(event.pos, tiles, force_state=state)

        # 2. ボタンを離した瞬間
        elif event.type == pygame.MOUSEBUTTONUP and is_inside:
            if event.button == 1:
                self.is_left_constrained = False
                cvh.sync_parts_from_tiles(tiles)

        # 3. マウス移動中（ドラッグ中）
        elif event.type == pygame.MOUSEMOTION and is_inside:
            if self.is_left_constrained and is_ctrl_pressed:
                self._toggle_tile_at_pos(
                    event.pos, tiles, force_state=self.current_type
                )

    def _toggle_tile_at_pos(self, pos, tiles, force_state=None):
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
        

    def handle_event(self, event):
        mouse_pos = getattr(event, "pos", None)
        is_inside = mouse_pos and self.rect.collidepoint(mouse_pos)
        if event.type == pygame.KEYDOWN:
                if pygame.K_0 <= event.key <= pygame.K_9:
                    self.current_type = event.key - pygame.K_0

        if event.type == pygame.MOUSEBUTTONDOWN and is_inside:
            if event.button == 1:
                for part in reversed(self.parts):
                    adjusted_pos=(event.pos[0]-self.rect.x, event.pos[1] -self.rect.y)
                    if part.is_clicked(adjusted_pos):
                        self.selected_part = part
                        part.is_dragging = True
                        break
        elif event.type == pygame.MOUSEMOTION and is_inside:
            if self.selected_part and self.selected_part.is_dragging:
                self.selected_part.move(event.rel[0], event.rel[1])


        elif event.type == pygame.MOUSEBUTTONUP and is_inside:
            if event.button == 1:
                if self.selected_part:
                    self.selected_part.is_dragging = False
                    self.selected_part = None



    def add_parts(self,centers,type,pos=(0,0)):
        part_instance = part.Part(centers, type)
        part_instance.pos = np.array(pos, dtype=float)
        self.parts.append(part_instance)

    def draw(self, screen):
        for part in self.parts:
            part.draw(screen)

    def sync_parts_from_tiles(self, tiles):
        offsets={}
        for p in self.parts:
            offsets[p.type]=p.pos
        print(offsets)
        self.parts=[]
        for type in range(1, config.NUM_TYPE+1):
            type_tiles = [t for t in tiles if t.type == type]
            current_offset = offsets.get(type, (0, 0))
            if type_tiles:
                centers = []
                for t in type_tiles:
                    centers.append([t.center[0], t.center[1]])
                self.add_parts(centers=centers,type=type,pos=current_offset)


    def load_parts_data(self, parts_data, scale_factor):
        self.parts = []
        for part_data in parts_data:
            for center in part_data["centers"]:
                center[0]*=scale_factor
                center[1]*=scale_factor
            part_instance = part.Part(part_data["centers"], part_data["type"])
            part_instance.pos = np.array(part_data["pos"], dtype=float)
            self.parts.append(part_instance)