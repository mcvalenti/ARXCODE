'''
Created on 26/01/2017

@author: mcvalenti
'''
import os, glob, os.path, time
from AjustarTLE.AjustarTLE import *
from Comparar.TleVsCods import *

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
    
    print 'Indique si va a procesar: TLE o Datos_Mision'
    
    DATOS=raw_input()
    
    if DATOS == 'TLE':
        EjecutaAjustarTLE()
    else:
        EjecutaComparacion()
    print '--Fin del PROCESAMIENTO--'