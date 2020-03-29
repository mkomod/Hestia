import requests
import time
from collections import deque

import geopandas as gpd
from shapely.geometry import Point, Polygon

import matplotlib.pyplot as plt
import numpy as np

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
lonLat = []
polygons = []

for i,neigh in enumerate(neighbourhoods):
    print(i)
    id_ = neigh[0]
    
    #check_quota_limit()
    requestBoundary = requests.get(f'https://data.police.uk/api/{force}/{id_}/boundary').json()
    requestBoundary = [(float(i['latitude']), float(i['longitude'])) for i in requestBoundary]
    
    lonLat.append(requestBoundary)
    polygons.append( Polygon(requestBoundary) )

polygons = gpd.GeoSeries(polygons)
geoDf = gpd.GeoDataFrame({'name':[n[1] for n in neighbourhoods], 'geometry':polygons})

nCrimes = []
date = '2018-01'

for i, lonsLats in enumerate(lonLat):
    print(i)
    boundaryForAPI = ''
    for lat, lon in lonsLats:
        boundaryForAPI += str(lat) +','+str(lon) +':'
    boundaryForAPI = boundaryForAPI[:-1]
    
    rek = requests.post('https://data.police.uk/api/crimes-street/all-crime?', data = {'poly':boundaryForAPI, 'date':date})
    if rek.ok:
        crimes = rek.json()
        nCrimes.append(len(crimes))
        
    else:
        nCrimes.append(np.nan)
        

geoDf[date] = nCrimes

fig, ax = plt.subplots(1, 1)
geoDf.plot(column = date, ax = ax, legend = True)

