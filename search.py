from urllib.request import urlopen
import json
import osmnx as ox
import pwaqi as pw
import pandas as pd
import networkx as nx
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
def detect_street_network_from_place(place, save = True, filename = 'icts2000'):
	G = ox.graph_from_place(query = place, infrastructure = 'way["highway"]', network_type = 'drive', simplify = True)
	G_projected = ox.project_graph(G)
	highways_to_keep = ['motorway', 'trunk', 'primary']
	H = nx.MultiDiGraph()
	for u,v,attr in G.edges(data=True):
	    if attr['highway'] in highways_to_keep:
	        H.add_edge(u,v,attr_dict=attr)
	        H.node[u].update(G.node[u])
	        H.node[v].update(G.node[v])
	H.graph = G.graph
	H_projected = ox.project_graph(H)
	fig, ax = ox.plot_graph(H_projected, show = False, save = save, filename = filename, file_format='svg')
	ox.save_graphml(H, filename = filename + '.graphml')
	return H
	return G

@timer
def detect_street_network_from_point(lat = 13.14633, lon = 77.514386, distance = 2000, save = True, filename = 'icts2000'):
	G = ox.graph_from_point((lat, lon), distance = distance, infrastructure = 'way["highway"]',\
		network_type = 'drive', simplify = False)
	highways_to_keep = ['motorway', 'trunk', 'primary']
	H = nx.MultiDiGraph()
	for u,v,attr in G.edges(data=True):
	    if attr['highway'] in highways_to_keep:
	        H.add_edge(u,v,attr_dict=attr)
	        H.node[u].update(G.node[u])
	        H.node[v].update(G.node[v])
	H.graph = G.graph
	H_projected = ox.project_graph(H)
	fig, ax = ox.plot_graph(H_projected, show = False, save = save, filename = filename, file_format='svg')
	ox.save_graphml(H, filename = filename + '.graphml')
	return H

#print(get_city_pollution_data('Bangalore', folder = 'data/'))
detect_street_network_from_point(13.0339, 77.51321111, filename = 'icts-2000')
#detect_street_network_from_place('Bangalore, India', filename = 'Bangalore')