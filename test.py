import scioi_pysim.core as core
import scioi_pysim.environments.grid.xy as xy

from math import pi

ss = core.spaces.StateSpace(dimensions=[core.spaces.Dimension(name='x'), core.spaces.Dimension(name='y'),
                                        core.spaces.Dimension(name='psi', limits=[0, 2 * pi], wrapping=True)])

state = ss.map([1, 1, -4])



a = 2
