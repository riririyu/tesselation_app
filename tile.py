import pygame
import math
import config

TILE_SIZE = config.TILE_SIZE
TILE_COLOR = config.TILE_COLOR
LINE_COLOR = config.LINE_COLOR

class Tile:
    def __init__(self,x,y,size):
        self.rect = pygame.Rect(x,y,size,size)
    def draw(self,screen):
        pygame.draw.rect(screen,TILE_COLOR,self.rect)
        pygame.draw.rect(screen,LINE_COLOR,self.rect,2)
        
class HexTile:
    def __init__(self,center_x, center_y, size):
        self.center = (center_x, center_y)
        self.size = size
        self.points = self.calculate_points()
    
    def calculate_points(self):
        points=[]
        for i in range(6):
            angle_deg = math.radians(60 * i - 30)
            x = self.center[0] + self.size * math.cos(angle_deg)
            y = self.center[1] + self.size * math.sin(angle_deg)
            points.append((x,y))
        return points
    
    def draw(self, screen):
        pygame.draw.polygon(screen, TILE_COLOR, self.points)
        pygame.draw.polygon(screen, LINE_COLOR, self.points, 2)
    def is_clicked(self, pos):
        dist=math.hypot(pos[0]-self.center[0], pos[1]-self.center[1])
        return dist < self.size
    def move(self, dx, dy):
        self.center = (self.center[0]+dx, self.center[1]+dy)
        self.points = self.calculate_points()

    def snap_to_grid(self, other_tile):
        threshold=TILE_SIZE*0.3
        for p1 in self.points:
            for p2 in other_tile.points:
                if math.hypot(p1[0]-p2[0], p1[1]-p2[1]) < threshold:
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    self.move(dx, dy)
                    return True
        return False