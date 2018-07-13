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


@timer
def detect_street_network_from_point(lat = 13.14633, lon = 77.514386, distance = 2000, filename = 'icts2000'):
	G = ox.graph_from_point((lat, lon), distance = distance, network_type = 'drive_service', simplify = False)
	G_projected = ox.project_graph(G)
	fig, ax = ox.plot_graph(G_projected, show = False, save = True, filename = filename, file_format='svg')
	ox.save_graphml(G, filename = filename + '.graphml')
	return G


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


def C(x, y, z, Q = 1, u = 5, K = 1.5, H = 0):
	r = K*x/u
	try:
		rr = np.sqrt(r)
	except:
		print(r)
	cz = np.exp(-(z - H)**2/(4*r)) + np.exp(-(z + H)**2/(4*r))
	cy = np.exp(-y**2/(4*r))
	return Q*cy*cz/(4*u*rr*np.sqrt(np.pi))

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
G = detect_street_network_from_point()
for u in G.nodes:
	print(G.node[u])

#detect_street_network_from_point(distance = 2000, filename = 'icts2000')
"""

class LineWay:

	def __init__(self, start, end):
		self.start = start
		self.end  =  end
		self.length = np.norm(start - end)

	def params():
		pass 

def detect_network_segments(network):
	segments = []
	for edge in network.edges:
		start = np.array(network.node[edge[0]]['x'], network.node[edge[0]]['y'])
		end = np.array(network.node[edge[1]]['x'], network.node[edge[1]]['y'])
		lw = LineWay(start, end)
		segments.append(lw)
		print(lw, network[edge[0]][edge[1]]['length'])

detect_network_segments(G)
"""