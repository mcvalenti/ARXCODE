"""
Created on Mon Apr 25 15:54:20 2016

Coordenadas fijas a la Tierra
Rotacion terrestre. 

@author: mcvalenti
"""
import numpy as np

def rot_tierra(x,y,z,minu,ts):
    pos=[x,y,z]
    OmegaT=ts#+minu*60.0*15.04/3600.0 # velocidad angular de la tierra [seg]
    OmegaT_rad=OmegaT*np.pi/180.0

    ma_rot=np.array([[np.cos(OmegaT_rad), np.sin(OmegaT_rad), 0.0],
                       [-np.sin(OmegaT_rad), np.cos(OmegaT_rad), 0.0],
                       [0.0, 0.0, 1.0]])
#    print ma_rot
#    print pos                   
    r_prima=np.dot(ma_rot,pos)
    return r_prima 







