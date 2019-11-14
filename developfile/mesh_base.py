#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: mesh_base.py
@time: 2019-11-13 20:24
"""
import json
import numpy as np
import time

start = time.clock()
# divided into 0.5̊
# [47.88293333, 200.84929, -19.2496, 52.22840833]
# [latitude_min, latitude_max, longitude_min, longitude_max]
study_area = [0., 45., 90., 150.]
deta = 0.5  # Spatial resolution
latitude = np.round(np.arange(study_area[0], study_area[1], deta), 2)
longitude = np.round(np.arange(study_area[2], study_area[3], deta), 2)

lists = []
num = 0                             # Number of area.  The bottom left corner of the map is zero.
index_list = range(0, len(latitude))  # Number of latitude
ii_list = range(0, len(longitude))   # Number of longitude

for index in index_list:
    for ii in ii_list:
        list_area = dict()
        list_area = {"Left": {"lat": "", "lon": ""},
                     "Right": {"lat": "", "lon": ""},
                     "Flag": "", "area_ID": "",
                     "candidate":""}
        list_area["area_ID"] = num
        num = num + 1
        # Because two points can determine a rectangular area,
        # record the lower left and upper right latitude and longitude.
        #   FLag: 3, The middle area Flag is 3, and there are 8 areas around.
        #         2, The area Flag is 2, and there are 5 areas around.
        #         1, The area Flag is 1, and there are 3 areas around.
        list_area["candidate"] = 0
        list_area["Left"]["lat"] = latitude[index]
        list_area["Left"]["lon"] = longitude[ii]
        list_area["Right"]["lat"] = latitude[index] + deta
        list_area["Right"]["lon"] = longitude[ii] + deta
        list_area["Flag"] = 3
        if index == min(index_list) or index == max(index_list):
            list_area["Flag"] = 2
            if ii == min(ii_list) or ii == max(ii_list):
                list_area["Flag"] = 1
        # Find the area above and below the entire area.
        if ii == min(ii_list) or ii == max(ii_list):
            list_area["Flag"] = 2
            if index == min(index_list) or index == max(index_list):
                list_area["Flag"] = 1
        lists.append(list_area)

# save the mesh infomation as .json format
with open("../output/Research_area_code.json", "w", encoding="UTF-8") as f_dump:
    s_dump = json.dump(lists, f_dump)
end = time.clock()
print(" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", "\n", "   succesful complete the task ", "\n", "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print('Running time:', (end-start))