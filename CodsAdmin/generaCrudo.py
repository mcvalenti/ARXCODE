'''
Created on 22/12/2016

@author: mcvalenti
'''

import os, glob
import numpy as np
from StateVector import StateVector

lista=glob.glob('TOD_O/*')

for arch in lista:
    print arch, type(arch)
    sv1=StateVector(arch)
    print sv1.fecha, sv1.hora