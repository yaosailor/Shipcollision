#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: tools.py
@time: 2019-11-07 10:33
"""
import pandas as pd
import datetime


'''
*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
* Unimportant information   *
*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
    * There are Parameters from AIS data:
        'FID', 'mmsi', 'imo', 'vessel_name', 'callsign', 'vessel_type',
               'vessel_type_code', 'vessel_type_cargo', 'vessel_class', 'length',
               'width', 'flag_country', 'flag_code', 'destination', 'eta', 'draught',
               'position', 'longitude', 'latitude', 'sog', 'cog', 'rot', 'heading',
               'nav_status', 'nav_status_code', 'source', 'ts_pos_utc',
               'ts_static_utc', 'dt_pos_utc', 'dt_static_utc', 'vessel_type_main',
               'vessel_type_sub', 'message_type', 'eeid', 'dtg'
        !explain
            1 vessel_class: Class B transponders have been developed to provide the safety and navigation benefits of AIS to smaller vessels with
            lower cost and simpler installation when compared to Class A. As the Class B system was developed after the introduction
            of Class A it was designed to be compatible whilst protecting the safety critical operation of the Class A system for big
            ships. 
            Ref. http://old.voilier-idem.com/Documents/carto_gps/aisguide.pdf
            
            2 eta:https://blog.csdn.net/hejishan/article/details/2166900
        
*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
*  important information    *
*-*-*-*-*-*-*-*-*-*-*-*-*-*-*           
    * These are the parameters we need：
        1 mmsi : MMSI number of the vessel (AIS identifier)
        2 vessel_type: 
            Type of the vessel according to AIS Specification
            The details Listed in '../doc/AIS_Ship_Types.pdf'
            Ref.https://api.vtexplorer.com/docs/ref-aistypes.html
            
        3 length: length  
        4 width: beam
        5 longitude: Geographical longitude (WGS84)
        6 latitude:  Geographical latitude (WGS84)
        7 sog: Speed over ground (knots)	
        8 cog: Course over ground (degrees)
        9 heading: Heading (degrees) of the vessel's hull. A value of 511 indicates there is no heading data.
        10 dt_pos_utc:  the time of position report(UTC)
'''


def read_ais(input_url):
    df = pd.read_excel(input_url)
    keys_data = df.keys()
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
    next_ship_index = df.loc[df['FID'] == 'FID']  # 读取某一行
    # These are the parameters we need
    parameter_needs = {'mmsi': 'int',
                       'vessel_type': 'str',
                       'length': 'float',
                       'width': 'float',
                       'longitude': 'float',
                       'latitude': 'float',
                       'sog': 'float',
                       'cog': 'float',
                       'heading': 'float',
                       'dt_pos_utc': 'time'}
    #
    for _ in keys_data.values:
        if _ in parameter_needs:
            print(_, parameter_needs[_])
            data_temp = df.loc[0:next_ship_index.index[0] - 1:, [_]]
            dd_use = data_temp[_].str.split("\t", n=1, expand=True)
            if parameter_needs[_] == 'float' or parameter_needs[_] == 'int':
                formatdata = list(map(eval, dd_use[1][:].values))
            elif parameter_needs[_] == 'str':
                formatdata = dd_use[1][:].values
            elif parameter_needs[_] == 'time':
                formatdata = [datetime.datetime.strptime(tem_str, "%Y-%m-%d %H:%M:%S") for tem_str in dd_use[1][:].values]
            else:
                print('error: transform the format of data')
            print('&' * 30, _)
            print(dd_use[1][:].values)
            print(formatdata[4:10])




