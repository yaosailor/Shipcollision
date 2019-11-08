#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: synthetic_indicator.py
@time: 2019-11-06 15:19
"""
'''
This work is based on Synthetic indicator approach.
Parameters: 
    Closest Point of Approach (CPA),which means the closest distance between two ships 
    Distance to CPA (DCPA),
    Time to CPA (TCPA),  which is the time left to the CPA point.l
'''
import pandas as pd
from developfile.tools import read_ais

input_url = '../input/ais_data.xlsx'
ship_info = read_ais(input_url)


