'''
Created on 19/01/2017

@author: mcvalenti
'''

from os import system
import numpy as np
import pylab
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from time import mktime
from datetime import datetime
import datetime as dt

#system('gnuplot TleVsCods.plt')

def my_plotter(ax, data1, data2, param_dict):
    """
    A helper function to make a graph

    Parameters
    ----------
    ax : Axes
        The axes to draw to

    data1 : array
       The x data

    data2 : array
       The y data

    param_dict : dict
       Dictionary of kwargs to pass to ax.plot

    Returns
    -------
    out : list
        list of artists added
    """
       
    ax.plot_date(data1, data2,**param_dict)
#    out = ax.plot(data1, data2, **param_dict)

def AjustePol():
    pass
    

#def VerGrafico():
if __name__=='__main__':
    
    datos=open('../visual/archivos/diferenciasTOD','r')
    listas=datos.readlines()
    data0=[]
    data1=[]
    data2=[]
    data3=[]
    
    for l in listas:
        linea=l.split(' ')
        data0.append(linea[0])
        data1.append(float(linea[2]))
        data2.append(linea[3])
        data3.append(linea[4])
        
    """
    FUNCION DE AJUSTE
    """
#     fecha=[]
#     for dt in data0:
#         #fecha.append(mktime(dt.timetuple())+1e-6*dt.microsecond)
#         dt1=datetime.strptime(dt,'%Y-%m-%d')
#         fecha.append((mktime(dt1.timetuple())+1e-6*dt1.microsecond)/1e+6)
    
           
       
    maxx=float(max(data1))
    minx=float(min(data1))
    maxy=float(max(data2))
    miny=float(min(data2))
    plt.ylim([miny,maxy])
    plt.xlim([minx,maxx])
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    """
    Gestion de Fechas
    """
    date_fmt = '%Y-%m-%d'
    epoca=[dt.datetime.strptime(str(i), date_fmt) for i in data0]
    x = [mdates.date2num(i) for i in epoca]
    date_formatter = mdates.DateFormatter('%d-%m-%y')
    """
    """
    Polynomial=np.polynomial.Polynomial
    b,a= Polynomial.fit(x, data1, deg=1)
    f=[]
    for t in x:
        f.append(a+b*(t-x[0]))
    """
    """
    ax1.xaxis.set_major_formatter(date_formatter)
    ax2.xaxis.set_major_formatter(date_formatter)
    ax3.xaxis.set_major_formatter(date_formatter)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    
    my_plotter(ax1, x, data1, {'marker':'x'})
    my_plotter(ax1, x, f, {'marker':'d'})
    my_plotter(ax2, x, data2, {'marker':'o'})
    my_plotter(ax3, x, data3, {'marker':'d'})

    plt.show()