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

def set_ermak_and_street_25(poll_file, station_id, wind_file, street_file, folder = 'data/', correction = 0.1):
	loc, pm25, deg, speed = read_data_25(poll_file, station_id, wind_file, folder)
	street = road.StreetNetwork('peenya-6000.graphml', origin = utm.from_latlon(*loc)[:2], rotation = deg)
	error = lambda p: (street.effect(lambda x, y, z: ermak_g(x, y, z, Q = p[0], u = speed,\
	 K = p[1], w_dep = p[2], w_set = p[3]), (0, 0, 0)) - correction*pm25)**2
	return error 

@timer
def fit_25(poll_file, station_id, wind_file, street_file, folder = 'data/'):
	f = set_ermak_and_street_25(poll_file, station_id, wind_file, folder)
	bnds = ((1e4,1e7), (0.25,1.3), (1e-3, 2e-3), (1e-5,1e-3))
	return minimize(f, (1e5, 1, 1.3e-3, 2e-4) , bounds = bnds, tol = 1e-10, method = 'TNC')

print(fit_25('Bangalore-2018-07-23 08:00:00-pollution.csv', 3758,\
	'Bangalore-2018-07-23 08:16:31.365250-weather.csv', 'btm-6000.graphml'))