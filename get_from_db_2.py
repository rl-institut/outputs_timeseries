#import shapefile
import oemof.db as db
from shapely import geometry as geopy
from oemof.db import coastdat
import pandas as pd
import numpy as np
import geoplot
import matplotlib.pyplot as plt
plt.style.use('ggplot')


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

# multiweather prompt
germany = {
    'table': 'deu3_21',
    'geo_col': 'geom',
    'id_col': 'region_id',
    'schema': 'deutschland',
    'simp_tolerance': '0.01',
    'where_col': 'region_id',
    'where_cond': '> 0',
    }

#geometrie = shapefile.Reader("~/temp/deutschland.shp")
year = 2010
conn = db.connection()
germany = fetch_geometries(**germany)
germany['geom'] = geoplot.postgis2shapely(germany.geom)
#print(germany)
#print(germany['geom'])
geom = geopy.Polygon([(12.2, 52.2), (12.2, 51.6), (13.2, 51.6), (13.2, 52.2)])
multi_weather = coastdat.get_weather(conn, geom, year)
my_weather = multi_weather[0]

#print(my_weather.geometry)
#print(my_weather.data)

#print(len(multi_weather), "-> number of weather objects")
#print((multi_weather), "multi_weather")
vector_coll = {}
calm_list = []

# Collecting calm vectors in dictionary
# For loop to find the longest calms per weather object

for i in range(len(multi_weather)):

    #print(multi_weather[i].data['v_wind'])

    calm, = np.where(multi_weather[i].data['v_wind'] < 3)
    vector_coll = np.split(calm, np.where(np.diff(calm) != 1)[0] + 1)
    vc = vector_coll
    calm = len(max(vc, key=len))
#    multi_weather[i].geometry
    calm_list = np.append(calm_list, calm)

# print(calm_list)

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

example = geoplot.GeoPlotter(coastdat_de['geom'], (3, 16, 47, 56),
                             data=np.random.rand(792))

#example = geoplot.GeoPlotter([geom], (3, 20, 47, 60),
                             #data=data_example)
example.cmapname = 'winter'
example.cmapname = 'winter'
example.plot(facecolor='#badd69', edgecolor='')

#example.geometries = germany['geom'] -> Netzregionen
example.data = None
example.plot(facecolor='', edgecolor='white', linewidth=2)

# Build Dataframe including the calms and the geometry
x = coastdat_de['geom']
df = pd.DataFrame(data = calm_list, columns = ['calms'])
df2 = pd.DataFrame(data = x, columns = ['geom'])

df3 = pd.concat([df, df2], axis = 1)
print(df3)

plt.tight_layout()
plt.box(on=None)
#plt.show()

