'''
Created on 12/06/2017
Voy a generar un crudo TLE con tles para el 1 de los meses de
Febrero, Abril, Junio, Agosto y Octubre del anio 2013.
Luego voy a propagar cada TLE por 3 dias (c/1seg) y comparar los resultados con 
los valores que ofrece cods. 
@author: mcvalenti
'''
import os, glob
import numpy as np
from datetime import datetime, timedelta
from TleAdmin.TLE import SetTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difPrimario
from Estadistica.maCovar import EjecutaMaCovar
from pruebas.claseTle import Tle
from CodsAdmin.EphemCODS import EphemCODS
from SistReferencia.sist_deCoordenadas import teme2tod, vncSis
"""
Pasos a seguir
* Bajar de NORAD SET DE 15 DIAS DE TLE finalizando en el 1.
  (los crudos se nombran satId_fechaini_fechafin)
  
* Correr OSW y generar las matrices.

* Tomar el ultimo TLE del SET (Correspondiente al 1 del mes)
* Importar el archivo CODS con la fecha del dia 3 del mes.
* Comparar segundo a segundo inicializando en 0. 
* Calcular la matriz que resulta. - Map_mes

"""
def procesar(sat_id,archivo_crudo_tle):
    """
    Invoca a la funcion setTLE, para fragmentar
    cada uno de los TLE del dato crudo en archivos
    individuales; y los guarda en: TleAdmin/tle
    """
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
    if os.stat('../TleAdmin/crudosTLE/'+archivo_crudo_tle).st_size == 0:
        print('El archivo esta vacio')
    SetTLE(sat_id,archivo_crudo_tle )
    lista_tles=glob.glob('../TleAdmin/tle/*')
    cant_tles=len(lista_tles)
    """
    Ordenamiento de los TLEs
    """
    tledic=generadorDatos(lista_tles)
    tleOrdenados=ordenaTles(tledic)
    """
    Impresiones de info de TLEs.
    """
    print 'PROCESAMIENTO DE TLE'
    print '-----------------------------------------------------'
    print 'TLE PRIMARIO'
    print '-----------------------------------------------------'
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tleOrdenados[-1][0])
    linea1= tle_primario.linea1
    linea2= tle_primario.linea2
    fin_tle=tle_primario.epoca()
#    ffin=fin_tle.strftime('%Y-%m-%d %H:%M:%S.%f' )
    print linea1
    print linea2
    print '-----------------------------------------------------'
    print 'TLE INICIAL DEL SET'
    print '-----------------------------------------------------'
    tle_inial = Tle.creadoxArchivo('../TleAdmin/tle/'+tleOrdenados[0][0])
    linea1_0= tle_inial.linea1
    linea2_0= tle_inial.linea2
#    ini_tle=tle_inial.epoca()
    print linea1_0
    print linea2_0
    print '-----------------------------------------------------'
    """
    PROCESAMIENTO.
    """
    files=glob.glob('../AjustarTLE/diferencias/*')
    for filename in files:
        os.unlink(filename)
    set_pri=difPrimario(tleOrdenados, cant_tles)
    nombre_archivo=set_pri[3]
    """
    Ma. de Covarianza
    """
    macovarT, arch_macovar=EjecutaMaCovar(nombre_archivo)
    print '================================================='
    print '        Ma. de Covarianza                '
    print '================================================='
    for k in macovarT[:3]:
        for j in k[:3]:
            print j,
        print
#    print macovarT
    tle_dia1 = Tle.creadoxArchivo('../TleAdmin/tle/'+tleOrdenados[-3][0])
    print 'Fin del Procesamiento'
    return tle_primario, tle_dia1

if __name__=='__main__':
    """
    Ma de Osweiler
    """
    # validacion 
#     sat_id='27642'
#     archivo_crudo_tle='27642_escenario51'
    #SAC-D
    sat_id='37673'
    #1 Junio
#     archivo_crudo_tle='37673_20130518_20130604.tle'
#     archivo_crudo_cods='CODS_20130604_135818_SACD_DENSEPHEM_TOD_XYZ_O.TXT'
    #2 julio
#     archivo_crudo_tle='37673_20130620_20130704.tle'
#     archivo_crudo_cods='CODS_20130704_135823_SACD_DENSEPHEM_TOD_XYZ_O.TXT'
    #3 Agosto
    archivo_crudo_tle='37673_20130721_20130804.tle'
    archivo_crudo_cods='CODS_20130804_135714_SACD_DENSEPHEM_TOD_XYZ_O.TXT'
    #4 Septiembre
#    archivo_crudo_tle='37673_20130821_20130904.tle'
    #5 Octubre
#    archivo_crudo_tle='37673_20130920_20131004.tle'
    #6 Noviembre
#    archivo_crudo_tle='37673_20131021_20131104.tle'
    #7 Diciembre
#    archivo_crudo_tle='37673_20131120_20131204.tle'
    #8 Enero
#    archivo_crudo_tle='37673_20131221_20140104.tle'
    #9 Febrero
#    archivo_crudo_tle='37673_20140121_20140204.tle' 
    #10 Marzo
#    archivo_crudo_tle='37673_20140218_20130304.tle'
    #11 Abril
#    archivo_crudo_tle='37673_20140321_20140404.tle'
    #12 Mayo
#    archivo_crudo_tle='37673_20140420_20140504.tle'
    #13 Junio  
#    archivo_crudo_tle='37673_20140521_20140604.tle'
    tle_primario, tle_dia1= procesar(sat_id,archivo_crudo_tle)
    print 'Fecha del TLE del dia 1: ', tle_dia1.epoca()
    """
    Comparacion con CODS
    """
    ephem=EphemCODS('../CodsAdmin/sacDdensos/'+archivo_crudo_cods)   
    ephem_dic=ephem.genera_diccionario()
    # Propago el TLE del dia 1. 
    anio=tle_dia1.epoca.year
    mes=tle_dia1.epoca.month
    epoca_ini_prop=datetime(anio,mes,3,0,0,0)
    epoca_fin_prop=epoca_ini_prop+timedelta(days=1)
    dif_r=[]
    dif_v=[]
    dif_n=[]
    dif_c=[]
    while epoca_ini_prop < epoca_fin_prop:
        #propago
        r,v = tle_dia1.propagaTLE(epoca_ini_prop)
        r_tod = teme2tod(epoca_ini_prop,r)        
        #extraigo datos cods
        x=ephem_dic[epoca_ini_prop]['x']
        y=ephem_dic[epoca_ini_prop]['y']
        z=ephem_dic[epoca_ini_prop]['z']
        vx=ephem_dic[epoca_ini_prop]['vx']
        vy=ephem_dic[epoca_ini_prop]['vy']
        vz=ephem_dic[epoca_ini_prop]['vz']
        r_cods=np.array([float(x),float(y),float(z)])
        v_cods=np.array([float(vx),float(vy),float(vz)])
      
        resta=r_cods[0]-r_tod.item(0),r_cods[1]-r_tod.item(1),r_cods[2]-r_tod.item(2)
        v,n,c=vncSis(r_cods,v_cods,resta)
          
        dif_r.append(resta)
        dif_v.append(v)
        dif_n.append(n)
        dif_c.append(c)
          
        epoca_ini_prop=epoca_ini_prop+timedelta(seconds=1)
      
    print 'Promedio de dv = ', np.mean(dif_v), np.var(dif_v)
    print 'Promedio de dn = ', np.mean(dif_n), np.var(dif_n)
    print 'Promedio de dc = ', np.mean(dif_c), np.var(dif_c)

