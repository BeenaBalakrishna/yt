import yt
import numpy as np
from yt.visualization.volume_rendering.api import PointSource
from yt.units import kpc

np.random.seed(1234567)

ds = yt.load('IsolatedGalaxy/galaxy0030/galaxy0030')

im, sc = yt.volume_render(ds)

npoints = 1000
vertices = np.random.random([npoints, 3])*200*kpc
colors = np.random.random([npoints, 4])
colors[:, 3] = 1.0

points = PointSource(vertices, colors=colors)
sc.add_source(points)

sc.camera.width = 300*kpc

sc.save()
