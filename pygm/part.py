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
        
    
    
    def draw(self, screen):
        
        color=pygame.Color(config.TILE_COLOR[self.type])
        for center in self.centers:
            vertices=[]
            for i in range(6):
                angle_deg = math.radians(60 * i - 30)
                x = center[0] + self.size * math.cos(angle_deg)
                y = center[1] + self.size * math.sin(angle_deg)
                vertices.append((x + self.pos[0], y + self.pos[1]))
            pygame.draw.polygon(screen, color, vertices)
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