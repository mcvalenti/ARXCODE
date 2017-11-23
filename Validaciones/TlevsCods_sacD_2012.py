'''
Created on 21 nov. 2017

@author: curso
'''
import os, glob, re
import numpy as np
from datetime import datetime, timedelta
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

    error_file_number=0
    epoca_tle_list=[]
    dx=[]
    dy=[]
    dz=[]
    for f in tle_files[1:3]:
        # TLE data - transformacion al sistema TOD
        tle=Tle.creadoxArchivo(f)
        epoca_tle=tle.epoca()
        r,v=tle.propagaTLE(datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second))
        r_tod=teme2tod(epoca_tle, r)
        date_tle=datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day)
        
        # Busqueda del archivo correspondiente.

        cods_date=date_tle+timedelta(days=2)
        existe_dosmas=cods_date_dic.has_key(cods_date)
        if existe_dosmas:
            nombre_cods=cods_date_dic[cods_date]['nombre']
            ephem_sv = EphemCODS(nombre_cods)
            ephem_dic= ephem_sv.genera_diccionario() 
        else:
            cods_date=date_tle+timedelta(days=1)
            existe_unomas=cods_date_dic.has_key(cods_date)
            if existe_unomas:
                nombre_cods=cods_date_dic[cods_date]['nombre']
                ephem_sv = EphemCODS(nombre_cods)
                ephem_dic= ephem_sv.genera_diccionario()
            else:
                pass

        if ephem_dic.has_key(datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)) :                   
            x=ephem_dic[datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)]['x']
            y=ephem_dic[datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)]['y']
            z=ephem_dic[datetime(epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second)]['z']
            print '======================================================================================'
            print nombre_cods
            print epoca_tle, r_tod
            print epoca_tle.year,epoca_tle.month,epoca_tle.day,epoca_tle.hour,epoca_tle.minute,epoca_tle.second, x, y ,z
            print '======================================================================================'
            epoca_tle_list.append(epoca_tle)
            r_tod_array=np.array(r_tod)
            difx=r_tod_array[0][0]-float(x)
            dify=r_tod_array[0][1]-float(y)
            difz=r_tod_array[0][2]-float(z)
            dx.append(difx) 
            dy.append(dify)
            dz.append(difz)
        else:
            error_file_number=error_file_number+1
        
           
                
    print '======================================================================================' 
    info = 'Proceso finalizado con: '+ str(len(tle_files))+' TLE registrados \n'
    info2 = 'TLE no comparados: '+str(error_file_number)+'\n'     
    print info
    print info2
    
    """
    Grafico
    """   
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    """
    Gestion de Fechas
    """
    date_fmt = '%Y-%m-%d %H:%M:%S.%f'
    epoca=[dt.datetime.strptime(str(i), date_fmt) for i in epoca_tle_list]
    x = [mdates.date2num(i) for i in epoca]
    date_formatter = mdates.DateFormatter('%d/%m')

    ax1.xaxis.set_major_formatter(date_formatter)
    ax2.xaxis.set_major_formatter(date_formatter)
    ax3.xaxis.set_major_formatter(date_formatter)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    
    ax1.set_ylim(-30,30 )
    ax1.set_ylabel('[km]')
    ax1.plot_date(x, dx,'rx',label='X')
    ax2.set_ylim(-20,10)
    ax2.set_ylabel('Diferencias')
    ax2.plot_date(x, dy,'rx',label='Y')
    ax3.set_ylim(-20,20 )
    ax3.set_ylabel('[km]')
    ax3.plot_date(x, dz,'rx',label='Z')

    fig.suptitle('Diferencias posicion del TLE y coordenadas precisas (SAC-D 2012)')
    plt.xlabel('Epoca del TLE [dia/mes]')


    plt.show()
