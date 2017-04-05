'''
Created on 23/01/2017

@author: mcvalenti
'''
import os, glob, csv
import numpy as np
from datetime import datetime


def sigmaCalcCODS(x_vect,y_vect):
    """
    --------------------------------------------------------------------------------------
    Calcula el cuadrado de la varianza - sigma2 y las varianzas cruzadas.
    --------------------------------------------------------------------------------------
    inputs
        x_vect: contiene las diferencias tomando como valor esperado el valor CODS. (vect)
        y_vect: contiene las diferencias tomando como valor esperado el valor CODS. (vect)
    output
        sigma2: varianza al cuadrado (float)
    """
    y_vect=np.transpose(y_vect)
    prod=np.dot(x_vect,y_vect)
    l=len(x_vect)
    sigma2=prod/l
    
    return sigma2

def maCovCODS(uu,vv,ww,uvel,vvel,wvel):
    """
    Sigma Posiciones
    """
    s2_uu=sigmaCalcCODS(uu,uu)
    s2_uv=sigmaCalcCODS(uu,vv)
    s2_uw=sigmaCalcCODS(uu,ww)
    s2_vv=sigmaCalcCODS(vv,vv)
    s2_vw=sigmaCalcCODS(vv,ww)
    s2_ww=sigmaCalcCODS(ww,ww)
    """
    Sigma Velocidades
    """
    s2_uvel=sigmaCalcCODS(uvel,uvel)
    s2_uvvel=sigmaCalcCODS(uvel,vvel)
    s2_uwvel=sigmaCalcCODS(uvel,wvel)
    s2_vvvel=sigmaCalcCODS(vvel,vvel)
    s2_vwvel=sigmaCalcCODS(vvel,wvel)
    s2_wwvel=sigmaCalcCODS(wvel,wvel)
    """
    Sigmas de Pos y Vel - cruzados
    """
    s2_uuvel=sigmaCalcCODS(uu,uvel)
    s2_uuvvel=sigmaCalcCODS(uu,vvel)
    s2_uuwvel=sigmaCalcCODS(uu,wvel)
    s2_vvuvel=sigmaCalcCODS(vv,uvel)
    s2_vvvvel=sigmaCalcCODS(vv,vvel)
    s2_vvwvel=sigmaCalcCODS(vv,wvel)
    s2_wwuvel=sigmaCalcCODS(ww,uvel)
    s2_wwvvel=sigmaCalcCODS(ww,vvel)
    s2_wwwvel=sigmaCalcCODS(ww,wvel)
    
    linea1=[s2_uu,s2_uv,s2_uw,s2_uuvel,s2_uuvvel,s2_uuwvel]
    linea2=[s2_uv,s2_vv,s2_vw,s2_vvuvel,s2_vvvvel,s2_vvwvel]
    linea3=[s2_uw,s2_vw,s2_ww,s2_wwuvel,s2_wwvvel,s2_wwwvel]
    linea4=[s2_uuvel,s2_uuvvel,s2_uuwvel,s2_uvel,s2_uvvel,s2_uwvel]
    linea5=[s2_vvuvel,s2_vvvvel,s2_vvwvel,s2_uvvel,s2_vvvel,s2_vwvel,]
    linea6=[s2_wwuvel,s2_wwvvel,s2_wwwvel,s2_uwvel,s2_vwvel,s2_wwvel]        
    maCovarC=np.array([linea1,linea2,linea3,linea4,linea5,linea6])
      
    return maCovarC

def maCovTLE(u, v, w, uv, vv, wv):
    m_u=np.mean(u)
    m_v=np.mean(v)
    m_w=np.mean(w)
    m_uv=np.mean(uv)
    m_vv=np.mean(vv)
    m_wv=np.mean(wv)
    uu=[]
    vx=[]
    ww=[]
    uvuv=[]
    vvvv=[]
    wvwv=[]
    for i in range(len(u)):
        uu.append(u[i]-m_u)
        vx.append(v[i]-m_v)
        ww.append(w[i]-m_w)
        uvuv.append(uv[i]-m_uv)
        vvvv.append(vv[i]-m_vv)
        wvwv.append(wv[i]-m_wv)
        
    maCovarT=maCovCODS(uu,vx,ww,uvuv,vvvv,wvwv)
    
    return maCovarT   


def EjecutaMaCovar(archivo):
#     files=glob.glob('../main/matrices/*')
#     for filename in files:
#         os.unlink(filename)
#    datoTipo=raw_input()
    u=[]
    v=[]
    w=[]
    uv=[]
    vv=[]
    wv=[]
    datos=open('../AjustarTLE/diferencias/'+archivo,'r')
    datos1=datos.readlines()
    for l in datos1:
        campos=l.split()
        dt=l[:19]
        dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
        u.append(float(campos[2]))
        v.append(float(campos[3]))
        w.append(float(campos[4]))
        uv.append(float(campos[5]))
        vv.append(float(campos[6]))
        wv.append(float(campos[7]))
    maCovar=maCovTLE(u, v, w, uv, vv, wv)
    
    ma_archivo=str(archivo.split('.')[0])+'_tle.csv'
    csvsalida = open('../main/matrices/'+ma_archivo, 'w')
    salida = csv.writer(csvsalida)
    salida.writerows(maCovar)
    
    return maCovar, ma_archivo

def EjecutaMaCovarCODS(archivo):
#     files=glob.glob('../main/matrices/*')
#     for filename in files:
#         os.unlink(filename)
    u=[]
    v=[]
    w=[]
    uv=[]
    vv=[]
    wv=[]
    datos=open('../Comparar/diferencias/'+archivo,'r')
    datos1=datos.readlines()
    for l in datos1:
        campos=l.split()
        dt=l[:19]
        dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
        u.append(float(campos[2]))
        v.append(float(campos[3]))
        w.append(float(campos[4]))
        uv.append(float(campos[5]))
        vv.append(float(campos[6]))
        wv.append(float(campos[7]))
    maCovar=maCovTLE(u, v, w, uv, vv, wv)
    
    
    csvsalida = open('../main/matrices/'+archivo.split('.')[0]+'_cods.csv', 'w')
    salida = csv.writer(csvsalida)
    salida.writerows(maCovar)
    
#     print 'Ma. de Covarianza de: ', archivo    
#     print maCovar
    
    return maCovar
    
    