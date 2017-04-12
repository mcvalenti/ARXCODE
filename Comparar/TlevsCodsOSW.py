'''
Created on 16/03/2017

@author: mcvalenti
'''

import os, glob
import numpy as np
import numpy.polynomial as P
from datetime import datetime, timedelta
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TLE import Tle
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from Comparar.TleVsCods import interpola, encuentraBordes
from SistReferencia.sist_deCoordenadas import vncSis, teme2tod
from CodsAdmin.EphemCODS import EphemCODS
from Estadistica.ajusteMinCuad import ajustar_diferencias

def FiltraArchivos(tle):
    """
    Extrae la fecha del TLE y busca los
    archivos CODS que podrian contener la fecha necesaria.
    Toma el nombre del archivo cuyo nombre contiene la fecha el TLE
    primario y agrega a su vez el nombre de los proximos 3 archivos
    ya que tambien contendran esa fecha y con valores mas actualizados.
    ----------------------------------------------------------------
    input
        tle: nombre del archivo del TLE a procesar (String)
    output
        archivos_datos: nombres de los archivos CODS que contienen la fecha
                        del TLE primario - (Lista)
    """
    tle1=Tle(tle)
    fecha=tle1.epoca()
    fechas_busqueda=[datetime(fecha.year,fecha.month,fecha.day)+timedelta(days=2),
                     datetime(fecha.year,fecha.month,fecha.day)+timedelta(days=1),
                     datetime(fecha.year,fecha.month,fecha.day)]
    
    nombre_archivos = glob.glob('../CodsAdmin/TOD_O/*')
    lista_fechas=[]
    archivos_datos=[]
    for nom in nombre_archivos:        
        e_CODS=EphemCODS(nom.split('/')[-1])
        anio, mes, dia, hora, minu, seg = EphemCODS.parsea_epoca(e_CODS)
        fecha_cods_nombre=datetime(int(anio),int(mes),int(dia))
        lista_fechas.append(fecha_cods_nombre)

    for f in fechas_busqueda:
        indice = lista_fechas.index(f)
        archivos_datos.append(nombre_archivos[indice])
        
    return archivos_datos

