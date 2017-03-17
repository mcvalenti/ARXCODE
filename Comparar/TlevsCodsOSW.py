'''
Created on 16/03/2017

@author: mcvalenti
'''

import os, glob
import numpy as np
from datetime import datetime, timedelta
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TLE import Tle
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from Comparar.TleVsCods import interpola, encuentraBordes
from SistReferencia.sist_deCoordenadas import vncSis
from visual.CodsOsweiler import VerGrafico
from CodsAdmin.EphemCODS import EphemCODS


def FiltraArchivos(tle):
    """
    Extrae la fecha del TLE y busca los
    archivos CODS que podrian contener la fecha necesaria.
    Ordena los archivos CODS y se queda con el dato mas actualizado
    para realizar la interpolacion.
    ----------------------------------------------------------------
    input
        tle: nombre del archivo del TLE a procesar (String)
    output
        lineainterpol: Linea CODS interpolada correspondiente a la fecha del TLE. (String)
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
    print 'Procesando ...'
    for i in tles:
        tle1=Tle(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        fila=str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
        inferior, superior= encuentraBordes(gpslista,fila)
        lineaInterpol.append(interpola(fila,inferior,superior))
    return lineaInterpol

def interpola_3sv(tle,arch3_cods):
    tle1=Tle(tle)
    fecha=tle1.epoca()
    r,v=tle1.propagaTLE()
    fila=str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
    print 'Epoca del TLE = ',fecha
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
            fecha=c[:19]
            d=datetime.strptime(fecha,'%Y/%m/%d %H:%M:%S')
            lista_epocas.append(d)
        if fecha_minutos in lista_epocas and m==0:
            indice = lista_epocas.index(fecha_minutos)
            inferior = contenido[indice+1]
            superior = contenido[indice+2]
            print inferior
            print superior
            m=m+1
            
    linea_interpol=interpola(fila,inferior,superior)
    
    return linea_interpol

def diferencias_tleCODS(tles,linea_interpol):
    archivo = 'codsOsweiler.dif'
    salida=open(archivo,'w')
    fecha=linea_interpol[:19]
    d=datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S')
    r=np.array([float(linea_interpol.split()[2]),float(linea_interpol.split()[3]),float(linea_interpol.split()[4])])
    rp=np.array([float(linea_interpol.split()[5]),float(linea_interpol.split()[6]),float(linea_interpol.split()[7])])
    item=range(0,len(tle_ordenados)-1)
    whichconst=wgs72
    for j in item:
        tle0=Tle('../TleAdmin/tle/'+tle_ordenados[j][0])
        fecha_tle=tle0.epoca()
        line1=tle0.linea1
        line2=tle0.linea2
        satrec = twoline2rv(line1, line2, whichconst)
        pos, vel=satrec.propagate(d.year, d.month, d.day,d.hour, d.minute, d.second)
        difx=[float(pos[0])-r[0],float(pos[1])-r[1],float(pos[2])-r[2]]
        difv=[float(vel[0])-rp[0],float(vel[1])-rp[1],float(vel[2])-rp[2]]
        v,n,c=vncSis(r,rp,difx)
        vv,nn,cc=vncSis(r,rp,difv)
        dato=str(fecha_tle)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+'\n'
        salida.write(dato)
    salida.close()
    return archivo
        

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

    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
    arch3_cods=FiltraArchivos('../TleAdmin/tle/'+tle_ordenados[-1][0])
    linea_interpol=interpola_3sv('../TleAdmin/tle/'+tle_ordenados[-1][0], arch3_cods)
    print linea_interpol
    print '*****************************************************************'
    
    archivo_diferencias = diferencias_tleCODS(tle_ordenados, linea_interpol)
    print archivo_diferencias
    
    VerGrafico(archivo_diferencias)

    print 'FIN'
    
    """
    Procedimiento iterativo para el TLE primario.
    """
    
#     sv_interp=sv_interpolados(tles)
#     
#     """
#     cods_dic={}
#     fecha_int=[]
#     m=0
#     for li in sv_interp:
#         nombre='ephem_'+str(m)
#         fecha=li[:19]
#         fecha1=datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
# #        fecha_int.append(fecha1) # ejecuta un metodo de la clase TLE
#         cods_dic[fecha1]= li[19:]
#         m=m+1
#     cods_dic_ord=sorted(cods_dic.items(), reverse=True)
# 
#     print cods_dic_ord
#    
#  
#     date_fmt = '%Y-%m-%d %H:%M:%S'
#     whichconst=wgs72
#      
#     m=0
#     for k in cods_dic_ord:   
#         fecha=k[0] 
#         sv=k[1]
#         r=np.array([float(sv.split()[0]),float(sv.split()[1]),float(sv.split()[2])])
#         rp=np.array([float(sv.split()[3]),float(sv.split()[4]),float(sv.split()[5])])
#         item=range(0,len(tle_ordenados))
#         for j in item:
#             tle0=Tle('../TleAdmin/tle/'+tle_ordenados[j][0])
#             fecha_tle=tle0.epoca()
#             if fecha_tle <= fecha:
#                 line1=tle0.linea1
#                 line2=tle0.linea2
#                 satrec = twoline2rv(line1, line2, whichconst)
#                 pos, vel=satrec.propagate(fecha.year, fecha.month, fecha.day, fecha.hour, fecha.minute, fecha.second)
#                 difx=[float(pos[0])-r[0],float(pos[1])-r[1],float(pos[2])-r[2]]
#                 difv=[float(vel[0])-rp[0],float(vel[1])-rp[1],float(vel[2])-rp[2]]
#                 v,n,c=vncSis(r,rp,difx)
#                 vv,nn,cc=vncSis(r,rp,difv)
#                 dato=str(fecha_tle)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+'\n'
#                 if m < len(cods_dic_ord):
#                     salida.write(dato)
#                 m=m+1
#                 
#     salida.close()           
#     VerGrafico('codsOsweiler.dif')