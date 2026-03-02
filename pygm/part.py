import pygame
import math
import config
import numpy as np

TILE_COLOR = config.TILE_COLOR
TILE_SIZE = config.TILE_SIZE_PIX
LINE_COLOR = config.LINE_COLOR

       
class Part:
    def __init__(self,centers,type):
        self.size = TILE_SIZE
        self.centers = centers
        self.origin = centers[0] if centers else (0, 0)
        self.type = type
        self.pos=np.array([0.0,0.0])
        self.is_dragging=False
        self.vertices=[]
        
        
    
    
    def draw(self, screen):
        
        color=pygame.Color(config.TILE_COLOR[self.type])
        self.vertices=[]
        for center in self.centers:
            tile_vertices=[]
            for i in range(6):
                angle_deg = math.radians(60 * i - 30)
                x = center[0] + self.size * math.cos(angle_deg)
                y = center[1] + self.size * math.sin(angle_deg)
                self.vertices.append((x + self.pos[0], y + self.pos[1]))
                tile_vertices.append((x + self.pos[0], y + self.pos[1]))
            pygame.draw.polygon(screen, color, tile_vertices)
        pygame.draw.circle(screen, (0,0,0), (int(self.origin[0] + self.pos[0]), int(self.origin[1] + self.pos[1])), 5)
    
    def is_clicked(self, pos):
        dist=math.hypot(pos[0]-self.origin[0]-self.pos[0], pos[1]-self.origin[1]-self.pos[1])
        return dist < self.size
    
    def move(self, dx, dy):
        self.pos += np.array([dx, dy])
    def save(self):
        return {
            "centers": self.centers,
            "type": self.type,
            "pos": self.pos.tolist()
        }

class Edge:
    def __init__(self, p1_idx, p2_idx, v1_pos, v2_pos):
        # どのパーツの、どの座標かを保持
        self.part_indices = frozenset([p1_idx, p2_idx])
        self.v1_pos = v1_pos
        self.v2_pos = v2_pos

class EdgeManager:
    def __init__(self):
        self.edges = []  # Edgeオブジェクトのリスト

    def draw(self, screen, color=(0, 0, 0)):
        for edge in self.edges:
            # 各Edgeオブジェクトが持つ座標を使って描画
            pygame.draw.line(screen, color, edge.v1_pos, edge.v2_pos, 2)

    def auto_connect(self, parts, threshold):
        self.edges.clear()  # 一旦すべて消去して再計算
        print("init:",len(self.edges))
        print("auto connect")
        for i, part1 in enumerate(parts):
            for j, part2 in enumerate(parts):
                if i >= j:
                    continue
                
                # 各パーツの現在の頂点座標（動的な位置）を取得
                # get_world_vertices() メソッドが Part クラスにあると想定
                v_list1 = part1.vertices
                v_list2 = part2.vertices
                for v1 in v_list1:
                    for v2 in v_list2:
                        dist = math.hypot(v1[0] - v2[0], v1[1] - v2[1])
                        if dist < threshold:
                            # 新しいEdgeインスタンスを作成して追加
                            new_edge = Edge(i, j, v1, v2)
                            self.edges.append(new_edge)
        print("final:", len(self.edges))
                            
