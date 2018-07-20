from time import time
import numpy as np

def timer(func):
	def new_func(*args,**kwargs):
		start = time()
		val = func(*args,**kwargs)
		end = time()
		print('Time taken by function {} is {} seconds'.format(func.__name__, end-start))
		return val
	return new_func

def str2num(arr):
	nums = []
	for s in arr:
		nums.append(float(s))
	return nums


def read_gq(file):
	weights, points = [], []
	with open(file, 'r') as gq:
		for line in gq:
			w, x = str2num(line.split()[1:])
			weights.append(w)
			points.append(x)
	return weights, points

def set_grid(point, size, step):
	x, y = point
	X = np.arange(x-size/2.0, x+size/2.0, step)
	Y = np.arange(y-size/2.0, y+size/2.0, step)
	return np.meshgrid(X, Y)

def C(x, y, z, Q = 1, u = 5, K = 1, H = 0):
	if x <= 0:
		return 0
	else:
		r = K*x/u
		cz = np.exp(-(z - H)**2/(4*r)) + np.exp(-(z + H)**2/(4*r))
		cy = np.exp(-y**2/(4*r))
		return Q*cy*cz/(4*u*r*np.sqrt(np.pi))

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

"""