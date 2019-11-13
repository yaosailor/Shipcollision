#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: operation.py
@time: 2019-11-12 15:45
"""
import os, shutil
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.abspath(os.path.join(current_path, '../'))
# from developfile.ship_domain import fujidomain, wangdomain,goodwindomain
# from developfile.ship_domain import ship_shap_base, ship_shape
from tools import read_ais, freq_vessel_type
import pickle
from pathlib import Path


'''
This script is used for test the dynamic ship domain base on AIS data.

'''
import time
from functools import wraps

def main(input_url):
    # setting the input url
    #input_url = '/Users/yaochenyang/Desktop/aischangjiang/5.csv'
    alpha0 = False
    ship_info = read_ais(input_url)
    keys = list(ship_info.keys())
    # - ship infomation-
    length = float(ship_info[keys[1]]['length'])
    width = float(ship_info[keys[1]]['width'])
    ownship_x = 0
    ownship_y = 0
    sog_ship = ship_info[keys[1]]['sog']
    cog_ship = ship_info[keys[1]]['cog']
    time = ship_info[keys[1]]['dt_pos_utc']
    return ship_info


if __name__ == '__main__':
    data_url = '../input'
    roots = Path(data_url)
    ship_info = dict()
    for index, file in enumerate(list(roots.glob('*.csv'))):
        ship_info_tem = main(file)
        ship_info = dict(ship_info, **ship_info_tem)

    freq_vessel_type(ship_info)
    srcfile = "ship_info.pkl"
    with open(srcfile, "wb") as f:
        pickle.dump(ship_info, f)
    dstfile = '../output/{0}'.format(srcfile)
    shutil.move(srcfile, dstfile)
    # https://www.cnblogs.com/taoshiqian/p/9771786.html
