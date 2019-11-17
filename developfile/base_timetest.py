#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: base_timetest.py
@time: 2019-11-14 15:31
"""
import pickle
from datetime import datetime, timedelta
import time
import numpy as np
from collections import OrderedDict
from tools import cal_area_id, time2minutes
'''
Organize ship data
    1 Create a variable that take time as keys
    2 Determine which grid the ship is in
    3 Organize ship data
'''

def old_method(inputfile):
    date_ship = OrderedDict()
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
        date_ship[timeArray_reference.strftime(time_format)] = dict()
        timeArray_reference += timedelta(minutes=minutes_set)
    timeArray_reference += timedelta(minutes=minutes_set)
    with open(inputfile, "rb") as f:
        ship_info = pickle.load(f)
    for info in ship_info:
        num = 0
        for index_key in date_ship:
            times = [x.timestamp() for x in ship_info[info]['dt_pos_utc']]
            minus_tem = np.absolute(datetime.strptime(index_key, time_format).timestamp() - np.array(times))
            index = np.argmin(np.absolute(minus_tem))
            if -minutes_set*60 < minus_tem[index] < minutes_set*60:
                num += 1
                lon_tem = ship_info[info]['longitude'][index]
                lat_tem = ship_info[info]['latitude'][index]
                area_id = cal_area_id(lat_tem, lon_tem)
                if area_id is None:
                    break
                tem_dict = {'mmsi': info, 'longitude': lon_tem,
                            'latitude': lat_tem,
                            'sog': ship_info[info]['sog'][index],
                            'cog': ship_info[info]['cog'][index]}

                if area_id not in date_ship[index_key]:
                    date_ship[index_key][area_id] = []
                date_ship[index_key][area_id].append(tem_dict)
    return date_ship

def time_array(inputfile, date_start, date_end):
    start = time.clock()
    date_ship = OrderedDict()
    time_format = "%Y-%m-%d %H:%M:%S"
    minutes_set = 5
    # create the dict of time str
    timeArray_start = datetime.strptime(date_start, time_format)
    timeArray_end = datetime.strptime(date_end, time_format)
    timeArray_reference = timeArray_start
    while timeArray_reference <= timeArray_end:
        date_ship[timeArray_reference.strftime(time_format)] = dict()
        timeArray_reference += timedelta(minutes=minutes_set)
    # read the data of ships
    with open(inputfile, "rb") as f:
        ship_info = pickle.load(f)
    num = 0
    # screen the time of ship
    for info_mmsi in ship_info:
        total_ship = OrderedDict()
        delta_set = 60 * minutes_set
        for index_ii in range(0, len(ship_info[info_mmsi]['dt_pos_utc'])):
            ii = ship_info[info_mmsi]['dt_pos_utc'][index_ii]
            afminset, residue_time = time2minutes(ii)
            afminset = afminset.strftime(time_format)
            if afminset not in total_ship:
                total_ship[afminset] = [ii, residue_time, index_ii]
            elif afminset in total_ship:
                if residue_time < total_ship[afminset][1]:
                    total_ship[afminset] = [ii, residue_time, index_ii]
        num += 1
        solo_ship_index = []
        for time_key in total_ship:
            tys_index = total_ship[time_key][2]
            # print(tys_index,total_ship[time_key][0])
            # time_key, index_ii,
            # area_id judge each available information
            lat_tem = ship_info[info_mmsi]['latitude'][tys_index]
            lon_tem = ship_info[info_mmsi]['longitude'][tys_index]
            area_id = cal_area_id(lat_tem, lon_tem)
            if area_id is None:
                break
            tem_dict = {'mmsi': info_mmsi, 'longitude': lon_tem,
                        'latitude': lat_tem,
                        'sog': ship_info[info_mmsi]['sog'][tys_index],
                        'cog': ship_info[info_mmsi]['cog'][tys_index]}
            if area_id not in date_ship[time_key]:
                date_ship[time_key][area_id] = []
            date_ship[time_key][area_id].append(tem_dict)
    end = time.clock()
    print('Running time:', (end - start))
    return date_ship
        # extract the data


if __name__ == '__main__':
    inputfile = '../output/ship_info.pkl'
    date_start = "2019-10-09 00:00:00"
    date_end = "2019-10-24 13:21:16"
    # date_ship = old_method(inputfile,)
    date_ship = time_array(inputfile, date_start, date_end)
    srcfile = "ship_area_info_new.pkl"
    with open(srcfile, "wb") as f:
        pickle.dump(date_ship, f)
