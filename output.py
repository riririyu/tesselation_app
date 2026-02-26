import ezdxf

def create_puzzle_tiles(filename,rows,cols,tile_size):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for r in range(rows):
        for c in range(cols):
            x = c * tile_size
            y = r * tile_size

            points=[
                (x, y),
                (x + tile_size, y),
                (x + tile_size, y + tile_size),
                (x, y + tile_size),
                (x,y)
            ]
            msp.add_lwpolyline(points)
    
    doc.saveas(filename)

if __name__ == "__main__":
    create_puzzle_tiles("puzzle.dxf", 5, 5, 10)