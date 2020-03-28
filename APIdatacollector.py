import requests
import time
from collections import deque

import geopandas as gpd
from shapely.geometry import Point, Polygon

import matplotlib.pyplot as plt

time_limit = .999
calls_limit = 15
log = deque([time.time() - time_limit - 60,], maxlen = calls_limit)

def check_quota_limit():
    if log[0] >= time.time() - time_limit:
        time.sleep(log[0]+time_limit-time.time()+.0001)
    log.append(time.time())

force = 'metropolitan'
request = requests.get(f'https://data.police.uk/api/{force}/neighbourhoods')


neighbourhoods = [list(id_name.values()) for id_name in request.json()]
polygons = []

for i,neigh in enumerate(neighbourhoods):
    print(i)
    id_ = neigh[0]
    
    #check_quota_limit()
    requestBoundary = requests.get(f'https://data.police.uk/api/{force}/{id_}/boundary').json()
    
    requestBoundary = [(float(i['latitude']), float(i['longitude'])) for i in requestBoundary]
    
    polygons.append( Polygon(requestBoundary) )

polygons = gpd.GeoSeries(polygons)
geoDf = gpd.GeoDataFrame({'name':[n[1] for n in neighbourhoods], 'geometry':polygons})

fig, ax = plt.subplots(1, 1)
geoDf.plot(column = 'name', ax = ax, legend = True)

