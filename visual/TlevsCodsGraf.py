'''
Created on 19/01/2017

@author: mcvalenti
'''

from os import system
from numpy.polynomial import Polynomial
import numpy as np
from scipy import stats
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
    

def VerGrafico():
#if __name__=='__main__':
    
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
        data2.append(float(linea[3]))
        data3.append(float(linea[4]))
                     
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
    Funcion de Ajuste
    """
    slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(x,data1)
    slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(x,data2)
    slope3, intercept3, r_value3, p_value3, std_err3 = stats.linregress(x,data3)

    g1=np.poly1d([slope1,intercept1])
    y1=g1(x)
    g2=np.poly1d([slope2,intercept2])
    y2=g2(x)
    g3=np.poly1d([slope3,intercept3])
    y3=g3(x)

    ax1.xaxis.set_major_formatter(date_formatter)
    ax2.xaxis.set_major_formatter(date_formatter)
    ax3.xaxis.set_major_formatter(date_formatter)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    
    my_plotter(ax1, x, y1, {'marker':'d'})
    my_plotter(ax1, x, data1, {'marker':'x'})
    my_plotter(ax2, x, data2, {'marker':'x'})
    my_plotter(ax2, x, y2, {'marker':'v'})
    my_plotter(ax3, x, data3, {'marker':'x'})
    my_plotter(ax3, x, y3, {'marker':'o'})

    plt.show()