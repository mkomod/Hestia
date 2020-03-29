import requests
import time
from collections import deque
import json

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

polLines = open('data/pols.json').read().splitlines()


def makeBoundary(polLine):
    boundary = ''
    
    points = polLine.split('}')[:-1]
    
    for point_ in points:
        lat, lon = [i.split(':')[-1][1:-1] for i in point_.split(',')[-2:]]
        boundary += lat + ',' + lon + ':'
        
    boundary = boundary[:-1]
    
    return boundary

dates = ['20'+yy+'-'+mm for yy in ['17','18','19','20'] for mm in ['01','02','03','04','05','06','07','08','09','10','11','12']][2:-10]

def summaryStats(crimes):
    return len(crimes)

def getCrimeData(date, boundary):
    check_quota_limit()
    rek = requests.post('https://data.police.uk/api/crimes-street/all-crime?', data = {'poly':boundary, 'date':date})
    if rek.ok:
        crimes = rek.json()
        return summaryStats(crimes)
    else:
        return rek.reason
    
getCrimeData = np.vectorize(getCrimeData)

crimeData = np.zeros((len(polLines), len(dates)))

for i, polLine_ in enumerate(polLines):
    print(i/len(polLines)*100)
    crimeData[i] = getCrimeData( dates, makeBoundary(polLine_) )

np.savetxt('crimeData.csv', crimeData, delimiter=',', fmt='%d')













