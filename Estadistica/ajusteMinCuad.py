'''
Created on 10/04/2017

@author: mcvalenti
'''
import numpy as np
import numpy.polynomial as P


def ajustar_diferencias(epoca_ffin,data,g):
    """
    Toma los datos de fechas y coordenadas y realiza
    un ajuste de minimos cuadrados con la funcion del 
    grado que se le indica en g.
    ----------------------------------------------------
    devuelve la estadistica
    [residuals, rank, singular_values, rcond] : list
    """
    t=data[0]
    dt=[]
    dv=data[1]
    dn=data[2]
    dc=data[3]
    dvv=data[4]
    dnn=data[5]
    dcc=data[6]
    
    if g == 2:    
        for kt in t:
            dt.append((epoca_ffin-kt).total_seconds()/86400.0)
        c, stats = P.polynomial.polyfit(dt, dv, deg=g, full=True)
        c1, stats1 = P.polynomial.polyfit(dt, dn, deg=g, full=True)
        c2, stats2 = P.polynomial.polyfit(dt, dc, deg=g, full=True)
        coef=[c,c1,c2]
        statsReport=[stats,stats1,stats2] 
        return dt,coef,statsReport
    
    elif g == 1:
        for kt in t:
            dt.append((epoca_ffin-kt).total_seconds()/86400.0)
        c, stats = P.polynomial.polyfit(dt, dv, deg=g, full=True)
        c1, stats1 = P.polynomial.polyfit(dt, dn, deg=g, full=True)
        c2, stats2 = P.polynomial.polyfit(dt, dc, deg=g, full=True)
        coef=[c,c1,c2]
        statsReport=[stats,stats1,stats2] 
        return dt,coef,statsReport
        