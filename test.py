import matplotlib.pyplot as plt
import geopandas as gpd
import pysal as ps
from pysal.contrib.viz import mapping as maps

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world.plot()
print(gpd.datasets.available)