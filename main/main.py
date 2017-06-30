'''
Created on 26/01/2017

@author: mcvalenti
'''
import os
import numpy as np
from scipy.integrate import quad, dblquad
from datetime import datetime, timedelta
from Aplicacion.globals import tabla
from TleAdmin.TLE import Tle, SetTLE
from Encuentro.Encuentro import Encuentro
from Estadistica.matrizOsweiler import calcula_matriz_Tles, calcula_matriz_OSWcorregido
from Comparar.TlevsCodsOSW import ejecutaProcesamientoCods
from Estadistica.maCovar import EjecutaMaCovar, EjecutaMaCovarCODS


if __name__ == '__main__':
    """
    Codigo principal.
    Inicia el ciclo de procesamiento. 
    -----------------------------------------------------------
    inputs (ya sea x CDM o por metodo manual)
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
    """
    Estos procedimientos deben estar en la GUI. 
    """
    TCA=datetime(2004,9,2,19,14,11,0)
    sat_id='27386' #ENVISAT
    deb_id='12442' #COSMOS
#     TCA=datetime(2008,1,9,19,1,30,0)
#     sat_id='27386' #ENVISAT
#     deb_id='15482' #COSMOS
#     TCA=datetime(2013,1,1)
#     sat_id='37673' #SAC-D  
#     deb_id='15482' #COSMOS
    """
    Prediccion con n dias de aticipacion
    """
    n=0 # x ejemplo para un CDM que llega 72 hs antes.
    #===========================================================
    # Satelite
    #===========================================================
    tle_sat=Tle.creadoxParam(sat_id, TCA-timedelta(days=n))
    #===========================================================
    # Desecho
    #===========================================================
    tle_deb=Tle.creadoxParam(deb_id, TCA-timedelta(days=n)) 
    #===========================================================
    #    ENCUENTRO
    #===========================================================
    encuentro1=Encuentro(tle_sat,tle_deb,TCA,n)    
    tca_calculado=encuentro1.tca_c
    min_distancia=encuentro1.mod_minDist
    dif_r=encuentro1.DistRic_min[0]
    dif_t=encuentro1.DistRic_min[1]
    dif_n=encuentro1.DistRic_min[2] 
    #Calculo el angulo entre los vectores velocidad.
#     v_sat=encuentro1.vel_sat_tca
#     v_deb=encuentro1.vel_deb_tca
#     cos_phi=np.dot(v_sat,v_deb)/(np.sqrt(np.dot(v_sat,v_sat))*np.sqrt(np.dot(v_deb,v_deb)))
#     phi=np.arccos(cos_phi)
         
    print '*****************************************************'
    print '-----------------ENCUENTRO---------------------------'
    print '*****************************************************'
    print 'TCA calcualdo = ', tca_calculado
    print 'Minima Distancia =', min_distancia
    print 'Distancia en R = ', dif_r 
    print 'Distancia en T = ', dif_t
    print 'Distancia en N = ', dif_n
    #===========================================================
    # Matriz Combinada
    #===========================================================
    matriz_combinada=encuentro1.calculaMacombinada()
    print '*****************************************************'
    print '-----------------Matriz COMBINADA--------------------'
    print '*****************************************************'    
    for k in matriz_combinada[:3]:
        print k[:3]
    #===========================================================
    # PoC
    #===========================================================
#      
#     mu_x=dif_r
#     mu_y=np.sqrt(dif_t*dif_t+dif_n*dif_n)
# 
#     var_s=matriz_combinada[1][1]
#     var_w=matriz_combinada[2][2]
#     
#     var_x=matriz_combinada[0][0]
#     var_y=var_s*np.cos(phi/2.0)*np.cos(phi/2.0)+var_w*np.sin(phi/2.0)*np.sin(phi/2.0)
# 
#     ra=0.01
#     PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/var_x)+(mu_y*mu_y/var_y)))*(1-np.exp(-ra/(2*np.sqrt(var_x)*np.sqrt(var_y))))
#    PoC=dblquad(lambda y, x: (1.0/(2.0*np.pi*np.sqrt(var_x)*np.sqrt(var_y)))*np.exp((-1.0/2.0)*((x*x/var_x)+(y*y/var_y))), mu_x-ra, mu_x+ra, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)
    PoC=encuentro1.calculaPoC_circ()
    print '======================================================'
    print 'PoC = ', PoC
    print '======================================================'
    