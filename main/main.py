'''
Created on 26/01/2017

@author: mcvalenti
'''
import os, glob, os.path, time
from datetime import datetime
from AjustarTLE.AjustarTLE import *
from Comparar.TleVsCods import *
from Estadistica.maCovar import *
from TleAdmin.get_tle import*

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
    
    
    print 'Indique si va a procesar: TLE o Datos_Mision'
    
    DATOS=raw_input()
    t1=datetime(2003,04,03)
    t0=datetime(2003,03,20)
    
    arch_tle=importar_tle('8820',t0,t1)
    
    if DATOS == 'TLE':
        archivo=EjecutaAjustarTLE()
    else:
        EjecutaComparacion()
        
    """
    Calculo de la matriz de Covarianza
    """    
    EjecutaMaCovar(archivo)
    
    print '-----------------------------------------------'
    print '--Fin del PROCESAMIENTO--'