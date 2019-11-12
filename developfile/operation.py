#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: operation.py
@time: 2019-11-12 15:45
"""
import os
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.abspath(os.path.join(current_path, '../'))
#from developfile.ship_domain import fujidomain, wangdomain,goodwindomain
#from developfile.ship_domain import ship_shap_base, ship_shape
from tools import read_ais
import time
'''
This script is used for test the dynamic ship domain base on AIS data.

'''
import time
from functools import wraps

def main():
    # setting the input url
    input_url = '/Users/yaochenyang/Desktop/aischangjiang/6.csv'
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
    print(keys)

if __name__ == '__main__':
    main()