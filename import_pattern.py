import pygame
import json
import math
import numpy as np
import config


def draw_panels(screen, data,scale):
    num_panel=len(data["panels"])
    for i,(panel_name, panel_data) in enumerate(data["panels"].items()):
        offset_x=(i+1)*config.SCREEN_SIZE[0]/(num_panel+1)
        offset_y=0.25*config.SCREEN_SIZE[1]
        offset= np.array([offset_x, offset_y])
        
        generate_panel_lines(screen, panel_data,offset,scale)


def generate_panel_lines(screen, panel_data,offset,scale):
    vertices=panel_data["vertices"]
    edges=panel_data["edges"]
    for edge in edges:
        points=[]
        start_idx,end_idx=edge["endpoints"]
        start=np.array([vertices[start_idx][0], vertices[start_idx][1]])
        end=np.array([vertices[end_idx][0], vertices[end_idx][1]])
        if edge.get("curvature"):
            curvature=edge["curvature"]
            if curvature["type"]=="cubic" and "params" in curvature:
                cps=[]
                for p in curvature["params"]:
                    cps.append(control_to_abs_coord(start,end,p))
                for t in np.linspace(0,1,20):
                    point=get_cubic_baezier_point(start,cps[0],cps[1],end,t)
                    points.append(point)
            elif curvature["type"]=="circle" and "params" in curvature:
                radius=curvature["params"][0]
                large_arc=curvature["params"][1]
                direction=curvature["params"][2]
                arc_points=calculate_arc_points(start,end,radius,large_arc,direction,20)
                points.extend(arc_points)
            
            elif curvature["type"]=="quadratic" and "params" in curvature:
                for p in curvature["params"]:
                    cp=control_to_abs_coord(start,end,p)
                for t in np.linspace(0,1,20):
                    point=get_quadratic_baezier_point(start,cp,end,t)
                    points.append(point)
        else:
            points.append(start)
            points.append(end)
        
        intger_points=[(int(p[0]*scale+offset[0]), int(p[1]*scale+offset[1])) for p in points]
        
        pygame.draw.lines(screen,(0,0,0),False,intger_points,2)

def unify_edge_data(panel_data):
    for panel_name, panel in panel_data.items():
        edges = panel["edges"]
        unified_edges = []
        for edge in edges:
            if isinstance(edge, tuple):
                # タプル型の場合、辞書型に変換
                unified_edge = {
                    "endpoints": edge,
                    "curvature": None,  # 直線の場合は None に設定
                }
                unified_edges.append(unified_edge)
            elif isinstance(edge, dict):
                unified_edges.append(edge)
            else:
                raise ValueError(f"Invalid edge data in panel {panel_name}: {edge}")
        panel["edges"] = unified_edges


def get_cubic_baezier_point(p0,p1,p2,p3,t)->np.array:
    x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
    y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
    return np.array([x, y])

def get_quadratic_baezier_point(p0,p1,p2,t)->np.array:
    x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
    return np.array([x, y])


def control_to_abs_coord(start, end, control_scale):
    control_scale[1]*=-1
    edge_vector = end - start
    edge_length = np.linalg.norm(edge_vector)
    edge_vector_normalized = edge_vector/edge_length
    edge_vector_T = [edge_vector[1], -edge_vector[0]]
    edge_vector_T_normalized = edge_vector_T/np.linalg.norm(edge_vector_T)
    control_point = (
        start
        + (control_scale[0] * edge_length) * edge_vector_normalized
        + control_scale[1] * edge_vector_T_normalized * edge_length
    )
    return control_point

def calculate_arc_points(start, end, radius, direction, large_arc, num_points):
    x1, y1 = start[0], start[1]
    x2, y2 = end[0], end[1]

    dx2 = (x1 - x2) / 2.0
    dy2 = (y1 - y2) / 2.0
    dx2,dy2 =(start-end)

    rx = abs(radius)
    ry = abs(radius)
    Prx = rx**2
    Pry = ry**2
    Px = dx2**2
    Py = dy2**2

    radii_check = Px / Prx + Py / Pry
    if radii_check > 1:
        rx = ry = math.sqrt(radii_check) * radius
        Prx = rx**2
        Pry = ry**2

    sign = -1 if direction == large_arc else 1
    sq = max(0, (Prx * Pry - Prx * Py - Pry * Px) / (Prx * Py + Pry * Px))
    coef = sign * math.sqrt(sq)
    cx1 = coef * ((rx * dy2) / ry)
    cy1 = coef * (-(ry * dx2) / rx)

    cx = (x1 + x2) / 2.0 + cx1
    cy = (y1 + y2) / 2.0 + cy1

    start_angle = math.atan2((y1 - cy) / ry, (x1 - cx) / rx)
    end_angle = math.atan2((y2 - cy) / ry, (x2 - cx) / rx)

    delta_angle = end_angle - start_angle
    if direction == 0 and delta_angle > 0:
        delta_angle -= 2 * math.pi
    elif direction == 1 and delta_angle < 0:
        delta_angle += 2 * math.pi

    if not large_arc and abs(delta_angle) > math.pi:
        delta_angle = (
            delta_angle - 2 * math.pi if delta_angle > 0 else delta_angle + 2 * math.pi
        )
    elif large_arc and abs(delta_angle) < math.pi:
        delta_angle = (
            delta_angle + 2 * math.pi if delta_angle > 0 else delta_angle - 2 * math.pi
        )

    arc_points = []
    for i in range(num_points + 1):
        t = i / num_points
        angle = start_angle + t * delta_angle
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        arc_points.append(np.array([x, y]))

    return arc_points