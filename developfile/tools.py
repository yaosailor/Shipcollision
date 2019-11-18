#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: tools.py
@time: 2019-11-07 10:33
"""
import pandas as pd
import json
import numpy as np
import time
import pickle
from datetime import datetime, timedelta
from collections import OrderedDict
from fastkml import kml
from math import sin, asin, cos, radians, fabs, sqrt
from setting import study_area as study_area_default

'''
def read_ais()

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
    #df = pd.read_excel(input_url)
    df = pd.read_csv(input_url)
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_excel.html
    # next_ship_index: find the index of title
    # because the fist title is not include the varible, I add the first index '0' and last index  into the ship_spiltindex
    next_ship_index = df.loc[df['FID'] == 'FID']
    ship_spiltindex = next_ship_index.index.values
    ship_spiltindex = np.insert(ship_spiltindex, [0, len(ship_spiltindex)], [-1, df.shape[0]])
    # changed the order
    df = df[['mmsi', 'vessel_type', 'length', 'width', 'sog', 'cog', 'longitude', 'latitude', 'heading', 'dt_pos_utc']]
    keys_data = df.keys()
    # These are the parameters we need
    # In order to distinguish list and others, I changed the type of length and width into 'string' instead of 'float'.
    # Considering the demand that we should eliminate information with a speed of 0. First we should get the mmsi, then
    # We judge according to the speed of the ship(sog).
    parameter_needs = {'mmsi': 'int',
                       'vessel_type': 'str',
                       'sog': 'float',
                       'length': 'str',
                       'width': 'str',
                       'longitude': 'float',
                       'latitude': 'float',
                       'cog': 'float',
                       'heading': 'float',
                       'dt_pos_utc': 'time'}
    # Filter by using advanced criteria（vessel_type >> sog）
    type_criteria = ['Cargo', 'Passenger', 'SAR', 'Tanker']
    sog_criteria = [0, 50]  # (min_speed, max_speed)knots
    # shipdata_base: use shipdata_base to save the ship infomations from AIS
    # This is the dict structure of shipdata_base
    # name     keys         type   list[:]
    #       |- vessel_type  str
    # mmsi -|- length       str
    # (dict)|- width        str
    #       |- longitude    list    float
    #       |- latitude     list    float
    #       |- sog          list    float
    #       |- cog          list    float
    #       |- heading      list    float
    #       |- dt_pos_utc   list    datetime
    bugmodel = False
    shipdata_base = dict()
    number_error = 0
    # inns:index_number_ship
    for inns in range(0, ship_spiltindex.size-1):
        for _ in keys_data.values:
            if _ in parameter_needs:
                # print(_, parameter_needs[_])
                data_temp = df.loc[ship_spiltindex[inns]+1:ship_spiltindex[inns+1]-1, [_]]
                dd_use = data_temp[_].str.split("\t", n=1, expand=True)
                if parameter_needs[_] == 'float' or parameter_needs[_] == 'int':
                    try:
                        formatdata = list(map(eval, dd_use[1][:].values))
                    # Read error ：due to error format
                    except Exception as inst:
                        if bugmodel is True:
                            print("OS error: {0}".format(inst), 'mmsi:{}'.format(str(ship_mmsi)),
                                  'erro', 'ship_spiltindex: ', ship_spiltindex[inns], 'parameter: ', _,
                                  'ship type: ', df['vessel_type'][ship_spiltindex[inns]+1])
                        number_error += 1
                        shipdata_base.pop(ship_mmsi)
                        break
                    if _ == 'mmsi':
                        ship_mmsi = str(formatdata[0])
                        shipdata_base[ship_mmsi] = dict()
                    if _ == 'sog':
                        formatdata = np.array(formatdata)
                        index_filter_ship, = np.where((formatdata > 0.) & (formatdata < 50.))

                elif parameter_needs[_] == 'str':
                    formatdata = dd_use[1][:].values
                    shipdata_base[ship_mmsi][_] = formatdata[0]
                    # Filter and delete the Useless information
                    if _ == 'vessel_type' and formatdata[0] not in type_criteria:
                            shipdata_base.pop(ship_mmsi)
                            break
                elif parameter_needs[_] == 'time':
                    formatdata = [datetime.strptime(tem_str, "%Y-%m-%d %H:%M:%S") for tem_str in dd_use[1][:].values]
                else:
                    print('error: transform the format of data')
                if _ != 'mmsi' and parameter_needs[_] != 'str':
                    formatdata_af = [formatdata[x] for x in index_filter_ship]
                    shipdata_base[ship_mmsi][_] = formatdata_af
                    # if the length of index_filter_ship equal the length of formatdata,
                    # it means that the ship didn't move during the whole time.
                    if not formatdata_af:
                        shipdata_base.pop(ship_mmsi)
                        break

    if bugmodel is True:
        print(ship_spiltindex.size, 'error infomation: ', number_error, number_error/ship_spiltindex.size)
    return shipdata_base


def freq_vessel_type(ship_info):
    keys = list(ship_info.keys())
    freq = {}
    for index in keys:
        sog_ship = ship_info[index]['vessel_type']
        if sog_ship not in list(freq.keys()):
            freq[sog_ship] = 1
        else:
            freq[sog_ship] += 1
    for _ in freq:
        print(_, ': ', freq[_])


def setup_mesh(study_area=False):
    start = time.clock()
    # divided into 0.5̊
    # [47.88293333, 200.84929, -19.2496, 52.22840833]
    # [latitude_min, latitude_max, longitude_min, longitude_max]
    # default study_area = [0., 45., 90., 150.]
    if not study_area:
        study_area = study_area_default
    deta = 0.5  # Spatial resolution
    latitude = np.round(np.arange(study_area[0], study_area[1], deta), 2)
    longitude = np.round(np.arange(study_area[2], study_area[3], deta), 2)
    lists = []
    num = 0  # Number of area.  The bottom left corner of the map is zero.
    index_list = range(0, len(latitude))  # Number of latitude
    ii_list = range(0, len(longitude))  # Number of longitude
    for index in index_list:
        for ii in ii_list:
            list_area = dict()
            list_area = {"Left": {"lat": "", "lon": ""},
                         "Right": {"lat": "", "lon": ""},
                         "Flag": "", "area_ID": "",
                         "candidate": ""}
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
    output_meshfile = '../output/Research_area_code.json'
    with open(output_meshfile, "w", encoding="UTF-8") as f_dump:
        s_dump = json.dump(lists, f_dump)
    end = time.clock()
    print(" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", "\n", "   succesful complete the task ", "\n",
          "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print('Running time:', (end - start))
    return output_meshfile


def cal_area_id(lat_tem, lon_tem, study_area=False):
    if not study_area:
        study_area = study_area_default
    deta = 0.5  # Spatial resolution
    #
    if lat_tem < study_area[0] or lat_tem > study_area[1]:
        return None
    if lon_tem < study_area[2] or lon_tem > study_area[3]:
        return None
    # latitude = np.round(np.arange(study_area[0], study_area[1], deta), 2)
    longitude = np.round(np.arange(study_area[2], study_area[3], deta), 2)
    index = (lat_tem - study_area[0]) // 0.5
    jndex = (lon_tem - study_area[2]) // 0.5
    area_id = int((int(index)) * len(longitude) + jndex)
    return area_id


def time2minutes(date_re, minutes_set=5):
    time_format = "%Y-%m-%d %H:%M:%S"
    delta_set = 60 * minutes_set
    if isinstance(date_re, datetime):
        timeArray_re = date_re.timestamp()
    else:
        timeArray_re = datetime.strptime(date_re, time_format).timestamp()
    Quotient_time = timeArray_re//(60*minutes_set)
    residue_time = timeArray_re % (60*minutes_set)
    if residue_time <= (delta_set/2):
        c = Quotient_time * delta_set
    else:
        c = (1+Quotient_time) * delta_set
    final = datetime.fromtimestamp(c)
    return final, residue_time


def time_array(inputfile,date_start, date_end):
    '''
    :param inputfile:
    :param date_start:
    :param date_end:
    :return: date_ship
    # date_ship: use date_ship to organize information by time
    # This is the dict structure of date_ship
    # name     keys             list[0]
    #       |- area_id    -|-     mmsi
    # time -|-    ·        |-     longitude
    # (dict)|-    ·        |-     latitude
    #       |-    ·        |-     sog
    #       |- area_id     |-     cog

    '''
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
    # total_ship: save data closest to standardization time.
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
        # get the index of needed information depend on timeseries.
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


def kml2path(url='None'):
    # https://fastkml.readthedocs.io/en/latest/usage_guide.html
    # https://github.com/cleder/fastkml/issues/57
    # https://github.com/kennethreitz/requests-html/issues/145 !!!
    '''
     File "src/lxml/etree.pyx", line 3213, in lxml.etree.fromstring
      File "src/lxml/parser.pxi", line 1872, in lxml.etree._parseMemoryDocument
    ValueError: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
    Process finished with exit code 1
    '''
    try:
        kml_file = url
        with open(kml_file, 'rt', encoding="UTF-8") as myfile:
            doc = myfile.read().encode('utf-8')
    except:
        kml_file = '../input/inland_waterway_channel.kml'
        with open(kml_file, 'rt', encoding="UTF-8") as myfile:
            doc = myfile.read().encode('utf-8')
    k = kml.KML()
    k.from_string(doc)
    features = list(k.features())
    resulet = features[0]._features[0].geometry.xy
    resulet = [(resulet[0][_], resulet[1][_]) for _ in range(0, len(resulet[0]))]
    return resulet

earth_radius = 6371             # 地球平均半径，6371km


def hav(theta):
    s = sin(theta / 2)
    return s * s

def get_distance_hav(lat0, lng0, lat1, lng1):
    "haversine"
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)

    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * earth_radius * asin(sqrt(h))
    return distance