from time import time
import numpy as np
import scipy.special as sp
import mpmath as mp

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


def C_g(x, y, z, Q = 1, u = 5.1, K = 0.5, H = 0):
	if x <= 0:
		return 0
	else:
		r = K*x/u
		cy = np.exp(-y**2/(4*r))
		return Q*cy/(2*u*r*np.sqrt(np.pi))

def ermak(x, y, z, Q = 1, u = 5, K = 1, H = 0, w_dep = 0.13e-2, w_set = 0.02e-2):
	if x <= 0:
		return 0
	else:
		r, w_o = K*x/u, w_dep - 0.5*w_set 
		a = 2*w_o*np.sqrt(np.pi)/K
		rr = np.sqrt(r)
		cz = mp.exp(-(z - H)**2/(4*r)) + mp.exp(-(z + H)**2/(4*r))\
		 - a*rr*np.exp(w_o*(z+H)/K + r*(w_o/K)**2)*sp.erfc((z+H)/(2*rr)+w_o*rr/K)
		cxz = np.exp(-w_set*(z-H)/(2*K)-r*(w_set/(2*K))**2)
		cy = np.exp(-y**2/(4*r))
		return Q*cxz*cy*cz/(4*u*r*np.sqrt(np.pi))

def ermak_g(x, y, z, Q = 1, u = 5.1, K = 1, w_dep = 0.13e-2, w_set = 0.02e-2):
	if x <= 0:
		return 0
	else:
		r, w_o = K*x/u, w_dep - 0.5*w_set 
		a = 2*w_o*np.sqrt(np.pi)/K
		rr = np.sqrt(r)
		cz = 2 - a*rr*np.exp(r*(w_o/K)**2)*sp.erfc(w_o*rr/K)
		cxz = np.exp(-r*(w_set/(2*K))**2)
		cy = np.exp(-y**2/(4*r))
		return Q*cxz*cy*cz/(4*u*r*np.sqrt(np.pi))


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
#print(ermak(1,1,0))