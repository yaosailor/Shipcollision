#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: base_timetest.py
@time: 2019-11-14 15:31
"""
import pickle
from datetime import datetime, timedelta
import numpy as np
from collections import OrderedDict
from tools import cal_area_id
'''
Organize ship data
    1 Create a variable that take time as keys
    2 Determine which grid the ship is in
    3 Organize ship data
'''
data_ship = OrderedDict()

one_list = []
index = 0
time_format = "%Y-%m-%d %H:%M:%S"
minutes_set = 5

date_start = "2019-10-09 00:00:00"
date_end = "2019-10-24 13:21:16"

timeArray_start = datetime.strptime(date_start, time_format)
timeArray_end = datetime.strptime(date_end, time_format)
timeArray_reference = timeArray_start
while timeArray_reference <= timeArray_end:
    timeArray_reference += timedelta(minutes=minutes_set)
    data_ship[timeArray_reference.strftime(time_format)] = dict()
timeArray_reference += timedelta(minutes=minutes_set)
timeArray_referencemin = timeArray_reference - timedelta(minutes=minutes_set/2)
timeArray_referencemax = timeArray_reference + timedelta(minutes=minutes_set/2)

file = '../output/ship_info.pkl'
with open(file, "rb") as f:
    ship_info = pickle.load(f)
for info in ship_info:
    num = 0
    for index_key in data_ship:
        times = [x.timestamp() for x in ship_info[info]['dt_pos_utc']]
        minus_tem = np.absolute(datetime.strptime(index_key, time_format).timestamp() - np.array(times))
        index = np.argmin(np.absolute(minus_tem))
        if -minutes_set*60 < minus_tem[index] < minutes_set*60:
            num += 1
            lon_tem = ship_info[info]['longitude'][index]
            lat_tem = ship_info[info]['latitude'][index]
            area_id = cal_area_id(lat_tem,lon_tem)
            #
            tem_dict = {'mmsi': info, 'longitude': lon_tem,
                        'latitude': lat_tem,
                        'sog': ship_info[info]['sog'][index],
                        'cog': ship_info[info]['cog'][index]}
            #
            if area_id not in data_ship[index_key]:
                data_ship[index_key][area_id] = []
            data_ship[index_key][area_id].append(tem_dict)

            print(data_ship[index_key][area_id])
srcfile = "ship_area_info_last.pkl"
with open(srcfile, "wb") as f:
    pickle.dump(data_ship, f)
