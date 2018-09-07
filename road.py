from utility import *
import numpy as np 
import osmnx as ox
import matplotlib.pyplot as plt
import utm
import scipy.integrate as integrate


class LinearStreet:

	def __init__(self, start, end):
		self.a = end[0] - start[0]
		self.b = end[1] - start[1]
		self.x0, self.y0 = start
		self.x1, self.y1 = end

	def effect(self, f, point):
		x, y, z = point
		f1 = lambda t: f(x-self.x0-self.a*t, y-self.y0-self.b*t, z)
		return np.sqrt(self.a**2+self.b**2)*integrate.quad(f1,0,1)[0]

	def length(self):
		return np.sqrt((self.x0-self.x1)**2+(self.y0-self.y1)**2)


	def modify(self, rotation):
		c, s = np.cos(rotation), np.sin(rotation)
		R = np.array([[c, s],[-s, c]])
		self.x0, self.y0 = np.dot(R, [self.x0, self.y0])
		self.x1, self.y1 = np.dot(R, [self.x1, self.y1])
		self.a = self.x1 - self.x0
		self.b = self.y1 - self.y0

class StreetNetwork:

	def __init__(self, file, origin = [0, 0], rotation = 0):
		self.network = ox.load_graphml(file)
		self.detect_network_segments(origin, rotation)
		self.rot = rotation

	def detect_network_segments(self, origin = [0, 0], rotation = 0):
		self.segments = []
		c, s = np.cos(rotation), np.sin(rotation)
		self.R = np.array([[c, s],[-s, c]])
		origin = np.array(origin)
		for edge in self.network.edges:
			start = np.array(utm.from_latlon(self.network.node[edge[0]]['y'], self.network.node[edge[0]]['x'])[:2])-origin
			end = np.array(utm.from_latlon(self.network.node[edge[1]]['y'], self.network.node[edge[1]]['x'])[:2])-origin
			self.segments.append(LinearStreet(np.dot(self.R, start), np.dot(self.R, end)))
		return self.segments


	def modify_segments(self, rotation = 0):
		c, s = np.cos(rotation), np.sin(rotation)
		self.R = np.array([[c, s],[-s, c]])
		print(self.R)
		for segment in self.segments:
			segment.modify(rotation)


	def effect(self, f, point, form = 'latlon'):
		if form == 'latlon':
			pt = list(np.dot(self.R, list(utm.from_latlon(*point[:2])[:2])))
		else:
			pt = list(np.dot(self.R, point))
		print('point', pt)
		if len(point) < 3:
			pt.append(0)
		else:
			pt.append(point[2])
		s = 0
		for line in self.segments:
			s += line.effect(f, pt)
		print(s)
		return s

class CircularStreet:
	
	def __init__(self, center, radius, resolution = 1e-3, show = False):
		self.center = center
		self.radius = radius
		self.resolution = resolution
		t = np.arange(np.pi/2, 3*np.pi/2, resolution)
		x, y = radius*np.cos(t) + center[0], radius*np.sin(t) + center[1]
		self.points = list(zip(x,y))
		self.segments = []
		lt = len(t)
		for i in range(lt):
			if i < lt - 1:
				self.segments.append(LinearStreet(self.points[i], self.points[i+1]))
			else:
				self.segments.append(LinearStreet(self.points[i], self.points[0]))
		if show is True:
			plt.scatter(x, y)
			plt.show()



	def effect(self, f, point):
		s = 0
		for line in self.segments:
			s += line.effect(f, point)
		return s

#S = StreetNetwork('peenya-6000.graphml', rotation = 0, origin = utm.from_latlon(*[13.0339, 77.51321111][:2])[:2])
#print(S.effect(C_g, (12,77)))