def sv_interpolados(tles):
    """
    Arma la lista de TLEs y busca los valores
    del Vector de Estado de CODS interpolado para las fechas
    correspondientes a los TLEs. 
    """
    gpsf=open('../CodsAdmin/TOD_O/TOD_CODS_SACD_xyz.txt','r')
    gpslista=gpsf.readlines()
    lineaInterpol=[]
    for i in tles:
        tle1=Tle(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        fila=str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
        inferior, superior= encuentraBordes(gpslista,fila)
        lineaInterpol.append(interpola(fila,inferior,superior))
    return lineaInterpol

def interpola_3sv(tle,arch3_cods):
    """
    Extrale del tle primario la epoca y luego busca entre los archivos
    CODS cual de los mas actualizados contiene la epoca del TLE.
    Luego interpola los valores de CODS para la epoca del TLE 
    y devuelve el vector de estado interpolado correspondiente a la epoca.
    ----------------------------------------------------------------------------------------
    input
        tle: nombre del archivo del TLE primario (String)
        arch3_cods: nombre de los archivos CODS que contienen la epoca del TLE. (Lista)
    output
        linea_interpol: linea con el vector de estado interpolado a la epoca del TLE. (String)
    """
    tle1=Tle(tle)
    fecha=tle1.epoca()
    r,v=tle1.propagaTLE()
    fila=str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
    fecha_minutos = datetime(int(fecha.year),int(fecha.month),int(fecha.day),int(fecha.hour),int(fecha.minute),0)

    m=0
    for arch in arch3_cods:
        a=open(arch,'r')
        contenido = a.readlines()
        lista_epocas=[]
        for c in contenido:
            c1=c.split(' ')
            if c1[0]=='*HEADER':
                continue
            fecha=c[:16]
            hr=fecha[11:13]
            if hr != '24':
                d=datetime.strptime(fecha,'%Y/%m/%d %H:%M')
            lista_epocas.append(d)
        if fecha_minutos in lista_epocas and m==0:
            indice = lista_epocas.index(fecha_minutos)
            inferior = contenido[indice+1]
            superior = contenido[indice+2]
            m=m+1            
    linea_interpol=interpola(fila,inferior,superior)    
    return linea_interpol

def diferencias_tleCODS(salida,tles,linea_interpol,data):
    """
    Toma la lista de archivos TLEs y propaga cada uno hasta la epoca de la
    linea interpolada. Luego compara los valores de las coordenadas propagadas
    con los valores de la linea interpolada y genera las diferencias. 
    Imprime los resultados en el archivo salida.     
    ----------------------------------------------------------------------------------------------------------
    input
        salida: archivo donde se escribe (Instancia de apertura de archivo)
        tles: lista de nombres de archivos tle (diccionario)
        linea_interpol: Linea interpolada de los datos CODS para la epoca del TLE primario. (String)
    output
        difTot_satId_fini_ffin.cods: Archivo con todas las diferencias ('../Comparar/diferencias/')
    """
    fecha=linea_interpol[:26]
    d=datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S.%f')
    r=np.array([float(linea_interpol.split()[2]),float(linea_interpol.split()[3]),float(linea_interpol.split()[4])])
    rp=np.array([float(linea_interpol.split()[5]),float(linea_interpol.split()[6]),float(linea_interpol.split()[7])])
    item=range(0,len(tles))
    whichconst=wgs72
    for j in item:
        tle0=Tle('../TleAdmin/tle/'+tles[j][0])
        fecha_tle=tle0.epoca()
        if fecha_tle <= d:
            line1=tle0.linea1
            line2=tle0.linea2
            satrec = twoline2rv(line1, line2, whichconst)
            pos1, vel1=satrec.propagate(d.year, d.month, d.day,d.hour, d.minute, d.second)
            pos=teme2tod(fecha_tle, pos1)
            vel=teme2tod(fecha_tle, vel1)
            difx=[pos[0,0]-r[0],pos[0,1]-r[1],pos[0,2]-r[2]]
            difv=[vel[0,0]-rp[0],vel[0,1]-rp[1],vel[0,2]-rp[2]]
            v,n,c=vncSis(r,rp,difx)
            vv,nn,cc=vncSis(r,rp,difv)
            dato=str(fecha_tle)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+'\n'
            salida.write(dato)
            data[0].append(fecha_tle)
            data[1].append(v)
            data[2].append(n)
            data[3].append(c)
            data[4].append(vv)
            data[5].append(nn)
            data[6].append(cc)
    return data

# def ajustar_diferencias(data):
#     
#     t=data[0]
#     dt=[]
#     dv=data[1]
#     dn=data[2]
#     dc=data[3]
#     dvv=data[4]
#     dnn=data[5]
#     dcc=data[6]
#     
#     for kt in t:
#         dt.append((kt-t[0]).total_seconds()/86400.0)
#     c, b, a = P.polynomial.polyfit(dt, dv, deg=2)
#     c1, b1, a1 = P.polynomial.polyfit(dt, dn, deg=2)
#     c2, b2, a2 = P.polynomial.polyfit(dt, dc, deg=2)
#     coef=[a,b,c,a1,b1,c1,a2,b2,c2]
# 
#     return dt,coef
        
def ejecutaProcesamientoCods():
#if __name__ == '__main__':
    """
    Lista los nombres de los archivos de la carpeta: TleAdmin/tles.
    Recupera la informacion del ultimo TLE del set (TLE primario), en particular la epoca.
    Busca entre los archivos de CODS, la epoca coincidente con la epoca del TLE primario.
    Interpola para la fecha al nivel del segundo. 
    Luego propaga todos los TLEs del set a la epoca del CODS interpolado y calcular las 
    diferencias. 
    ---------------------------------------------------------------------------------------
    Nota! LOS DATOS CODS SON SOLO DE LA MISION SAC-D.
    Luego los tles, previamente procesados y archivados en la carpeta de TleAdmin/tles, deben
    corresponderse con esa mision.
    """

    print 'Procesando datos CODS...'
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
    """
    Impresiones de info de TLEs.
    """
    tle_inicio = Tle('../TleAdmin/tle/'+tle_ordenados[0][0])
    cat_id = tle_inicio.catID()
    epoca_ini = tle_inicio.epoca()
    
    tle_primario = Tle('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_fin  = tle_primario.epoca()
    epoca_ffin = epoca_fin
    linea1 = tle_primario.linea1
    linea2 = tle_primario.linea2
    fecha_ini=str(epoca_ini.year)+str(epoca_ini.month)+str(epoca_ini.day)
    fecha_fin=str(epoca_fin.year)+str(epoca_fin.month)+str(epoca_fin.day)
    print '------------------------------------------------------------------------'
    print '-------------------------TLE PRIMARIO-----------------------------------'
    print linea1
    print linea2
    print epoca_ffin
    print '------------------------------------------------------------------------'
    t=[]
    dv=[]
    du=[]
    dc=[]
    dvv=[]
    dnn=[]
    dcc=[]
    data=[t,dv,du,dc,dvv,dnn,dcc]
    archivo = cat_id+'_'+fecha_ini+'_'+fecha_fin+'.cods'    
    salida=open('../Comparar/diferencias/difTot_'+archivo,'w')
    salida1=open('../Comparar/diferencias/'+archivo,'w')
    for m in range(len(tle_ordenados)-1,0,-1):
        tle_primario = Tle('../TleAdmin/tle/'+tle_ordenados[m][0])
        epoca_fin = tle_primario.epoca()
        arch3_cods=FiltraArchivos('../TleAdmin/tle/'+tle_ordenados[m][0])
        linea_interpol=interpola_3sv('../TleAdmin/tle/'+tle_ordenados[m][0], arch3_cods)                   
        data=diferencias_tleCODS(salida,tle_ordenados, linea_interpol,data)
        if m == len(tle_ordenados)-1:
            for k in range(len(data[0])):
                info = data[0][k].strftime("%Y-%m-%d %H:%M:%S.%f")+' '+str(data[1][k])+' '+str(data[2][k])+' '+str(data[3][k])+' '+str(data[4][k])+' '+str(data[5][k])+' '+str(data[6][k])+'\n'
                salida1.write(info)
    salida1.close()
    
    dt,coef=ajustar_diferencias(epoca_ffin,data,2)

    print 'DIFERENCIAS:'
    print '-------------------------TLE PRIMARIO-----------------------------------'
    print 'dv =',data[1][25]
    print 'dn =',data[2][25]
    print 'dc =',data[3][25]
    print '-------------------------TLE PRIMARIO-----------------------------------'
    print 'Fin del Calculo de Diferencias'

    set_datos=[str(cat_id),linea1,linea2,epoca_ini.strftime("%Y-%m-%d %H:%M:%S.%f"),epoca_ffin.strftime("%Y-%m-%d %H:%M:%S.%f"),dt,data,coef,archivo]
    return set_datos

