#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: ship_domain.py
@time: 2019-11-07 21:54
"""

import numpy as np
from matplotlib import pyplot as plt
from math import pi, cos, sin
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
method 1   Fuji
    ···
method 2   Goodwin
    ···
method 3   wang
    Vown: the own ship speed represented in knots.
    IQSDk = {(x,y) | fk(x,y;Q) <= 1, Q = {R_fore, R_aft, R_starb, R_port}, k >= 1 }
    fk(x,y;Q) = ((2 * x) / ((1 + sgnx) * R_fore - (1 - sgnx) * Raft))^k
              + ((2 * y) / ((1 + sgny) * R_starb - (1 - sgny) * R_port))^k
    sgnx  = 1 or -1 (x>=0, else )
    # 待补充
        / R_fore = (1 + 1.34 * ( K_AD^2 + (K_DT/2)^2)^1/2 ) * L
        | R_aft = (1 + 0.67 * ( K_AD^2 + (K_DT/2)^2)^1/2 ) * L
        | R_starb = (0.2 + K_DT) * L
        \ R_port = (0.2 + 0.75 * K_DT) * L
    
    K_AD = AD/L = 10^(0.3591lgVown+0.0952)
    K_DT = DT/L = 10^(0.5441lgVown-0.0795)
    # 待补充
    Ref. list  
        [1] Wang, N., 2013. A novel analytical framework for dynamic quaternion ship domains.J. Navig. 66, 265–281.

'''

length = 125
u = 1.              # x-position of the center
v = 0.5             # y-position of the center
b = 7*length        # radius on the x-axis
a = 3.5*length      # radius on the y-axis
t_rot = pi*250/180        # rotation angle
fig, ax = plt.subplots()
t = np.linspace(0, 2*pi, 100)
Ell = np.array([a*np.cos(t) , b*np.sin(t)])
# u,v removed to keep the same center location
# R_rot = np.array([[cos(t_rot), -sin(t_rot)], [sin(t_rot), cos(t_rot)]])
R_rot = np.array([[cos(t_rot), sin(t_rot)], [-sin(t_rot), cos(t_rot)]])

# 2-D rotation matrix
Ell_rot = np.zeros((2, Ell.shape[1]))
for i in range(Ell.shape[1]):
    Ell_rot[:,i] = np.dot(R_rot, Ell[:, i])

plt.plot(u+Ell[0, :], v+Ell[1, :])     # initial ellipse
plt.plot(u+Ell_rot[0, :], v+Ell_rot[1, :], 'k' )    # rotated ellipse
plt.grid(color='lightgray', linestyle='--')
ax.set_aspect(1.0)
plt.show()