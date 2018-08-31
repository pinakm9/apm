from utility import *
from scipy.optimize import minimize
import pandas as pd
import road
import json
import utm

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

def set_ermak_and_street_no2(poll_file, station_id, wind_file, street_file='', folder = 'data/', correction =0.22):
	loc, no2, deg, speed = read_data_no2(poll_file, station_id, wind_file, folder)
	street = road.StreetNetwork('peenya-100000.graphml', origin = utm.from_latlon(*loc)[:2], rotation = deg)
	error = lambda p: (street.effect(lambda x, y, z: ermak_g_no2(x, y, z, Q = p[0], u = speed,\
	 K = p[1]), (0, 0, 0)) - correction*no2)**2
	return error 

@timer
def fit_no2(poll_file, station_id, wind_file, street_file='', folder = 'data/'):
	f = set_ermak_and_street_no2(poll_file, station_id, wind_file, folder)
	bnds = ((1,1e7), (0.1,2))
	return minimize(f, (1, 1) , bounds = bnds, tol = 1e-12, method = 'TNC')

print(fit_no2('Bangalore-2018-07-23 08:00:00-pollution.csv', 3758,\
	'Bangalore-2018-07-23 08:16:31.365250-weather.csv'))