from scioi_py_core.objects.world.grid import Grid2D

def main():
    grid = Grid2D(cell_size=1, cells_x=5, cells_y=5, origin=[0,0])
    cell = grid.getCell(pos_x=0, pos_y=0)
    acells = grid.getAdjacentCells(cell)
    print(cell)

if __name__ == '__main__':
    main()