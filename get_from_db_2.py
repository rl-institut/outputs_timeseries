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
year = 2014
conn = db.connection()
germany = fetch_geometries(**germany)
germany['geom'] = geoplot.postgis2shapely(germany.geom)
#print(germany)
#print(germany['geom'])
#geom = geopy.Polygon([(12.2, 52.2), (12.2, 51.6), (13.2, 51.6), (13.2, 52.2)])

c = fiona.open('C:/temp/germany_and_offshore.shp')
pol = c.next()
geom = shape(pol['geometry'])

multi_weather = coastdat.get_weather(conn, geom, year)
my_weather = multi_weather[0]


#print(my_weather.geometry)
#print(my_weather.data)

#print(len(multi_weather), "-> number of weather objects")

print((multi_weather), "multi_weather")
vector_coll = {}
calm_list = []

# Collecting calm vectors in dictionary
# For loop to find the longest calms per weather object

print('calculating calms...')
for i in range(len(multi_weather)):

    calm, = np.where(multi_weather[i].data['v_wind'] < 3)
    vector_coll = np.split(calm, np.where(np.diff(calm) != 1)[0] + 1)
    vc = vector_coll
    calm = len(max(vc, key=len))

#    multi_weather[i].geometry
    calm_list = np.append(calm_list, calm)
    calm_list2 = np.log(calm_list) / np.log(calm_list.max(axis=0))
    calm_list3 = np.sort(calm_list)
#np.save(calm_list, calm_list)
#print(calm_list3)
x = np.amax(calm_list)
y = np.amin(calm_list)
print()
print('-> longest calm:', x, 'hours')
print('-> shortest calm:', y, 'hours')
print()

plt.hist(calm_list3, normed=False, range=(calm_list3.min(),
     calm_list3.max()), log=True)
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
print()


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
example.draw_legend(legendlabel="Length of wind calms < 3 m/s in h",
                     extend='neither', tick_list=[1, 10, 100, 1000,
                     np.amax(calm_list)])

example.basemap.drawcountries(color='white', linewidth=2)
example.basemap.shadedrelief()
plt.tight_layout()
plt.box(on=None)
plt.show()

