from urllib.request import urlopen
import json
import osmnx as ox
import pwaqi as pw
import pandas as pd
from utility import *

@timer
def collect_weather_data(lat, lon):
	api_key = 'fd27039e71beb2089a3fc8114db42d6b'
	site = 'https://api.openweathermap.org/data/2.5/weather?'
	url = '{}lat={}&lon={}&appid={}'.format(site,lat,lon,api_key)
	response = urlopen(url)
	return json.loads(response.read().decode())

#data = collect_weather_data(13,77)
#print(data['wind'])

@timer
def collect_station_pollution_data(station_id, token = '09f4aebf96d26720c88d48f23293f18a6e912eb4'):
	print('Collecting pollution data for station {} ...'.format(station_id))
	return pw.get_station_observation(station_id, token)

@timer
def collect_city_pollution_data(city, token = '09f4aebf96d26720c88d48f23293f18a6e912eb4', max_attempts = 4):
	print('Collecting pollution data for {} ...'.format(city))
	stations = pw.findStationCodesByCity(city, token)
	data = {}
	for station in stations:
		data.update({station : {}})
	attempt = 0
	while attempt < max_attempts and {} in data.values():
		for station in stations:
			data[station] = collect_station_pollution_data(station, token)
		attempt += 1
	return data

def process_station_pollution_data(data):
	for item in data['iaqi']:
		data.update({item['p'] : item['v']})
	data.pop('iaqi', None)
	return data

def process_city_pollution_data(data):
	dicts = []
	for key in data.keys():
		dicts.append(process_station_pollution_data(data[key]))
	new_d = {}
	keys = set()
	for d in dicts:
		keys = keys.union(d.keys())
	for key in keys:
		new_d[key] = [item[key] if key in item.keys() else 'nan' for item in dicts]	
	return new_d

@timer
def get_city_pollution_data(city, token = '09f4aebf96d26720c88d48f23293f18a6e912eb4', max_attempts = 10,\
 save = True, folder = '', filename = ''):
	data = process_city_pollution_data(collect_city_pollution_data(city, token, max_attempts))
	if save is True:
		if filename is '':
			filename = folder + city
		pd.DataFrame(data).to_csv(filename + '.csv', index = False)
	return data

@timer
def detect_drive_network_from_place(place, save = True, filename = 'icts2000'):
	G = ox.graph_from_place(query = place, network_type = 'drive', simplify = False)
	hwy_types = ['primary', 'motorway', 'trunk']
	gdf = ox.graph_to_gdfs(G, nodes=False)
	mask = ~gdf['highway'].map(lambda x: isinstance(x, str) and x in hwy_types)
	edges = zip(gdf[mask]['u'], gdf[mask]['v'], gdf[mask]['key'])
	G.remove_edges_from(edges)
	G = ox.remove_isolated_nodes(G)
	G_projected = ox.project_graph(G)
	fig, ax = ox.plot_graph(G_projected, show = False, save = save, filename = filename, file_format='svg')
	ox.save_graphml(G, filename = filename + '.graphml')
	return G

@timer
def detect_drive_network_from_point(lat = 13.14633, lon = 77.514386, distance = 2000, save = True, filename = 'icts2000'):
	G = ox.graph_from_point((lat, lon), distance = distance, network_type = 'drive', simplify = False)
	hwy_types = ['primary', 'motorway', 'trunk']
	gdf = ox.graph_to_gdfs(G, nodes=False)
	mask = ~gdf['highway'].map(lambda x: isinstance(x, str) and x in hwy_types)
	edges = zip(gdf[mask]['u'], gdf[mask]['v'], gdf[mask]['key'])
	G.remove_edges_from(edges)
	G = ox.remove_isolated_nodes(G)
	G_projected = ox.project_graph(G)
	filename += '-' + str(distance)
	fig, ax = ox.plot_graph(G_projected, show = False, save = save, filename = filename, file_format='svg')
	ox.save_graphml(G, filename = filename + '.graphml')
	return G

#print(get_city_pollution_data('Bangalore', folder = 'data/'))
#detect_drive_network_from_point(13.0339, 77.51321111, 4000, filename = 'peenya')
detect_drive_network_from_place('Bangalore, India', filename = 'Bangalore')