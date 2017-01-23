'''
Created on 23/01/2017

@author: mcvalenti
'''
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
    
    maCovarC=np.array([[s2_uu,s2_uv,s2_uw],[s2_uv,s2_vv,s2_vw],[s2_uw,s2_uw,s2_ww]])
    
    return maCovarC

if __name__ == '__main__':   
    datos=open('../Ajustar/diferencias/diferenciasUVW','r')
    u=[]
    v=[]
    w=[]
    datos1=datos.readlines()
    for l in datos1:
        campos=l.split()
        dt=l[:19]
        dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
        u.append(float(campos[2]))
        v.append(float(campos[3]))
        w.append(float(campos[4]))

    
    maCovar=maCovCODS(u,v,w)