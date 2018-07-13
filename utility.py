from time import time

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
"""