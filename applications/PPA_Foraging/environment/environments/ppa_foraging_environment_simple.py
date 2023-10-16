from applications.PPA_Foraging.environment.ppa_foraging_environment import EnvironmentBase
from scioi_py_core.objects.world import floor


class EnvironmentSimple(EnvironmentBase):
    world_size = [2, 2]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.world.setSize(x=[-self.world_size[0]/2, self.world_size[0]/2], y=[-self.world_size[1]/2, self.world_size[1]/2])
        # floor.generateTileFloor(self.world, tile_size=0.5)
