import pygame
import util

class InputHandler:
    def __init__(self):
        self.is_left_constrained = False

    def handle_event(self, event, tiles,screen):
        mods=pygame.key.get_mods()
        is_ctrl_pressed=mods & pygame.KMOD_CTRL

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_left_constrained = True
                state=True if is_ctrl_pressed else None
                self._toggle_tile_at_pos(event.pos, tiles, force_state=state)

        # 2. ボタンを離した瞬間
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_left_constrained = False

        # 3. マウス移動中（ドラッグ中）
        elif event.type == pygame.MOUSEMOTION:
            if self.is_left_constrained and is_ctrl_pressed:
                self._toggle_tile_at_pos(event.pos, tiles, force_state=True)
        
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_r:
                self._deactivate_all(tiles)
            if event.key == pygame.K_s:
                util.export_to_dxf("puzzle.dxf",screen,tiles)



    def _toggle_tile_at_pos(self, pos, tiles, force_state=None):
        """指定座標にあるタイルの状態を切り替える"""
        for t in tiles:
            if t.is_clicked(pos):
                if force_state is not None:
                    t.is_active = force_state
                else:
                    t.is_active = not t.is_active
                
                break

    def snap_near_tile(self, tiles):

        if selected_tile:
            for other in tiles:
                if other !=selected_tile:
                    if selected_tile.snap_to_grid(other):
                        break
                selected_tile = None

    def move_selected_tile(selected_tile, dx, dy):
        if selected_tile:
            selected_tile.move(0,0)
            # selected_tile.move(event.rel[0], event.rel[1])

    def _clear_all_tiles(self, tiles):
        for t in tiles:
            t.is_active=False
