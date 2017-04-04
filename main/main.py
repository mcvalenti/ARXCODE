'''
Created on 26/01/2017

@author: mcvalenti
'''
import os
import numpy as np
from datetime import datetime
from TleAdmin.TLE import Tle
from SistReferencia.sist_deCoordenadas import teme2tod



if __name__ == '__main__':
    
    """
    Se crean los directorios necesarios.
    """
    
    d1='../TleAdmin/tle'
    if not os.path.exists(d1):
        os.mkdir(d1)
    d2='../AjustarTLE/diferencias'
    if not os.path.exists(d2):
        os.mkdir(d2)
    d3='../main/matrices/'
    if not os.path.exists(d3):
        os.mkdir(d3)
    d4='../visual/archivos'
    if not os.path.exists(d4):
        os.mkdir(d4)

#     tle_archivo='../TleAdmin/tle/37673tle3'
#     tle1=Tle(tle_archivo)
#     epoca=tle1.epoca()
#     r,v=tle1.propagaTLE()    
#     r=[3961.0035498,6010.7511740,4619.3009301]
#     epoca=datetime(2000,06,28,15,8,51)
#     r_tod=teme2tod(epoca, r) 
# 
#     print r
#     print r_tod
#     print r-r_tod

    