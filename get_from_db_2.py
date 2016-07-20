#import shapefile
import oemof.db as db
from shapely import geometry as geopy
from oemof.db import coastdat
import pandas as pd
import numpy as np
import geoplot
import matplotlib.pyplot as plt
import array
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

# geometrie = shapefile.Reader('~/temp/deutschland.shp')
year = 2010
conn = db.connection()
germany = fetch_geometries(**germany)
germany['geom'] = geoplot.postgis2shapely(germany.geom)
# print(germany)
#print(germany['geom'])
geom = geopy.Polygon([(12.2, 52.2), (12.2, 51.6), (13.2, 51.6), (13.2, 52.2)])
multi_weather = coastdat.get_weather(conn, geom, year)
my_weather = multi_weather[0]
print(my_weather.geometry)
# print(my_weather.data)
print(len(multi_weather), "-> number of weather objects")
vector_coll = {}

# Collecting calm vectors in dictionary
# For loop to find the longest calms per weather object

for i in range(len(multi_weather)):

    # print(multi_weather[i].data['v_wind'])

    calm, = np.where(multi_weather[i].data['v_wind'] < 3)
    vector_coll = np.split(calm, np.where(np.diff(calm) != 1)[0] + 1)
    vc = vector_coll
    calm = len(max(vc, key=len))
    calm_list = np.matrix(calm)
    multi_weather[i].geometry
    #print(calm_list)

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

germany = fetch_geometries(**germany)
germany['geom'] = geoplot.postgis2shapely(germany.geom)

#print(geom)
#print(coastdat_de['geom'])

# random example polygons
#geom_2 = geopy.Polygon([(14.2, 52.2), (14.2, 51.6), (15.2, 51.6), (15.2, 52.2)])
#geom_3 = geopy.Polygon([(16.2, 52.2), (16.2, 51.6), (17.2, 51.6), (17.2, 52.2)])
#geom_4 = geopy.Polygon([(14.2, 53.4), (14.2, 52.8), (15.2, 52.8), (15.2, 53.4)])
#geom_5 = geopy.Polygon([(12.2, 53.4), (12.2, 52.8), (13.2, 52.8), (13.2, 53.4)])

# data_example = {geom: 130, geom_2: 2}

#data_example = [500, 1, 1, 1, 1]
example = geoplot.GeoPlotter(coastdat_de['geom'], (3, 16, 47, 56),
                             data=np.random.rand(792))
#data2 = np.random.rand(792)
#print(data2)
#example = geoplot.GeoPlotter([geom], (3, 20, 47, 60),
                             #data=data_example)
example.cmapname = 'winter'
example.cmapname = 'winter'
example.plot(facecolor='#badd69', edgecolor='')

# example.geometries = germany['geom']
example.data = None
example.plot(facecolor='', edgecolor='white', linewidth=2)

plt.tight_layout()
plt.box(on=None)
plt.show()

