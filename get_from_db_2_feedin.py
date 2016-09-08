import oemof.db as db
from shapely import geometry as geopy
from oemof.db import coastdat
import pandas as pd
import numpy as np
import geoplot
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from shapely.geometry import shape
import fiona
from oemof import db
from feedinlib import powerplants as plants
import pickle

def fetch_geometries(**kwargs):
    """Reads the geometry and the id of all given tables and writes it to
     the 'geom'-key of each branch of the data tree.
    """
    sql_str = '''
        SELECT {id_col}, ST_AsText(
            ST_SIMPLIFY({geo_col},{simp_tolerance})) geom
        FROM {schema}.{table}
        WHERE "{where_col}" {where_cond}
        ORDER BY {id_col} DESC;'''

    db_string = sql_str.format(**kwargs)
    results = db.connection().execute(db_string)
    cols = results.keys()
    return pd.DataFrame(results.fetchall(), columns=cols)

print('please wait...')

germany = {
    'table': 'deu3_21',
    'geo_col': 'geom',
    'id_col': 'region_id',
    'schema': 'deutschland',
    'simp_tolerance': '0.01',
    'where_col': 'region_id',
    'where_cond': '> 0',
    }

print('collecting weather objects...')
#geometrie = shapefile.Reader("~/temp/deutschland.shp")
year = 2007
conn = db.connection()
germany = fetch_geometries(**germany)
germany['geom'] = geoplot.postgis2shapely(germany.geom)
#print(germany)
#print(germany['geom'])
#geom = geopy.Polygon([(12.2, 52.2), (12.2, 51.6), (13.2, 51.6), (13.2, 52.2)])

c = fiona.open('C:/temp/germany_and_offshore.shp')
pol = c.next()
geom = shape(pol['geometry'])


#use pickle to save or load the weather objects
multi_weather = pickle.load(open('multi_weather_save.p', 'rb'))
#multi_weather = coastdat.get_weather(conn, geom, year)
my_weather = multi_weather[0]

pickle.dump(multi_weather, open('multi_weather_save.p', 'wb'))

##########-------feedinlib Components--------------------------################

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

# Definition of the power plants
E126_power_plant = plants.WindPowerPlant(**enerconE126)
advent_module = plants.Photovoltaic(**advent210)
#wind_feedin = E126_power_plant.feedin(weather=my_weather,
#installed_capacity=1)
#pv_feedin = advent_module.feedin(weather=my_weather, peak_power=1)

########----------------------------------------------------------#############


#print(my_weather.geometry)
#print(my_weather.data)

#print(len(multi_weather), "-> number of weather objects")
#print((multi_weather), "multi_weather")
vector_coll = {}
calm_list = []

# Collecting calm vectors in dictionary
# For loop to find the longest calms per weather object
#print(wind_feedin)
print('calculating calms...')
for i in range(len(multi_weather)):
#    pv_feedin = advent_module.feedin(weather=multi_weather[i], peak_power=1)
    #print(pv_feedin)
    wind_feedin = E126_power_plant.feedin(weather=multi_weather[i],installed_capacity=1)
#    print(wind_feedin)
    calm, = np.where(wind_feedin < 0.05)
#    print(len(calm))
    vector_coll = np.split(calm, np.where(np.diff(calm) != 1)[0] + 1)
    vc = vector_coll
    calm = len(max(vc, key=len))
#    print(vc)
#    print(calm)

#    multi_weather[i].geometry
    calm_list = np.append(calm_list, calm)
    calm_list2 = (calm_list) / (calm_list.max(axis=0))
    calm_list3 = np.sort(calm_list)
    print('done_' + str(i))
#np.save(calm_list, calm_list)
print(calm_list)
x = np.amax(calm_list)
y = np.amin(calm_list)
print()
print('-> longest calm:', x, 'hours')
print('-> shortest calm:', y, 'hours')
print()

plt.hist(calm_list3, normed=False, range=(calm_list.min(),
     calm_list3.max())) #log=True)
plt.xlabel('length of calms in hours')
plt.ylabel('number of calms')
plt.title('calm histogram Germany{0}'.format(year))
plt.show()

#print(multi_weather.data)

# Germany dena_18 regions (ZNES)

coastdat_de = {
    'table': 'de_grid',
    'geo_col': 'geom',
    'id_col': 'gid',
    'schema': 'coastdat',
    'simp_tolerance': '0.01',
    'where_col': 'gid',
    'where_cond': '> 0'
    }
germany = {
    'table': 'deu3_21',
    'geo_col': 'geom',
    'id_col': 'region_id',
    'schema': 'deutschland',
    'simp_tolerance': '0.01',
    'where_col': 'region_id',
    'where_cond': '> 0',
    }


coastdat_de = fetch_geometries(**coastdat_de)
coastdat_de['geom'] = geoplot.postgis2shapely(coastdat_de.geom)
#print((coastdat_de), "coastdat")
germany = fetch_geometries(**germany)
germany['geom'] = geoplot.postgis2shapely(germany.geom)

#print(geom)
#print(coastdat_de['geom'])

# Build Dataframe including the calms and the geometry
print('building Dataframe...')
print()

x = coastdat_de['geom']
df = pd.DataFrame(data=calm_list2, columns=['calms'])
df2 = pd.DataFrame(data=x, columns=['geom'])
df3 = pd.concat([df, df2], axis=1)
#print(df3)
df4 = df3.loc[df3['calms'] == 1]
coordinate = df4['geom']
print('longest calm located in:')
print(coordinate)
#print()

######-----------------Point analysis----------------------------------########

conn = db.connection()
my_weather = coastdat.get_weather(
    conn, geopy.point(df3['geom'], year))


# Reshape data into matrix
matrix_wind = []
#total_power = wind_feedin + pv_feedin
matrix_wind = np.reshape(wind_feedin, (365, 24))
a = np.transpose(matrix_wind)
b = np.flipud(a)
fig, ax = plt.subplots()

# Plot image
plt.imshow(b, cmap='afmhot', interpolation='nearest',
     origin='lower', aspect='auto', vmax=0.1)

plt.title('Osnabrück {0} Wind and PV feedin(nominal power <5 %)'.format(year))
ax.set_xlabel('days of year')
ax.set_ylabel('hours of day')
clb = plt.colorbar()
clb.set_label('P_Wind + P_PV')
plt.show()

#######---------------------------------------------------------------#########





example = geoplot.GeoPlotter(df3['geom'], (3, 16, 47, 56),
                                data=df3['calms'])

example.cmapname = 'inferno'
#example.cmapname = 'winter'
#example.plot(facecolor='OrRd', edgecolor='')

#example.geometries = germany['geom'] -> Netzregionen
#example.data = None
example.plot(edgecolor='black', linewidth=1, alpha=1)

print('creating plot...')
plt.title('Longest calms Germany {0}'.format(year))
example.draw_legend(legendlabel="Length of wind calms < 5 % P_nenn in h",
                     extend='neither',tick_list=[0, np.amax(calm_list) *0.25,
                          np.amax(calm_list) *0.5, np.amax(calm_list) *0.75,
                           np.amax(calm_list)])

example.basemap.drawcountries(color='white', linewidth=2)
example.basemap.shadedrelief()
plt.tight_layout()
plt.box(on=None)
plt.show()

