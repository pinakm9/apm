from urllib.request import urlopen
import json
import osmnx as ox
import utm
import aqicn as aq
import pwaqi as pw

def collect_weather_data(lat, lon):
	api_key = 'fd27039e71beb2089a3fc8114db42d6b'
	site = 'https://api.openweathermap.org/data/2.5/weather?'
	url = '{}lat={}&lon={}&appid={}'.format(site,lat,lon,api_key)
	response = urlopen(url)
	return json.loads(response.read().decode())

data = collect_weather_data(13,77)
print(data['wind'])

api = aq.AqicnApi('09f4aebf96d26720c88d48f23293f18a6e912eb4')
class Point:
	def __init__(self,pt):
		x, y = pt
		self.lat = x
		self.lng = y

#print(api.get_location_feed(Point([12,77])))
print(pw.get_location_observation(13,77, '09f4aebf96d26720c88d48f23293f18a6e912eb4'))
print(pw.findStationCodesByCity('Beijing', '09f4aebf96d26720c88d48f23293f18a6e912eb4'))
