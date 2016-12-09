from shapely import geometry as geopy

from oemof import db
from oemof.db import coastdat
from feedinlib import powerplants as plants
import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import matplotlib
year = 2000


location = {
    'tz': 'Europe/Parchim',
    'latitude': 50.99787380076216,
    'longitude': 13.71091247271507
    }

#geolocator = Nominatim()
#location_geo = geolocator.reverse("53.41, 11.84")
#print(location_geo.address)

# Specific tion of the weather data set CoastDat2
coastDat2 = {
    'dhi': 0,
    'dirhi': 0,
    'pressure': 0,
    'temp_air': 2,
    'v_wind': 10,
    'Z0': 0}

# Specification of the wind turbines
enerconE126 = {
    'h_hub': 135,
    'd_rotor': 127,
    'wind_conv_type': 'ENERCON E 126 7500',
    'data_height': coastDat2}

# Specification of the pv module
advent210 = {
    'module_name': 'Advent_Solar_Ventura_210___2008_',
    'azimuth': 180,
    'tilt': 30,
    'albedo': 0.2}

conn = db.connection()
my_weather = coastdat.get_weather(
    conn, geopy.Point(location['longitude'], location['latitude']),
year)

# Location control
print(location['latitude'])
print(location['longitude'])

# Definition of the power plants
E126_power_plant = plants.WindPowerPlant(**enerconE126)
advent_module = plants.Photovoltaic(**advent210)
wind_feedin = E126_power_plant.feedin(weather=my_weather,
installed_capacity=1)
pv_feedin = advent_module.feedin(weather=my_weather, peak_power=1)



# Find all calms a < x and put it into the dictionary

vector_coll = {}
calm_list = []
calm, = np.where(pv_feedin < 0.05)
vector_coll = np.split(calm, np.where(np.diff(calm) != 1)[0] + 1)
vc = vector_coll
calm = len(max(vc, key=len))
print(calm)

#    calm_list = np.append(calm_list, calm)

# Reshape data into matrix
matrix_wind = []
#total_power = wind_feedin + pv_feedin
matrix_wind = np.reshape(pv_feedin, (366, 24))
a = np.transpose(matrix_wind)
b = np.flipud(a)
fig, ax = plt.subplots()

# Plot image
plt.imshow(b, cmap='afmhot', interpolation='nearest',
     origin='lower', aspect='auto', vmax=0.05)

plt.title('Parchim, MV, Ger 2007 PV feedin (nominal power <5 %)longest calm {0} hours'.format(calm))
ax.set_xlabel('days of year')
ax.set_ylabel('hours of day')
clb = plt.colorbar()
clb.set_label('P_Wind')
#matplotlib.figure.Figure.text('test')
plt.show()

