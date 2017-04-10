'''
Created on 10/04/2017

@author: mcvalenti
'''
import numpy as np
import numpy.polynomial as P


def ajustar_diferencias(epoca_ffin,data,g):
    
    t=data[0]
    dt=[]
    dv=data[1]
    dn=data[2]
    dc=data[3]
    dvv=data[4]
    dnn=data[5]
    dcc=data[6]
    
    for kt in t:
        dt.append((epoca_ffin-kt).total_seconds()/86400.0)
    c, b, a = P.polynomial.polyfit(dt, dv, deg=g)
    c1, b1, a1 = P.polynomial.polyfit(dt, dn, deg=g)
    c2, b2, a2 = P.polynomial.polyfit(dt, dc, deg=g)
    coef=[a,b,c,a1,b1,c1,a2,b2,c2]

    return dt,coef