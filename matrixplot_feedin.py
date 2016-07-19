from shapely import geometry as geopy

from oemof import db
from oemof.db import coastdat
from feedinlib import powerplants as plants
import numpy as np
import matplotlib.pyplot as plt

year = 2007


location = {
    'tz': 'Europe/Osnabrück',
    'latitude': 52.279,
    'longitude': 8.043
    }

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
installed_capacity=0.5)
pv_feedin = advent_module.feedin(weather=my_weather, peak_power=0.5)

# Reshape data into matrix
matrix_wind = []
total_power = wind_feedin + pv_feedin
matrix_wind = np.reshape(total_power, (365, 24))
a = np.transpose(matrix_wind)
b = np.flipud(a)
fig, ax = plt.subplots()


#print(b)
#print(pv_feedin)
#print(wind_feedin)


# Plot image
plt.imshow(b, cmap='afmhot', interpolation='nearest',
     origin='lower', aspect='auto', vmax=0.05)

plt.title('Osnabrück {0} Wind and PV feedin(nominal power <5 %)'.format(year))
ax.set_xlabel('days of year')
ax.set_ylabel('hours of day')
clb = plt.colorbar()
clb.set_label('P_Wind + P_PV')
plt.show()

