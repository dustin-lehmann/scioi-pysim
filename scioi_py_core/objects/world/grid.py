import numpy as np

from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.core.spaces import Space2D
from scioi_py_core.core.world import WorldObject, World
import scioi_py_core.core as core


class GridCell(WorldObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Grid:
    size: float = None
    origin = None



class GridCell2D(WorldObject):
    static = True
    x: int
    y: int
    pos_x: float
    pos_y: float
    cell_size: float
    object_type = 'grid_cell_2d'
    height = 0.01

    def __init__(self, world: World, x: int, y: int, pos_x: float, pos_y: float, cell_size: float, *args, **kwargs):

        super().__init__(world=world, space=Space2D(), *args, **kwargs)
        self.x = x
        self.y = y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.cell_size = cell_size

        self.physics = core.physics.CuboidPhysics(size_x=cell_size, size_y=cell_size, size_z=self.height,
                                                  position=[pos_x, pos_y, -self.height / 2], orientation=np.eye(3))
        self.collision.settings.collidable = False

        self.configuration['pos']['x'] = pos_x
        self.configuration['pos']['y'] = pos_y
        self.configuration['psi'] = 0

    # This should not be part of the GridCell but part of the visualization of the grid cell. I have to split these into cell, object and visualization of the object
    def highlight(self, state: bool = True, color = None):
        self.visualization.sample_flag = True
        self.visualization.sample['highlight'] = {}
        self.visualization.sample['highlight']['state'] = state
        if color is not None:
            self.visualization.sample['highlight']['color'] = color
        else:
            self.visualization.sample['highlight']['color'] = [1,0,0]

    def _getParameters(self):
        params = super()._getParameters()
        params['size'] = {
            'x': self.cell_size,
            'y': self.cell_size,
        }
        params['visible'] = True
        return params


class Grid2D(Grid):
    cell_size: float
    cells_x: int
    cells_y: int
    cells: list

    def __init__(self, world:World, cell_size: float, cells_x: int, cells_y: int, origin: list):

        # Check if the grid for x and y are either both lists or both integers
        assert(isinstance(cells_x, int) and isinstance(cells_y, int))

        self.cells_x = cells_x
        self.cells_y = cells_y
        self.cell_size = cell_size


        self.cells = [[None for x in range(cells_x)] for y in range(cells_y)]
        self.origin = origin

        pos_0_x = -cell_size * cells_x / 2 + cell_size / 2 - origin[0]
        pos_0_y = - cell_size * cells_y / 2 + cell_size / 2 - origin[1]

        for x in range(0, cells_x):
            for y in range(0, cells_y):
                    pos_x = pos_0_x + x * cell_size
                    pos_y = pos_0_y + y * cell_size
                    self.cells[x][y] = GridCell2D(world, x, y, pos_x, pos_y, cell_size)

    def getCell(self, x = None, y = None, pos_x = None, pos_y = None) -> GridCell2D:
        assert((x is not None and y is not None) or (pos_x is not None and pos_y is not None))

        if x is not None and y is not None:
            if 0 <= x < self.cells_x and 0 <= y < self.cells_y:
                return self.cells[x][y]
            else:
                return None
        else:
            cell_x = int((pos_x - self.origin[0] + self.cell_size * self.cells_x / 2) / self.cell_size)
            cell_y = int((pos_y - self.origin[1] + self.cell_size * self.cells_y / 2) / self.cell_size)

            if cell_x < 0 or cell_x >= self.cells_x or cell_y < 0 or cell_y >= self.cells_y:
                return None
            else:
                return self.cells[cell_x][cell_y]

    def getAdjacentCells(self, cell: GridCell2D):
        adjacent_cells = []
        if cell.x > 0:
            adjacent_cells.append(self.cells[cell.x - 1][cell.y])
        if cell.x < self.cells_x - 1:
            adjacent_cells.append(self.cells[cell.x + 1][cell.y])
        if cell.y > 0:
            adjacent_cells.append(self.cells[cell.x][cell.y - 1])
        if cell.y < self.cells_y - 1:
            adjacent_cells.append(self.cells[cell.x][cell.y + 1])
        if cell.x > 0 and cell.y > 0:
            adjacent_cells.append(self.cells[cell.x - 1][cell.y - 1])
        if cell.x < self.cells_x - 1 and cell.y > 0:
            adjacent_cells.append(self.cells[cell.x + 1][cell.y - 1])
        if cell.x > 0 and cell.y < self.cells_y - 1:
            adjacent_cells.append(self.cells[cell.x - 1][cell.y + 1])
        if cell.x < self.cells_x - 1 and cell.y < self.cells_y - 1:
            adjacent_cells.append(self.cells[cell.x + 1][cell.y + 1])
        return adjacent_cells



