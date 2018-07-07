import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np 
#city = ox.gdf_from_place('Berkeley, California')
#ox.plot_shape(ox.project_gdf(city))
#plt.show()
from svgpathtools import svg2paths
import scipy.integrate as integrate

"""
G = ox.graph_from_point((13.14633, 77.514386), distance= 2000, network_type='drive')
G_projected = ox.project_graph(G)
fig, ax = ox.plot_graph(G_projected, show=False, save=True, 
                           filename='icts2000', file_format='svg')
"""


class Point
	
	def __init__(self, loc):
		self.loc = loc
 	
 	def set_nbr(left, right):
 		self.left = left
 		self.right = right
 		self.len = abs(left - right)

 	def contrib(self, f):
 		return lambda x, y: f(x-self.loc.re, y-self.loc.imag)


def arange(path, n = 100):
	return	[path.point(i/float(n-1)) for i in range(n)]

def pieces(path, n = 100):
	points = arange(path, n)
	pts, last = [], len(points)
	for i, p in enumerate(points):
		pt = Point(p)
		if i == 0:
			pt.set_nbr(p, (p+points[i+1])/2)
		else i == last - 1:
			pt.set_nbr((p+points[i-1])/2, p)
		elif:
			pt.set_nbr((p+points[i-1])/2, (p+points[i+1])/2)
		pts.append(pt)
	return pts

def contrib(f, x, y, pts):
	s = 0
	for pt in pts:
		s += pt.contrib(f)(x, y)
	return s

def left(pt, pts):
	points = []
	for p in points:
		if p.re < pt.re:
			points.append(p)
	return points


def parametrize(path):
	if path.__class__.__name__ == 'Line':
		s, e = path.start, path.end
		f = lambda p, q, t: p + t*(q-p)
		return lambda t: f(s.real, e.real, t), lambda t: f(s.imag, e.imag, t)
	elif path.__class__.__name__ == 'CubicBezier':
		s, c1, c2, e = path.start, path.control1, path.control2, path.end
		f = lambda a, b, c, d, t: (1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t**2*c + t**3*d
		return lambda t: f(s.real, c1.real, c2.real, e.real, t),\
			   lambda t: f(s.imag, c1.imag, c2.imag, e.imag, t)
	else:
		print('Error42: {}'.format(path.__class__.__name__))


def segment_integrate(f, curve, a = 0, b = 1):
	x, y = curve
	return integrate.quad(lambda t: f(x(t), y(t)), a, b)[0]

def path_integrate(f, paths):
	s = 0
	for path in paths:
		for segment in path:
			curve = parametrize(segment)
			s += segment_integrate(f, curve)
	return s

def C(x, y, z, Q = 1, u = 5, K = 1.5, H = 0):
	r = K*x/u
	try:
		rr = np.sqrt(r)
	except:
		print(r)
	cz = np.exp(-(z - H)**2/(4*r)) + np.exp(-(z + H)**2/(4*r))
	cy = np.exp(-y**2/(4*r))
	return Q*cy*cz/(4*u*rr*np.sqrt(np.pi))

paths, attributes = svg2paths('images/icts2000.svg')
z = []
for path in paths:
	for segment in path: 
		z.append(arange(segment))











"""for segment in z:
	plt.scatter([t.real for t in segment], [t.imag for t in segment], s = 0.01)
plt.axes().set_aspect('equal', 'datalim')
plt.show()


x = np.arange(0.1, 5, 0.1)
y = np.arange(-5, 5, 0.1)
x, y  = np.meshgrid(x, y)
z = c(x, y, 0, paths)
plt.figure()
cp = plt.contourf(x, y, z)
plt.colorbar(cp)
plt.contour(x, y, z)

plt.show()"""