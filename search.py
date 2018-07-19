from urllib.request import urlopen
from utility import *
import json, utm
import osmnx as ox
from shapely import geometry
@timer
def collect_weather_data(lat, lon):
	api_key = 'fd27039e71beb2089a3fc8114db42d6b'
	site = 'https://api.openweathermap.org/data/2.5/weather?'
	url = '{}lat={}&lon={}&appid={}'.format(site,lat,lon,api_key)
	response = urlopen(url)
	return json.loads(response.read().decode())



import fiona
from shapely.geometry import shape
sh = fiona.open("../data/shapes/cb_2017_15_place_500k.shp")
first = sh.next()
poly = shape(first['geometry'])
#poly = geometry.Polygon(list(map(lambda z: utm.to_latlon(*z, 32, 'U'), first['geometry']['coordinates'] )))
#print(first['geometry']['coordinates'])

x, y = poly.exterior.coords.xy
z = list(zip(x,y))
print(z)

p = geometry.Polygon([(-159.51359300000001, 22.204227), (-159.510039, 22.202855),\
 (-159.505236, 22.202593), (-159.513883, 22.203910999999998), (-159.51359300000001, 22.204227)])

G = ox.graph_from_polygon(p, network_type = 'drive')
ox.plot_graph(G)