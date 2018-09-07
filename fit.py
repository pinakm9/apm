from utility import *
from scipy.optimize import minimize, least_squares, curve_fit
import pandas as pd
import road
import json
import utm
#from lmfit import minimize, Parameters

def read_data_25(poll_file, station_id, wind_file, folder = 'data/'):
	poll = pd.read_csv(folder + poll_file)
	poll = poll[poll.idx == station_id]
	pm25, city = poll.pm25.tolist()[0], poll.city.tolist()[0]
	city = json.loads(city.replace("'", "\""))
	wind = pd.read_csv(folder + wind_file)
	return  city['geo'], pm25, 270 - wind.deg[0], wind.speed[0]

def set_ermak_and_street_25(poll_file, station_id, wind_file, street_file, folder = 'data/', correction = 0.5):
	loc, pm25, deg, speed = read_data_25(poll_file, station_id, wind_file, folder)
	street = road.StreetNetwork('peenya-6000.graphml', origin = utm.from_latlon(*loc)[:2], rotation = deg)
	error = lambda p: (street.effect(lambda x, y, z: ermak_g(x, y, z, Q = p[0], u = speed,\
	 K = p[1], w_dep = p[2], w_set = p[3]), (0, 0, 0)) - correction*pm25)**2
	return error 

@timer
def fit_25(poll_file, station_id, wind_file, street_file, folder = 'data/'):
	f = set_ermak_and_street_25(poll_file, station_id, wind_file, folder)
	bnds = ((1e4,1e7), (0.25,1.3), (1e-3, 2e-3), (1e-5,1e-3))
	return minimize(f, (1e5, 1, 1.3e-3, 2e-4) , bounds = bnds, tol = 1e-12, method = 'TNC')

def read_data_no2(poll_file, station_id, wind_file, folder = 'data/'):
	poll = pd.read_csv(folder + poll_file)
	poll = poll[poll.idx == station_id]
	no2, city = poll.no2.tolist()[0], poll.city.tolist()[0]
	city = json.loads(city.replace("'", "\""))
	wind = pd.read_csv(folder + wind_file)
	return  city['geo'], no2, 270 - wind.deg[0], wind.speed[0]

def set_ermak_and_street_no2(poll_file, station_id, wind_file, street_file, folder = 'data/', correction = 0.22):
	loc, no2, deg, speed = read_data_no2(poll_file, station_id, wind_file, folder)
	loc = list(map(lambda x: float(x), loc))
	street = road.StreetNetwork('Bangalore.graphml', rotation = deg)
	error = lambda p: (street.effect(lambda x, y, z: ermak_g_no2(x, y, z, Q = p[0], u = speed,\
	 K = p[1]), loc) - correction*no2)**2
	return error 

@timer
def fit_no2_one(poll_file, station_id, wind_file, street_file='', folder = 'data/'):
	f = set_ermak_and_street_no2(poll_file, station_id, wind_file, folder)
	bnds = ((1,1e7), (0.001,2))
	return minimize(f, (1, 0.5) , bounds = bnds, tol = 1e-12, method = 'TNC')

@timer
def fit_curve_no2(poll_file, station_ids, wind_file, road_file, folder = 'data/'):
	lats, lons, no2s,locs = [], [], [], []
	for station_id in station_ids:
		loc, no2, deg, speed = read_data_no2(poll_file, station_id, wind_file, folder)
		lats.append(loc[0])
		lons.append(loc[1])
		no2s.append(no2)
		locs.append(loc)
	print(locs, no2s)
	street = road.StreetNetwork(road_file, rotation = deg)
	c = np.vectorize(lambda l, Q, K: street.effect(lambda x, y, z: ermak_g_no2(x, y, 0, Q, speed, K), locs[l]))
	popt, pcov = curve_fit(c, [0,1,2], no2s, p0=(1e5,1), bounds = ((1,0.1), (1e7,1.3))) 
	print(popt, pcov)
	print(no2s - c([0,1,2], *popt))
	residuals = np.linalg.norm(no2s - c([0,1,2], *popt))
	print('residuals--->', residuals)

@timer
def fit_ls_no2(files, station_id, road_file, folder = 'data/'):
	no2s, winds = [], []
	for pair in files:
		poll_file, wind_file = pair
		loc, no2, deg, speed = read_data_no2(poll_file, station_id, wind_file, folder)
		no2s.append(no2)
		winds.append([deg, speed])	
	loc = list(map(lambda s: float(s), loc))
	street = road.StreetNetwork('peenya-8000.graphml', origin = list(utm.from_latlon(*loc[:2])[:2]), rotation = 0)
	
	def f(i, Q, K):
		x = winds[i]
		print('hola', x)
		street.modify_segments(rotation = x[0]) 
		return street.effect(lambda x1, y1, z: ermak_g_no2(x1, y1, 0, Q, x[1], K), [0, 0], form = 'Cartesian')
	f = np.vectorize(f)
	index = [0,1, 2]
	popt, pcov = curve_fit(f, index, no2s, p0=(0.6,0.6), bounds = ((0.1,0.1), (1e7,1.3)), method = 'dogbox') 

	print(no2s - f(index, *popt))
	residuals = np.linalg.norm(no2s - f(index, *popt))
	print('residuals--->', residuals, popt, pcov)


@timer
def fit_horizontal_no2(files, station_id, road_file, folder = 'data/'):
	funcs = []
	for pair in files:
		poll, wind = pair
		funcs.append(set_ermak_and_street_no2(poll, station_id, wind, folder))
	f = lambda p: sum([func(p) for func in funcs])
	bnds = ((1,1e7), (0.1,1.4))
	return minimize(f, (100, 0.56) , bounds = bnds, tol = 1e-10)

def collect_ls_data(files, station_id = 3758):
	data = []
	for pair in files:
		poll, wind  = pair
		data.append(read_data_no2(poll, station_id, wind)[:3])
	return np.array(data)

ls_files = [('Bangalore-2018-07-23 08:00:00-pollution.csv','Bangalore-2018-07-23 08:16:31.365250-weather.csv'),\
			('Bangalore-2018-09-02 08:00:00-pollution.csv','Bangalore-2018-09-02 08:49:17.649399-weather.csv'),\
			('Bangalore-2018-09-02 16:00:00-pollution.csv','Bangalore-2018-09-02 16:58:09.138156-weather.csv'),\
			('Bangalore-2018-09-03 07:00:00-pollution.csv','Bangalore-2018-09-03 07:34:55.941468-weather.csv'),\
			('Bangalore-2018-09-05 07:00:00-pollution.csv','Bangalore-2018-09-05 07:44:17.453659-weather.csv')]

print(fit_horizontal_no2(ls_files, 8190 , 'Bangalore.graphml'))