import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np 
#city = ox.gdf_from_place('Berkeley, California')
#ox.plot_shape(ox.project_gdf(city))
#plt.show()
from svgpathtools import svg2paths
import scipy.integrate as integrate
from utility import *
"""
G = ox.graph_from_point((13.14633, 77.514386), distance= 2000, network_type='drive')
G_projected = ox.project_graph(G)
fig, ax = ox.plot_graph(G_projected, show=False, save=True, 
                           filename='icts2000', file_format='svg')
"""
class Point:
	
	def __init__(self, loc):
		self.loc = loc
		self.real = loc.real
		self.imag = loc.imag
 	
	def set_nbr(self, left, right):
 		self.left = left
 		self.right = right
 		self.len = abs(left - right)

	def contrib(self, f):
 		return lambda x, y: f(x-self.loc.real, y-self.loc.imag)


def arange(path, n = 100):
	return	[path.point(i/float(n-1)) for i in range(n)]

def pieces(path, n = 100):
	points = arange(path, n)
	pts, last = [], len(points)
	for i, p in enumerate(points):
		pt = Point(p)
		if i == 0:
			pt.set_nbr(p, (p+points[i+1])/2)
		elif i == last - 1:
			pt.set_nbr((p+points[i-1])/2, p)
		else:
			pt.set_nbr((p+points[i-1])/2, (p+points[i+1])/2)
		pts.append(pt)
	return pts

def contrib(f, x, y, pts):
	s = 0
	for pt in pts:
		s += pt.contrib(f)(x, y)*pt.len
	return s

def left(pt, pts):
	points = []
	for p in pts:
		if p.real < pt.real:
			points.append(p)
	return points

def ccontrib(x, y, z, f, paths):
	points = []
	for path in paths:
		points += pieces(path)
	pts = left(complex(x, y), points)
	return contrib(f, x, y, pts)


"""paths, attributes = svg2paths('images/icts2000.svg')
z = []
for path in paths:
	for segment in path: 
		z += arange(segment)

re = [p.real for p in z]
im = [p.imag for p in z]
#print(min(re), max(re), min(im), max(im))

c = np.vectorize(lambda a, b: ccontrib(a, b, 0, lambda x,y: C(x, y, 0), paths))
for segment in z:
	plt.scatter([t.real for t in segment], [t.imag for t in segment], s = 0.01)
plt.axes().set_aspect('equal', 'datalim')
plt.show()

@timer
def draw_contour(xl, xr, yl, yr, h = 0.1):
	x = np.arange(xl, xr, h)
	y = np.arange(yl, yr, h)
	x, y  = np.meshgrid(x, y)
	z = c(x, y)
	plt.figure()
	cp = plt.contourf(x, y, z)
	plt.colorbar(cp)
	plt.contour(x, y, z)
	plt.savefig('images/Concentration contour.png')
	plt.axes().set_aspect('equal', 'datalim')
	plt.show()

draw_contour(205,235,205,235,0.3)
"""
G = ox.load_graphml('icts1500.graphml')
for u in G.edges():
	print(G[u[0]][u[1]])

@timer
def detect_bld_network_from_point(lat = 13.14633, lon = 77.514386, distance = 2000, filename = 'icts2000'):
	G = ox.buildings.buildings_from_point((lat, lon), distance = distance)
	for n in G.geometry:
		print(n)
	return G

detect_bld_network_from_point()