import pygame
import util
import tkinter as tk
from tkinter import filedialog
import config
import numpy as np
import part_edge
import math

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
                cvh.edge_manager.clear_edges()
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


                util.save_part_as_svg(
                    directory_path, cvh.parts, width_str, height_str, screen_size
                )
            if pygame.K_0 <= event.key <= pygame.K_9:
                self.current_type = event.key - pygame.K_0
            if event.key == pygame.K_s:
                util.save_data( tiles, cvh.parts, cvh.edge_manager.manual_edges)
            if event.key == pygame.K_l:
                tiles = util.load_data(tiles, cvh,cvh.edge_manager)
                threshold = config.TILE_SIZE_PIX*0.5
                cvh.edge_manager.auto_connect(cvh.parts, threshold)
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
        self.edge_manager=part_edge.EdgeManager()
        self.selected_v=None

    def handle_event(self, event):
        mouse_pos = getattr(event, "pos", None)
        is_inside = mouse_pos and self.rect.collidepoint(mouse_pos)
        if event.type == pygame.KEYDOWN:
            if pygame.K_0 <= event.key <= pygame.K_9:
                self.current_type = event.key - pygame.K_0
            if event.key == pygame.K_e:
                directory_name = "hextile"
                import os
                directory_path = os.path.join(config.SVG_OUTPUT_DIR, directory_name)
                util.save_edge_as_json(directory_path, self.edge_manager)

        if event.type == pygame.MOUSEBUTTONDOWN and is_inside:
            if event.button == 1:
                clicked_v = None
                adjusted_pos=(event.pos[0]-self.rect.x, event.pos[1] -self.rect.y)

                for part in reversed(self.parts):
                    print("clicked")
                    print(f"Selected vertex: {self.selected_v}")
                    for v_idx, v in enumerate(part.vertices):
                        dist=math.hypot(v[0]-adjusted_pos[0], v[1]-adjusted_pos[1])
                        print(dist)
                        if dist< config.TILE_SIZE_PIX * 0.3:
                            clicked_v=(part,v_idx)
                            break
                if clicked_v:
                    if self.selected_v is None:
                        self.selected_v = clicked_v
                        print(f"Selected vertex: {self.selected_v}")
                    else:
                        print(f"Selected vertex already exist")
                        p1, v1 = self.selected_v
                        p2, v2 = clicked_v
                        if p1.type != p2.type:
                            self.edge_manager.operate_edge_manually(p1,p2,v1, v2)
                        self.selected_v = None
                    return


                for part in reversed(self.parts):
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
                    threshold = config.TILE_SIZE_PIX*0.5
                    self.edge_manager.auto_connect(self.parts, threshold)
                    self.selected_part.is_dragging = False
                    self.selected_part = None





    def add_parts(self,centers,type,pos=(0,0)):
        part_instance = part_edge.Part(centers, type)
        part_instance.pos = np.array(pos, dtype=float)
        self.parts.append(part_instance)

    def draw(self, screen):
        for part in self.parts:
            part.draw(screen)
        self.edge_manager.draw(screen)

    def sync_parts_from_tiles(self, tiles):
        offsets={}
        for p in self.parts:
            offsets[p.type]=p.pos
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
            part_instance = part_edge.Part(part_data["centers"], part_data["type"])
            part_instance.pos = np.array(part_data["pos"], dtype=float)
            self.parts.append(part_instance)