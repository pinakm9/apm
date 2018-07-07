import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np 
#city = ox.gdf_from_place('Berkeley, California')
#ox.plot_shape(ox.project_gdf(city))
#plt.show()
from svgpathtools import svg2paths
"""
G = ox.graph_from_point((13.14633, 77.514386), distance= 2000, network_type='drive')
G_projected = ox.project_graph(G)
fig, ax = ox.plot_graph(G_projected, show=False, save=True, 
                           filename='icts2000', file_format='svg')
"""



def arange(path, n = 200):
	return	[path.point(i/float(n-1)) for i in range(n)]

paths, attributes = svg2paths('images/icts2000.svg')
z = []
for p in paths:
	z.append(arange(p))


for segment in z:
	plt.scatter([t.real for t in segment], [t.imag for t in segment], s = 0.01)
plt.axes().set_aspect('equal', 'datalim')
plt.show()