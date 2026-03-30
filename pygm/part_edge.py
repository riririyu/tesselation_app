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
    def __init__(self, p1, p2, v1_idx, v2_idx):
        # どのパーツの、どの座標かを保持
        self.p1 = p1
        self.p2 = p2
        self.v1_idx = v1_idx
        self.v2_idx = v2_idx
    @property
    def v1_pos(self):
        return self.p1.vertices[self.v1_idx]   
    @property
    def v2_pos(self):
        return self.p2.vertices[self.v2_idx]   
    def save(self):
        return {
            "p1_idx": self.p1.type,
            "p2_idx": self.p2.type,
            "v1_idx": self.v1_idx,
            "v2_idx": self.v2_idx
        }

class EdgeManager:
    def __init__(self):
        self.auto_edges = []  # Edgeオブジェクトのリスト
        self.manual_edges = []  # Edgeオブジェクトのリスト
    
    def clear_edges(  self):
        self.auto_edges = []  # Edgeオブジェクトのリスト
        self.manual_edges = []  # Edgeオブジェクトのリスト

    def export(self):
        data={"edges": []}
        for edge in self.auto_edges + self.manual_edges:
            v1_pos_cm=[coord/config.PIXEL_PER_CM for coord in edge.v1_pos]
            v2_pos_cm=[coord/config.PIXEL_PER_CM for coord in edge.v2_pos]
            dict1=[{"idx": edge.p1.type,
                   "pos": v1_pos_cm},
                   {"idx": edge.p2.type,
                   "pos": v2_pos_cm}]
            data["edges"].append(dict1)
        return data


    def draw(self, screen, color=(0, 0, 0)):
        for edge in self.auto_edges + self.manual_edges:
            # 各Edgeオブジェクトが持つ座標を使って描画
            pygame.draw.line(screen, color, edge.v1_pos, edge.v2_pos, 2)

    def auto_connect(self, parts, threshold):
        self.auto_edges.clear()  # 一旦すべて消去して再計算
        print("init:",len(self.auto_edges))
        print("auto connect")
        for p1 in parts:
            for p2 in parts:
                t1=p1.type
                t2=p2.type
                if t1 >= t2:
                    continue
                
                # 各パーツの現在の頂点座標（動的な位置）を取得
                # get_world_vertices() メソッドが Part クラスにあると想定
                v_list1 = p1.vertices
                v_list2 = p2.vertices
                for v1_idx, v1 in enumerate(v_list1):
                    for v2_idx, v2 in enumerate(v_list2):
                        dist = math.hypot(v1[0] - v2[0], v1[1] - v2[1])
                        if dist < threshold:
                            # 新しいEdgeインスタンスを作成して追加
                            new_edge = Edge(p1, p2, v1_idx, v2_idx)
                            self.auto_edges.append(new_edge)
        print("final:", len(self.auto_edges))

    def operate_edge_manually(self, p1, p2, v1_idx, v2_idx):
        for e in self.auto_edges+self.manual_edges:
            if set([p1.vertices[v1_idx], p2.vertices[v2_idx]]) == set([e.v1_pos, e.v2_pos]):
                if e in self.auto_edges:
                    self.auto_edges.remove(e)
                if e in self.manual_edges:
                    self.manual_edges.remove(e)
                return
        new_edge = Edge(p1, p2, v1_idx, v2_idx)
        self.manual_edges.append(new_edge)
        print(f"Manual edge added: {p1.type} - {p2.type}")
    def save(self):
        return [e.save() for e in self.manual_edges]
    def load(self, edges_data, parts):
        for d in edges_data:
            for p1 in parts:
                if p1.type == d["p1_idx"]:
                    for p2 in parts:
                        if p2.type == d["p2_idx"]:
                            v1_idx = d["v1_idx"]
                            v2_idx = d["v2_idx"]
                            new_edge = Edge(p1, p2, v1_idx, v2_idx)
                            self.manual_edges.append(new_edge)