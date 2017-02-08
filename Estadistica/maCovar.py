'''
Created on 23/01/2017

@author: mcvalenti
'''
import csv
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

def maCovCODS(u,v,w):
    s2_uu=sigmaCalcCODS(u,u)
    s2_uv=sigmaCalcCODS(u,v)
    s2_uw=sigmaCalcCODS(u,w)
    s2_vv=sigmaCalcCODS(v,v)
    s2_vw=sigmaCalcCODS(v,w)
    s2_ww=sigmaCalcCODS(w,w)
    
    maCovarC=np.array([[s2_uu,s2_uv,s2_uw],[s2_uv,s2_vv,s2_vw],[s2_uw,s2_vw,s2_ww]])
   
    return maCovarC

def maCovTLE(u,v,w):
    m_u=np.mean(u)
    m_v=np.mean(v)
    m_w=np.mean(w)
    uu=[]
    vv=[]
    ww=[]
    for i in range(len(u)):
        uu.append(u[i]-m_u)
        vv.append(v[i]-m_v)
        ww.append(w[i]-m_w)
        
    maCovarT=maCovCODS(uu,vv,ww)
    
    return maCovarT   


def EjecutaMaCovar(archivo):
    
#    datoTipo=raw_input()
    u=[]
    v=[]
    w=[]
#     if datoTipo==2:
#         datos=open('../Ajustar/diferencias/diferenciasUVW','r')
#         datos1=datos.readlines()
#         for l in datos1:
#             campos=l.split()
#             dt=l[:19]
#             dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
#             u.append(float(campos[2]))
#             v.append(float(campos[3]))
#             w.append(float(campos[4]))
#         maCovar=maCovCODS(u,v,w)
#     else:
    datos=open('../AjustarTLE/diferencias/'+archivo,'r')
    datos1=datos.readlines()
    for l in datos1:
        campos=l.split()
        dt=l[:19]
        dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
        u.append(float(campos[2]))
        v.append(float(campos[3]))
        w.append(float(campos[4]))
    maCovar=maCovTLE(u, v, w)
    
    
    csvsalida = open('../main/matrices/'+archivo+'.csv', 'w')
    salida = csv.writer(csvsalida)
    salida.writerows(maCovar)
    
    print 'Ma. de Covarianza de: ', archivo    
    print maCovar
    
    return maCovar
    
    