import numpy as np 
from shapely import geometry
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from utility import *
import utm
import osmnx as ox #
import road

def find_drop_point(f, drop_ratio, direction, tol = 1e-6, start = 1, max_itr = 50, verbose = False):
	a, b = direction
	dr, t = 1, start 
	fs = f(a*t, b*t)
	if fs == 0:
		return 0, 0
	if verbose == True:
		print('t\tDrop ratio\t\tf({:.2f}t,{:.2f}t)\n{}'.format(a, b, '-'*53))
	while dr > drop_ratio and t - start < max_itr:
		t += 1
		y = f(a*t,b*t)
		dr = y/fs
		if verbose == True:
			print('{}\t{}\t{}'.format(t, dr, y))	
	return t, dr

def direction_from_degree(degree):
	rad = np.pi*degree/180.0
	return np.cos(rad), np.sin(rad)

def rotate_deg(point, angle):
	c, s = direction_from_degree(angle)
	x, y = point
	x1 = c*x - s*y
	y1 = c*y + s*x
	return np.array([x1, y1])


def find_influence_polygon(f, drop_ratio, tol = 1e-6, start = 1, max_itr = 50, origin = (0,0), angle = 0,\
 wind = 5, eddy = 1, plot = False, save_plot = False, filename = None, verbose = False):
	vertices = []
	origin = np.array(origin)
	for deg in range(360):
		a, b = rotate_deg(direction_from_degree(deg), -angle)
		t = find_drop_point(f, drop_ratio, (-a,-b), tol, start, max_itr, verbose)[0]
		vertices.append(rotate_deg([a*t, b*t], angle) + origin)
	vertices.append(vertices[0])
	poly = geometry.Polygon(vertices)
	if plot is True:
		fig = plt.figure()
		ax = plt.axes()
		ax.set_aspect('equal')
		ax.add_patch(PolygonPatch(poly, alpha = 1.0, color = 'deeppink', zorder = 0))
		ax.scatter(origin[0], origin[1], color = 'navy')
		x = [v[0] for v in vertices]
		y = [v[1] for v in vertices]
		mx, my = min(x), min(y)
		Mx, My = max(x), max(y)
		plt.xlim(mx-1, Mx+1)
		plt.ylim(my-1, My+1)
		plt.text(0,0,'wind speed = {}'.format(wind)+' $ms^{-1}$\n' +\
			'wind angle = {} deg\neddy-diffusivity = {}'.format(angle, eddy) +\
			' $m^2s^{-1}$', transform = fig.transFigure)
		if save_plot is True:
			plt.savefig(filename)
		plt.show()
	return poly

def find_influence_circle(f, drop_ratio, start = 1000, step = 1000, max_itr = 200, verbose = False):
	fs = road.CircularStreet((0,0), start).effect(f, (0,0,0))
	dr, t = 1, start
	if verbose == True:
		print('t\tDrop ratio\t\teffect\n{}'.format('-'*53))
	while dr > drop_ratio and t/step < max_itr:
		t += step
		y = road.CircularStreet((0,0), t).effect(f, (0,0,0))
		dr = y/fs
		if verbose == True:
			print('{}\t{}\t{}'.format(t, dr, y))	
	return t, dr

def get_ls_from_angle(angle, R = 1, origin = (0,0), rotation = 0):
		angle *= np.pi/180.0
		half = 0.125*np.pi/180.0
		R /= np.cos(half)
		x, y = origin
		left = rotate_deg([R*np.cos(angle+half)+x, R*np.sin(angle+half)+y], rotation)
		right = rotate_deg([R*np.cos(angle-half)+x, R*np.sin(angle-half)+y], rotation)
		return road.LinearStreet(left, right)

