#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: aisdoamintest.py
@time: 2019-11-09 10:30
"""
import os
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.abspath(os.path.join(current_path, '../'))
from developfile.ship_domain import fujidomain, wangdomain,goodwindomain
from developfile.ship_domain import ship_shap_base, ship_shape
from developfile.tools import read_ais
from matplotlib import pyplot as plt
from matplotlib.path import Path
from matplotlib.animation import FuncAnimation
from matplotlib.patches import PathPatch

plt.style.use('seaborn-pastel')

'''
This script is used for test the dynamic ship domain base on AIS data.
'''
# setting the input url
input_url = '../input/ais_data.xlsx'
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

#
cog = 0
# plot gif
# gif 20191109
ship_path_base = ship_shap_base(length, width)
ship_path = ship_shape(ship_path_base.T, cog)
# move the center of ship to real position
ship_ver = ship_path.copy()
ship_ver[:, 1] = ship_path[:, 1] + ownship_y
ship_ver[:, 0] = ship_path[:, 0] + ownship_x
#
path = Path(ship_ver)
pathpatch = PathPatch(path, facecolor='gray', edgecolor='k')
#
fig, ax = plt.subplots(1, 1, figsize=(6.40, 4.80))
# http://adrian.pw/blog/matplotlib-transparent-animation/
# set figure background opacity (alpha) to 0
if alpha0 == True:
    fig.patch.set_alpha(0.)
    fig.tight_layout()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)
    ax.patch.set_visible(False)

# set the line of ship domain
line1, = ax.plot([], [], lw=2, color='gray')
line2, = ax.plot([], [], color='blue')
line3, = ax.plot([], [], color='r')
line4, = ax.plot([], [], color='purple')
speed_text = ax.text(-1300, 1450, '', fontsize=10)
time_text = ax.text(-1300, 1600, '', fontsize=10)


# set the axis
ax.add_patch(pathpatch)
ax.set_aspect(1.0)
ax.set_xlim(-1500, 1700)
ax.set_ylim(-1000, 1700)

plt.legend(handles=[line1, line2, line3, line4],
           labels=['fuji 1971', 'goodwin 1975', 'wang 2012 r=0.5',
                   'wang 2012 r=0.8'],
           loc='upper right', fontsize=10)

ax.grid(False)

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])
    speed_text.set_text('')
    time_text.set_text('')
    return line1, line2, line3, line4,

def animate(i):
    # calculate the domain
    domain_ship = fujidomain((ownship_x, ownship_y), length, cog)
    domain_ship_g = goodwindomain((ownship_x, ownship_y), cog)
    domain_ship_w = wangdomain((ownship_x, ownship_y), length, sog_ship[i], cog)
    domain_ship_w2 = wangdomain((ownship_x, ownship_y), length, sog_ship[i], cog, r_static=0.8)
    line1.set_data(domain_ship[0], domain_ship[1])
    line2.set_data(domain_ship_g[0], domain_ship_g[1])
    line3.set_data(domain_ship_w[0], domain_ship_w[1])
    line4.set_data(domain_ship_w2[0], domain_ship_w2[1])
    speed_text.set_text('Speed: {0} knots'.format(str(sog_ship[i])))
    time_text.set_text('{0}'.format(str(time[i])))

    return line1, line2, line3, line4


anim = FuncAnimation(fig, animate, init_func=init,
                               frames=int(len(cog_ship)/3), interval=50, blit=True)
if alpha0 == True:
    anim.save('../output/ship_domain.gif', savefig_kwargs={'transparent': True, 'facecolor': 'none'}) #savefig_kwargs={'bbox_inches': 'tight'})
else:
    anim.save('../output/ship_domain.gif', dpi=72)
