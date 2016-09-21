# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 09:13:14 2016

METODO DE NEWTON

@author: mcvalenti
"""

import numpy as np

def newton(x,f,fp):
    x1=x-(float(f)/float(fp))
    dif=np.abs(x-x1)
    return x1,dif
            