def find_drop_point_ls(f, drop_ratio, angle, point = (0,0,0), start = 1, origin = (0,0), rotation = 0,\
	max_itr = 50, verbose = False):
	dr, t = 1, start
	fs = get_ls_from_angle(angle, t, origin, rotation).effect(f, point) 
	if fs == 0:
		return t, 0
	if verbose == True:
		print('t\tDrop ratio\t\teffect\n{}'.format('-'*53))
	while dr > drop_ratio and t/start < max_itr:
		t += start
		y = get_ls_from_angle(angle, t, origin, rotation).effect(f, point)
		dr = y/fs
		if verbose == True:
			print('{}\t{}\t{}'.format(t, dr, y))
	if t/start == max_itr:
		print('Search for drop point failed at angle {} deg, last drop_ratio = {}'.format(angle, dr))	
	return t, dr


def find_influence_polygon_ls(f, drop_ratio, point = (0,0,0), start = 1, origin = (0,0), rotation = 0, max_itr = 2000,\
 wind = 5.1, eddy = 1, plot = False, save_plot = False, filename = None, verbose = False):
	vertices = []
	for deg in range(360*4):
		deg *= 0.25
		rad = np.pi*deg/180.0
		t = find_drop_point_ls(f, drop_ratio, deg-rotation, point, start, origin, -rotation, max_itr, verbose)[0]
		vertices.append(rotate_deg([t*np.cos(rad)+origin[0], t*np.sin(rad)+origin[1]], rotation))
	vertices.append(vertices[0])
	poly = geometry.Polygon(vertices)
	if plot is True:
		fig = plt.figure()
		ax = plt.axes()
		#ax.set_aspect('equal')
		ax.add_patch(PolygonPatch(poly, alpha = 1.0, color = 'deeppink', zorder = 0))
		ax.scatter(point[0], point[1], color = 'navy')
		x = [v[0] for v in vertices]
		y = [v[1] for v in vertices]
		mx, my = min(x), min(y)
		Mx, My = max(x), max(y)
		plt.xlim(mx-1, Mx+1)
		plt.ylim(my-1, My+1)
		plt.text(0,0,'wind speed = {}'.format(wind)+' $ms^{-1}$\n' +\
			'wind angle = {} deg\neddy-diffusivity = {}'.format(rotation, eddy) +\
			' $m^2s^{-1}$', transform = fig.transFigure)
		if save_plot is True:
			if filename is None:
				filename = 'images/influence_polygon_ls.png'
			plt.savefig(filename)
		plt.show()
	return poly
"""
def influence_polygon_from_lat_lon(point, f, drop_ratio, tol = 1e-6, start = 1, max_itr = 50, angle = 0,\
 plot = False, save_plot = False, filename = None):
	ox, oy, zone, zone_letter = utm.from_latlon(*point)
	poly = find_influence_polygon(f, drop_ratio, tol, start, max_itr, (ox,oy), angle, plot, save_plot, filename)
	x, y = (poly.exterior.coords.xy)
	print(max(x), min(x), max(y), min(y))
	x, y = poly.exterior.coords.xy
	return print(list(map(lambda z: utm.to_latlon(*z, zone, zone_letter), list(zip(x,y)) )))

poly = influence_polygon_from_lat_lon((50,77), lambda x,y: C(x,y,0), 1e-6, angle = 60,  plot = True)
#G = ox.graph_from_polygon(geometry.Polygon([[12, 77], [13,78], [14,77], [13, 77], [12,77]]), network_type = 'all')
G = ox.graph_from_polygon(poly, network_type = 'drive')
ox.plot_graph(G)"""

#print(influence_polygon_from_lat_lon([7,8], lambda x,y: C(x,y,0), 1e-6, start = 100, angle = 60,  plot = True))
#print(find_drop_point(lambda x,y: C(x,y,0, u = 9e-3, K=1e-6), 1e-6, direction_from_degree(78), start = 1, verbose = True))
#find_influence_polygon(lambda x,y: C(x,y,0, u = 5, K=1), 1e-10, start = 300, max_itr = 500, angle = 120,\
#wind = 5, eddy = 1, plot = True, verbose = True, save_plot =True, filename = 'images/influence_polygon.png')
find_influence_polygon_ls(ermak_g, 1e-6, start = 1000, plot = True, rotation = 0, verbose = False, save_plot = True, max_itr = 2000)
#print(find_drop_point_ls(C_g, 1e-6, 180, start =1, verbose = True))
#print(get_ls_from_angle(90))