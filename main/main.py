'''
Created on 26/01/2017

@author: mcvalenti
'''
import os
import numpy as np
from datetime import datetime
from pruebas.claseTle import Tle, Encuentro
from TleAdmin.get_tle import importar_tle
from visual.trackencuentro import grafica_track


def proc_encuentroSimple(sat_id,deb_id,tca):
    """
    Propaga los objetos involucrados un intervalos [tca-90:tca+20]
    Calcula:
        Miss Distance
        TCA calculado
        Diferencias en RTN ---> Plotea.
        Genera archivo lat, long ---> Plotea.
      
    """
    # Importar los TLE de NORAD.

    usuario='macecilia'
    clave='MaCeciliaSpace17'
    tle_sat=Tle.creadoxParam(usuario, clave, sat_id, tca)
    tle_deb=Tle.creadoxParam(usuario, clave, deb_id, tca)
    
    """
    Propagacion hasta el Encuentro
    """
    encuentro1=Encuentro(tle_sat,tle_deb,tca)

    print 'Minima Distancia = ', encuentro1.mod_minDist,encuentro1.epoca_ini
    grafica_track('../Encuentro/archivos/'+str(sat_id)+'U', '../Encuentro/archivos/'+str(deb_id)+'U')
    print 'fin del procesamiento.'

    
def metodoOSWtles():
    """
     Tanto para el Satelite como para el Desecho:
    
    * Importar Set de TLEs (importar_tle)
    * Implementar OSW con TLEs ---> extrar matriz.
    * 
    
    """
    pass

if __name__ == '__main__':
    
    """
    Codigo principal.
    Inicia el ciclo de procesamiento. 
    -----------------------------------------------------------
    inputs
        sat_id: id NORAD del Satelite (string)
        deb_id: id NORAD del Desecho (String)
        tca: tiempo de maximo acercamiento (datetime)
    """
    

    # Se crean los directorios necesarios.
   
    d1='../TleAdmin/tle'
    if not os.path.exists(d1):
        os.mkdir(d1)
    d2='../AjustarTLE/diferencias'
    if not os.path.exists(d2):
        os.mkdir(d2)
    d3='../main/matrices/'
    if not os.path.exists(d3):
        os.mkdir(d3)
    d4='../visual/archivos/TLE'
    if not os.path.exists(d4):
        os.mkdir(d4)
    d5='../visual/archivos/CODS'
    if not os.path.exists(d5):
        os.mkdir(d5)    
    


    TCA=datetime(2008,1,9,19,1,30,0)
    sat_id='27386' #ENVISAT
    deb_id='15482' #COSMOS

    proc_encuentroSimple(sat_id,deb_id,TCA)
    

    