#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: main_cal.py
@time: 2019-11-17 13:44
"""
import pickle
import json
import numpy as np
import time
from datetime import datetime
from shapely.geometry.polygon import Polygon
from ship_domain import wangdomain
from tools import get_distance_hav
from setting import study_area

def process_shipll(s_length, s_width):
    if isinstance(s_length, str):
        s_length = float(s_length)
    if isinstance(s_width, str):
        s_width = float(s_width)
    if s_length != 0. and s_width != 0.:
        rat = s_length / s_width
        if rat < 2.2 or rat > 9.3:
            s_length = 65
            s_width = 11
    elif s_length == 0 or s_width == 0:
        s_length = 65
        s_width = 11
    else:
        pass
    return s_length, s_width

def position_relationship(own_domain, tar_domain):
    p1 = Polygon(own_domain)
    p2 = Polygon(tar_domain)
    p1.intersects(p2)
    if p1.intersects(p2):
        return True
    else:
        return False


def determine_computing_area(area_belong_ID, length_line):
    area = area_data[area_belong_ID]
    ID_need = []
    left_lat = area_data[area_belong_ID]["Left"]["lat"]
    left_lon = area_data[area_belong_ID]["Left"]["lon"]
    if area["Flag"] == 3:
        id_1 = area_belong_ID
        id_2 = area_belong_ID + 1
        id_3 = area_belong_ID + length_line - 1
        id_4 = area_belong_ID + length_line
        id_5 = area_belong_ID + length_line + 1
        ID_need = [id_1, id_2, id_3, id_4, id_5]
    elif area["Flag"] == 2:
        if left_lon == min(longitude):  # find 2.1 situation
            id_1 = area_belong_ID
            id_2 = area_belong_ID + 1
            id_3 = area_belong_ID + length_line
            id_4 = area_belong_ID + length_line + 1
            ID_need = [id_1, id_2, id_3, id_4]
        elif left_lon == max(longitude):  # find 2.2 situation
            id_1 = area_belong_ID
            id_2 = area_belong_ID + length_line
            id_3 = area_belong_ID + length_line - 1
            ID_need = [id_1, id_2, id_3]

        elif left_lat == max(latitude):  # find 1.3 situation
            id_1 = area_belong_ID
            id_2 = area_belong_ID + 1
            ID_need = [id_1, id_2]

        elif left_lat == min(latitude):  # find 2.4 situation
            id_1 = area_belong_ID
            id_2 = area_belong_ID + 1
            id_3 = area_belong_ID + length_line - 1
            id_4 = area_belong_ID + length_line
            id_5 = area_belong_ID + length_line + 1
            ID_need = [id_1, id_2, id_3, id_4, id_5]
    elif area["Flag"] == 1:
        if left_lon == min(longitude):  # bottom
            if left_lat == min(latitude):  # find 1.1 situation
                id_1 = area_belong_ID
                id_2 = area_belong_ID + 1
                id_3 = area_belong_ID + length_line
                id_4 = area_belong_ID + length_line + 1
                ID_need = [id_1, id_2, id_3, id_4]
            elif left_lat == max(latitude):  # find 1.2 situation
                id_1 = area_belong_ID
                id_2 = area_belong_ID + length_line
                id_3 = area_belong_ID + length_line - 1
                ID_need = [id_1, id_2, id_3]
        elif left_lon == max(longitude):  # bottom
            if left_lat == min(latitude):  # find 1.3 situation
                id_1 = area_belong_ID
                id_2 = area_belong_ID + 1
                ID_need = [id_1, id_2]
            elif left_lat == max(latitude):  # find 1.4 situation
                pass
    return ID_need


filename = '../output/Research_area_code.json'
with open(filename) as f:
    area_data = json.load(f)

deta = 0.5  # Spatial resolution
latitude = np.round(np.arange(study_area[0], study_area[1], deta), 2)
longitude = np.round(np.arange(study_area[2], study_area[3], deta), 2)
num_shipdomain = 0
Chopper = dict()
Frank = []
frank_index = 0
time_format = "%Y-%m-%d %H:%M:%S"


file = 'ship_area_info_openwater.pkl'
with open(file, "rb") as f:
    ship_info = pickle.load(f)

for index_time in ship_info:
    start = time.clock()
    print(index_time)
    for area_belong_ID in ship_info[index_time]:
        # get the id that need to calculate the domain of every ship.
        needid = determine_computing_area(area_belong_ID, longitude.shape[0])
        ship_ta = ship_info[index_time][area_belong_ID]
        for index_ship in range(0, len(ship_ta)):
            own_ship = ship_ta[index_ship]
            own_length, own_width = process_shipll(own_ship['length'], own_ship['width'])
            own_tem = wangdomain((own_ship['longitude'], own_ship['latitude']),
                                 own_length, own_ship['sog'], own_ship['cog'])
            own_domain = [(own_tem[0, index], own_tem[1, index]) for index in range(0, len(own_tem[0, :]))]
            if index_ship + 1 != len(ship_ta):
                for index_tarship in range(index_ship + 1, len(ship_ta)):
                    target_ship = ship_ta[index_tarship]
                    # screen length of ship
                    tar_length, tar_width = process_shipll(target_ship['length'], target_ship['width'])
                    tar_tem = wangdomain((target_ship['longitude'], target_ship['latitude']),
                                         tar_length, target_ship['sog'], target_ship['cog'])
                    tar_domain = [(tar_tem[0, index], tar_tem[1, index]) for index in range(0, len(tar_tem[0, :]))]


                    po_re = position_relationship(own_domain, tar_domain)
                    if po_re:
                        # [0:time, 1:own_mmsi, 2:own_lon, 3:own_lat, 4:own_sog, 5:own_cog 6:own_length, 7:own_width
                        # 8:tar_mmsi, 9:tar_lon, 10:tar_lat, 11:tar_sog, 12:tar_cog 13:tar_length, 14:tar_width]
                        Frank_tem = [index_time, own_ship['mmsi'], own_ship['longitude'],own_ship['latitude'], own_ship['sog'],
                                     own_ship['cog'], own_length, own_width, target_ship['mmsi'], target_ship['longitude'],
                                     target_ship['latitude'], target_ship['sog'], target_ship['cog'],
                                     tar_length, tar_width]
                        # [记录信息在此处]
                        distnce = get_distance_hav(own_ship['latitude'], own_ship['longitude'],
                                                   target_ship['latitude'], target_ship['longitude'])
                        # get the mmsimmsi
                        if own_ship['mmsi'] > target_ship['mmsi']:
                            mname = target_ship['mmsi'] + own_ship['mmsi']
                        else:
                            mname = own_ship['mmsi'] + target_ship['mmsi']

                        if mname not in Chopper:
                            Chopper[mname] = []
                            Chopper[mname] = [index_time, distnce, frank_index]
                            Frank.append(Frank_tem)
                            frank_index += 1
                        else:
                            # judge  0:time 1:distance 2:index
                            time_indict = datetime.strptime(Chopper[mname][0], time_format).timestamp()
                            time_outdict = datetime.strptime(Chopper[mname][0], time_format).timestamp()
                            if np.absolute(time_outdict - time_outdict) < 20*60:
                                if Chopper[mname][1] > distnce:
                                    # debug
                                    # print('*'*30)
                                    # print(tar_domain)
                                    # print(own_domain)
                                    # print(index_time, mname, distnce, Chopper[mname])
                                    # print(Frank[Chopper[mname][2]])
                                    Frank[Chopper[mname][2]] = Frank_tem
                                    Chopper[mname][0] = index_time
                                    Chopper[mname][1] = distnce
                                else:
                                    pass  #  need't operation
                            else:
                                Chopper[mname] = [index_time, distnce, frank_index]
                                Frank.append(Frank_tem)
                                frank_index += 1

                        num_shipdomain += 1
            #end = time.clock()
    end = time.clock()
    print(num_shipdomain)
    print('Running time:', (end - start))
import shutil
srcfile = "ship_Frank.pkl"
with open(srcfile, "wb") as f:
    pickle.dump(Frank, f)
dstfile = '../output/{0}'.format(srcfile)
shutil.move(srcfile, dstfile)

