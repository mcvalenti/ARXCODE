'''
Created on 21 nov. 2017

@author: curso
'''
import os, glob, re
from datetime import datetime, timedelta
from TleAdmin.TLE import Tle
from SistReferencia.sist_deCoordenadas import teme2tod
from CodsAdmin.EphemCODS import EphemCODS

def divide_setTLE(noradId,archivo):
    """
    Obtiene un dato con un listado de TLEs para todo un intervalo temporal.
    El mismo es para un satelite en particular.
    Esta funcion particiona el archivo en muchos archivos, uno por cada tle.
    Y los guarda en TleAdmin/tle
    """
    ruta_tle = r'../TleAdmin/tle_sacD_2012/' 
    if not os.path.exists(ruta_tle): os.makedirs(ruta_tle)
    
    files=glob.glob('../TleAdmin/tle_sacD_2012/*')
    for filename in files:
        os.unlink(filename)
    
    lista=open('../TleAdmin/crudosTLE/'+archivo,'r')
    filas=lista.readlines()
    largo=len(filas) # indicara la cantidad total de lineas
        
    
    m=0
    for i in range(0,largo-1,2):
        salida=open('../TleAdmin/tle_sacD_2012/'+noradId+'tle'+str(m),'w+')
        linea1=filas[i]
        linea2=filas[i+1]
        doslineas=linea1+linea2
        salida.write(doslineas)
        m=m+1
        salida.close()
        
if __name__=='__main__':
#    divide_setTLE('37673', 'sacD_2012')
    """
    TleAdmin/tle_sacD_2012 contiene todos los TLE del sac D del annio 2012.
    Los mismos deben ser comparados con las efemerides precisas de cods correspondientes
    a las mismas fechas y horarios y las difrencias deben ser graficadas. 
    """
    tle_files=glob.glob('../TleAdmin/tle_sacD_2012/*')
    cods_files=glob.glob('../CodsAdmin/CUSS_CODS/DENSEPHEM_2012/*.TXT')
    
    cods_dates=[]
    cods_date_dic={}
    for fcods in cods_files:
        campos=fcods.split('/')
        ephem=EphemCODS(campos[4])
        y_cods, mon_cods, d_cods, hs_cods, min_cods, sec_cods = ephem.parsea_epoca_nombre()
        cods_date_dic[datetime(int(y_cods), int(mon_cods),int(d_cods))]={'nombre':fcods}
        cods_dates.append(datetime(int(y_cods), int(mon_cods),int(d_cods)))

    cn=0
    for f in tle_files:
        # TLE data - transformacion al sistema TOD
        tle=Tle.creadoxArchivo(f)
        epoca_tle=tle.epoca()
        r,v=tle.propagaTLE()
        r_tod=teme2tod(epoca_tle, r)
        date_tle=datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day)        
         
        for cd in cods_dates:
            if cd == date_tle:                
                nombre_cods=cods_date_dic[cd]['nombre']
                ephem_sv = EphemCODS(nombre_cods)
                ephem_dic= ephem_sv.genera_diccionario() 
                exite=ephem_dic.has_key(datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)) 
                if exite:
                    pass
                else:
                    cd1=cd+timedelta(days=1) 
                    nombre_cods=cods_date_dic[cd1]['nombre']
                    ephem_sv = EphemCODS(nombre_cods)
                    ephem_dic= ephem_sv.genera_diccionario() 
                    existe=ephem_dic.has_key(datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second))
                    if exite:
                        pass
                    else:
                        cd2=cd+timedelta(days=2) 
                        nombre_cods=cods_date_dic[cd2]['nombre']
                        ephem_sv = EphemCODS(nombre_cods)
                        ephem_dic= ephem_sv.genera_diccionario() 
                        existe=ephem_dic.has_key(datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second))
                            
                x=ephem_dic[datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)]['x']
                y=ephem_dic[datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)]['y']
                z=ephem_dic[datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)]['z']
                print '======================================================================================'
                print nombre_cods
                print epoca_tle, r_tod
                print epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second, x, y ,z
                print '======================================================================================'
                
                
                
    print 'FIN'
