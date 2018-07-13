from utility import *
import numpy as np 
import osmnx as ox
import matplotlib.pyplot as plt
import utm
import scipy.integrate as integrate

G = ox.load_graphml('icts2000.graphml')

class LineWay:

	def __init__(self, start, end):
		self.start, self.end = np.array(start), np.array(end)
		self.a = end[0] - start[0]
		self.b = end[1] - start[1]
		self.x0, self.y0 = start
		self.x1, self.y1 = end

	def contrib(self, f, x, y, z):
		f1 = lambda t: f(x-self.x0-self.a*t, y-self.y0-self.b*t, z)
		return integrate.quad(f1,0,1)[0]

	def length(self):
		return np.linalg.norm(self.start - self.end)

def set_grid(point, size, step):
	x, y = point
	X = np.arange(x-size/2.0, x+size/2.0, step)
	Y = np.arange(y-size/2.0, y+size/2.0, step)
	return np.meshgrid(X, Y)

@timer
def detect_street_network_from_point(lat = 13.14633, lon = 77.514386, distance = 2000, filename = 'icts2000'):
	G = ox.graph_from_point((lat, lon), distance = distance, network_type = 'drive_service', simplify = False)
	G_projected = ox.project_graph(G)
	fig, ax = ox.plot_graph(G_projected, show = False, save = True, filename = filename, file_format='svg')
	ox.save_graphml(G, filename = filename + '.graphml')
	return G

@timer
def detect_network_segments(network, origin = [0, 0], rotation = 0):
	segments = []
	c, s = np.cos(rotation), np.sin(rotation)
	R = np.array([[c, s],[-s, c]])
	origin = np.array(origin)
	for edge in network.edges:
		start = np.array(utm.from_latlon(network.node[edge[0]]['y'], network.node[edge[0]]['x'])[:2])-origin
		end = np.array(utm.from_latlon(network.node[edge[1]]['y'], network.node[edge[1]]['x'])[:2])-origin
		segments.append(LineWay(np.dot(R, start), np.dot(R, end)))
	return segments

def total_contrib(segments, f, x, y, z):
	s = 0
	for line in segments:
		s += line.contrib(f, x, y, z)
	return s

def C(x, y, z, Q = 1, u = 5, K = 1.5):
	if x <= 0:
		return 0
	else:
		r = K*x/u
		rr = np.sqrt(r)
		cy = np.exp(-y**2/(4*r))
		return Q*cy/(2*u*rr*np.sqrt(np.pi))


origin = np.array(utm.from_latlon(13.14633, 77.514386)[:2])
segments = detect_network_segments(G, origin, np.pi/4)
grid = set_grid([0, 0], 1000, 10)
c = np.vectorize(lambda x, y: total_contrib(segments, C, x, y, 0))

@timer
def draw_contour(f, meshgrid, imgId):
	x, y  = meshgrid
	z = f(x, y)
	plt.figure()
	cp = plt.contourf(x, y, z)
	plt.colorbar(cp)
	plt.contour(x, y, z)
	plt.savefig('images/Concentration contour{}.png'.format(imgId))
	plt.axes().set_aspect('equal', 'datalim')
	plt.show()

"""
lw = segments[200]
print(np.linalg.norm(lw.start - np.array([x,y])))
print(lw.contrib(C,lw.x0+1,lw.y0+1,0))
for l in segments:
	print(l.length())"""
draw_contour(c, grid, 11)