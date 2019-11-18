#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: ship_domain.py
@time: 2019-11-07 21:54
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from math import pi, sqrt, cos, sin, log10 as lg, log as ln

'''
This work is based on ship safety domains approach.

The term of a ship domain was ﬁrst introduced in (Fuji, 1971)
definition: a two-dimensional area surrounding a 
        ship which other ships must avoid – it may be considered as the area of evasion.
Parameters: 
    coordinate
        ship_latitude: 
        ship_longtitude:
    sog: Speed over ground (knots)	
    cog: Course over ground (degrees)
-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*    
* method 1   Fuji
*    name     |   description in Ellipse |  description in ship
*    ownship_x:  x-position of the center,    longitude
*    ownship_y:  y-position of the center,    latitude
*    domain_a :  semi-major axis,             7*length
*    domain_b :  semi-minor axis,             3.5*length
*    cog:      rotation angle,              cog
*    

* method 2   Goodwin
*    Thita: the relative bearing of other ships 
*    Sector 1 (starboard sector) 0  <= Thita <= 112.5 
*    Sector 2 (port sector)      247.5 <= Thita < 360 
*    Sector 3 (astern sector)    112.5 <= Thita < 247.5
*    Ref. 
*    [1] Goodwin, E. (1975). A Statistical Study of Ship Domains. Journal of Navigation, 28(3), 328-344. 

* method 3   wang
*    Vown: the own ship speed represented in knots.
*    IQSDk = {(x,y) | fk(x,y;Q) <= 1, Q = {R_fore, R_aft, R_starb, R_port}, k >= 1 }
*    fk(x,y;Q) = ((2 * x) / ((1 + sgnx) * R_fore - (1 - sgnx) * Raft))^k
*              + ((2 * y) / ((1 + sgny) * R_starb - (1 - sgny) * R_port))^k
*    sgnx  = 1 or -1 (x>=0, else )
*    # 
*        / R_fore = (1 + 1.34 * ( K_AD^2 + (K_DT/2)^2)^1/2 ) * L
*        | R_aft = (1 + 0.67 * ( K_AD^2 + (K_DT/2)^2)^1/2 ) * L
*        | R_starb = (0.2 + K_DT) * L
*        \ R_port = (0.2 + 0.75 * K_DT) * L
*    
*    K_AD = AD/L = 10^(0.3591lgVown+0.0952)
*    K_DT = DT/L = 10^(0.5441lgVown-0.0795)
*    # 
*    Ref. list  
*        [1] Wang, N., 2013. A novel analytical framework for dynamic quaternion ship domains.J. Navig. 66, 265–281.
-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
'''


def fujidomain(own_ship_xy, length, cog=0):
    """
    Parameters
    ----------
    own_ship_xy : (float, float)
        xy coordinates of ellipse centre.
    domain_a : float
        Total length (diameter) of horizontal axis.
    domain_b : float
        Total length (diameter) of vertical axis.
    cog : scalar, optional
        Rotation in degrees anti-clockwise.
    """
    domain_b = 7 * length
    domain_a = 3.5 * length
    t_rot = pi * cog / 180
    t = np.linspace(0, 2 * pi, 100)
    Ell = np.array([domain_a * np.cos(t), domain_b * np.sin(t)])
    R_rot = np.array([[cos(t_rot), sin(t_rot)], [-sin(t_rot), cos(t_rot)]])
    Ell_rot = np.zeros((2, Ell.shape[1]))
    for i in range(Ell.shape[1]):
        Ell_rot[:, i] = np.dot(R_rot, Ell[:, i])
    domain_path = [own_ship_xy[0] + Ell_rot[0, :], own_ship_xy[1] + Ell_rot[1, :]]
    return domain_path


def goodwindomain(own_ship_xy, cog):
    """
    Parameters
    ----------
    own_ship_xy : (float, float)
        xy coordinates of ellipse centre.
    cog : scalar, optional
        Rotation in degrees anti-clockwise.
    """
    thita = np.array([cog, cog + 112.5, cog + 247.5, cog + 360])
    # number_of_scetor:
    #   use the number_of_scetor to control the result of sector.
    #   defalut values is 100, that means every sector have 100 points.
    #   sector_tem: (x,y), size:(2, number_of_scetor)
    number_of_scetor = 100
    radius_domain =[1.852*1000*x for x in [0.85, 0.4, 0.75]] # 0.75
    thita_deg = pi * thita / 180
    sector = np.zeros(shape=(2, 3 * number_of_scetor + 1))
    # calculate the sectors
    num_start = 0
    for jj in range(0, thita_deg.shape[0] - 1):
        t = np.linspace(thita_deg[jj], thita_deg[jj + 1], number_of_scetor)
        sector_tem = np.array([radius_domain[jj] * np.sin(t), radius_domain[jj] * np.cos(t)])
        sector[:, num_start:num_start + number_of_scetor] = sector_tem[:, :]
        num_start = num_start + number_of_scetor
    sector[:, 3 * number_of_scetor] = sector[:, 0]
    sector[0, :] += own_ship_xy[0]
    sector[1, :] += own_ship_xy[1]
    ship_sector = sector.copy()
    return ship_sector


