'''
Created on 26/01/2017

@author: mcvalenti
'''
import os
from datetime import datetime, timedelta
#from pruebas.claseTle import Tle, Encuentro
from TleAdmin.TLE import Tle, SetTLE
#from Encuentro.Encuentro import Encuentro
from Estadistica.matrizOsweiler import calcula_matriz_Tles
from Estadistica.maCovar import EjecutaMaCovar


# def proc_encuentroSimple(sat_id,deb_id,tca):
#     """
#     Propaga los objetos involucrados un intervalos [tca-90:tca+20]
#     Calcula:
#         Miss Distance
#         TCA calculado
#         Diferencias en RTN ---> Plotea.
#         Genera archivo lat, long ---> Plotea.
#       
#     """
#     # Importar los TLE de NORAD.
# 
#     usuario='macecilia'
#     clave='MaCeciliaSpace17'
#     tle_sat=Tle.creadoxParam(usuario, clave, sat_id, tca)
#     tle_deb=Tle.creadoxParam(usuario, clave, deb_id, tca)
#     
#     """
#     Propagacion hasta el Encuentro
#     """
#     encuentro1=Encuentro(tle_sat,tle_deb,tca)
# 
#     print 'Minima Distancia = ', encuentro1.mod_minDist,encuentro1.epoca_ini
#     grafica_track('../Encuentro/archivos/'+str(sat_id)+'U', '../Encuentro/archivos/'+str(deb_id)+'U')
#     print 'fin del procesamiento.'
# 
#     
# def metodoOSWtles():
#     """
#      Tanto para el Satelite como para el Desecho:
#     
#     * Importar Set de TLEs (importar_tle)
#     * Implementar OSW con TLEs ---> extrar matriz.
#     * 
#     
#     """
#     pass

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
    
    TCA=datetime(2008,1,9,19,1,30,0)
    sat_id='27386' #ENVISAT
    deb_id='15482' #COSMOS
    
    """
    Prediccion con 3 dias de aticipacion
    Asumimos que los CDM estaran cargados 3 dias antes del TCA.
    """
    
    tle_sat=Tle.creadoxParam(sat_id, TCA-timedelta(days=3))
    tle_deb=Tle.creadoxParam(deb_id, TCA-timedelta(days=3)) 
 
    #    ENCUENTRO
#     encuentro1=Encuentro(tle_sat,tle_deb,TCA)
#     
#     tca_calculado=encuentro1.tca_c
#     min_distancia=encuentro1.mod_minDist
#     dif_r=encuentro1.DistRic_min[0]
#     dif_t=encuentro1.DistRic_min[1]
#     dif_n=encuentro1.DistRic_min[2] 
#     
#     print '*****************************************************'
#     print '-----------------ENCUENTRO---------------------------'
#     print '*****************************************************'
#     print 'TCA calcualdo = ', tca_calculado
#     print 'Minima Distancia =', min_distancia
#     print 'Distancia en R = ', dif_r 
#     print 'Distancia en T = ', dif_t
#     print 'Distancia en N = ', dif_n

    """
    1 - Calculo la matriz del desecho x OSW.
    2 - Calculo la matriz de la mision x OSW (con TLEs).
    3 - Calculo la matriz de la mision x OSW modificado (TLEs vs CODS).
    4 - Calculo la diferencia de  las matrices 2 y 3.
    5 - Calculo la diferencia en la posicion del ultimo r,v vs dato TLE. 
    """
    
    # 1 - MATRIZ DEL DESECHO (calculada para TCA - 3 dias)
    ini_set_deb=tle_deb.epoca()-timedelta(days=15)
    fin_set_deb=tle_deb.epoca()
    archivo=deb_id+'_'+datetime.strftime(ini_set_deb,'%Y%m%d')+'.crudo'    
    nombre_archivo,var_r,var_t,var_n=calcula_matriz_Tles(deb_id,ini_set_deb,fin_set_deb,archivo)
    maCovar, ma_archivo=EjecutaMaCovar(nombre_archivo)
    
    print '*******************************************************'
    print '-----------------Varianzas DESECHO---------------------------'
    print '*******************************************************'
    print 'Var en R = ', var_r 
    print 'Var en T = ', var_t
    print 'Var en N = ', var_n
    print '*******************************************************'
    print '-----------------Ma. Desecho---------------------------'
    print '*******************************************************'
    for k in maCovar[:3]:
        print k[:3]
        
    # 2 - MATRIZ DE LA MISION (calculada para TCA - 3 dias)
    ini_set_sat=tle_sat.epoca()-timedelta(days=15)
    fin_set_sat=tle_sat.epoca()
    archivo_sat=sat_id+'_'+datetime.strftime(ini_set_sat,'%Y%m%d')+'.crudo'    
    nombre_archivo_sat,var_r_sat,var_t_sat,var_n_sat=calcula_matriz_Tles(sat_id,ini_set_deb,fin_set_deb,archivo_sat)
    maCovar_sat, ma_archivo_sat=EjecutaMaCovar(nombre_archivo_sat)
    
    print '*******************************************************'
    print '-----------------Varianzas MISION---------------------------'
    print '*******************************************************'
    print 'Var en R = ', var_r_sat
    print 'Var en T = ', var_t_sat
    print 'Var en N = ', var_n_sat
    print '*******************************************************'
    print '-----------------Ma. MISION---------------------------'
    print '*******************************************************'
    for k in maCovar_sat[:3]:
        print k[:3]
    

    
    
    # Matriz Combinada
    #var_r,var_t,var_n=encuentro1.calculaMacombinada()
    


    