def wangdomain(own_ship_xy, length, vown, cog=0, k_shape=2, r_static=0.5, unit='deg'):
    """
    Parameters
    ----------
    own_ship_xy : (float, float)
        xy coordinates of ellipse centre.
    cog : scalar, optional
        Rotation in degrees anti-clockwise.
    vown:  is the own ship speed represented in knots
    k_shape :shape index
    """
    # Constant
    r0 = 0.5
    if isinstance(length, str):
        length = float(length)
    # L is the own ship length,
    # k_AD and k_DT represent gains of the advance, AD ,
    # and the tactical diameter, D T ,
    if vown != 0.0:
        k_ad = 10 ** (0.359 * lg(vown) + 0.0952)
        k_dt = 10 ** (0.541 * lg(vown) - 0.0795)
    else:
        # When the speed approaches zero infinitely， k_ad = 10**-Inf = 0
        k_ad = 0
        k_dt = 0
    R_fore = (1 + 1.34 * sqrt((k_ad) ** 2 + (k_dt / 2) ** 2)) * length
    R_aft = (1 + 0.67 * sqrt((k_ad) ** 2 + (k_dt / 2) ** 2)) * length
    R_starb = (0.2 + k_dt) * length
    R_port = (0.2 + 0.75 * k_dt) * length

    R = np.array((R_fore, R_aft, R_starb, R_port))
    r_fuzzy = ((ln(1 / r_static)) / (ln(1 / r0))) ** (1 / k_shape)
    R_fuzzy = r_fuzzy * R
    # y_1: first quadrant  x >= 0 y >= 0
    x_max = R_fuzzy[0]
    x_min = -R_fuzzy[1]
    x_serises_plus = np.linspace(0, x_max, 80)
    x_serises_minus = np.linspace(x_min, -0.01, 80)
    # x>=0, y>=0
    y_1 = R_fuzzy[2] * pow((1 - (x_serises_plus / R_fuzzy[0]) ** k_shape), 1 / k_shape)
    y_4 = R_fuzzy[3] * -pow((1 - (x_serises_plus / R_fuzzy[0]) ** k_shape), 1 / k_shape)
    y_2 = R_fuzzy[2] * pow((1 - (-x_serises_minus / R_fuzzy[1]) ** k_shape), 1 / k_shape)
    y_3 = R_fuzzy[3] * -pow((1 - (-x_serises_minus / R_fuzzy[1]) ** k_shape), 1 / k_shape)
    # stack the column
    curve1 = np.column_stack((x_serises_plus, y_1))
    curve2 = np.column_stack((x_serises_minus, y_2))
    curve3 = np.column_stack((x_serises_minus, y_3))
    curve4 = np.column_stack((x_serises_plus, y_4))
    # Primacy connection
    curve4 = np.flipud(curve4)
    curve3 = np.flipud(curve3)
    # cat the data series to one curve.
    curves = np.row_stack((curve1, curve4, curve3, curve2)).T

    #
    t_rot = pi * cog / 180 - pi / 2
    R_rot = np.array([[cos(t_rot), sin(t_rot)], [-sin(t_rot), cos(t_rot)]])
    for i in range(curves.shape[1]):
        curves[:, i] = np.dot(R_rot, curves[:, i])
    # Translation to position
    curves[0, :] += own_ship_xy[0]
    curves[1, :] += own_ship_xy[1]
    if unit == 'deg':
        curves = curves/(111*1000)
    return curves

def ship_shap_base(length, width):
    #ship_path = [[0, length/2], [width/2, length/10], [width/2, -length/2],
    #             [-width/2, -length/2], [width/2, -length/10], [0, length/2]]
    tem_ship = [(0, length / 2), (width / 2, length / 10), (width / 2, -length / 2),
                 (-width / 2, -length / 2), (-width / 2, length / 10), (0, length / 2)]
    ship_path = np.array(tem_ship, float)
    return ship_path

def ship_shape(ship_path, cog):
    t_rot = pi * cog / 180
    R_rot = np.array([[cos(t_rot), sin(t_rot)], [-sin(t_rot), cos(t_rot)]])

    ship_rot = np.zeros((2, ship_path.shape[1]))
    for i in range(ship_path.shape[1]):
        ship_rot[:, i] = np.dot(R_rot, ship_path[:, i])
    return ship_rot.T


if __name__ == '__main__':
    # - ship infomation
    length = 175
    width = 30.0
    ownship_x = 400.0
    ownship_y = 21
    cog = 50
    v_speed = 50
    # - process
    ship_path_base = ship_shap_base(length, width)
    ship_path = ship_shape(ship_path_base.T, cog)
    # move the center of ship to real position
    ship_ver = ship_path.copy()
    ship_ver[:, 1] = ship_path[:, 1] + ownship_y
    ship_ver[:, 0] = ship_path[:, 0] + ownship_x
    # calculate the domain
    domain_ship = fujidomain((ownship_x, ownship_y), length, cog)
    domain_ship_g = goodwindomain((ownship_x, ownship_y), cog)
    domain_ship_w = wangdomain((ownship_x, ownship_y), length, v_speed, cog)
    domain_ship_w2 = wangdomain((ownship_x, ownship_y), length, v_speed, cog, r_static=0.8)

    # ----------------------------#
    #  plot the ship domain
    # ----------------------------#
    path = Path(ship_ver)
    pathpatch = PathPatch(path, facecolor='gray', edgecolor='k')
    #
    fig, ax = plt.subplots()
    ax.add_patch(pathpatch)
    line1, = plt.plot(domain_ship[0], domain_ship[1], 'gray')
    line2, = plt.plot(domain_ship_g[0], domain_ship_g[1], 'blue')
    line3, = plt.plot(domain_ship_w[0], domain_ship_w[1], 'r')
    line4, = plt.plot(domain_ship_w2[0], domain_ship_w2[1], 'purple')

    plt.grid(color='lightgray', linestyle='--')
    plt.legend(handles=[line1, line2, line3, line4],
               labels=['fuji 1971', 'goodwin 1975', 'wang 2012 r=0.5',
                       'wang 2012 r=0.8'],
               loc='upper right')
    ax.set_aspect(1.0)
    plt.show()
