'''
Created on 14/03/2017

@author: mcvalenti
'''

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt


def VerGrafico(archivo):
    f=open('../Comparar/'+archivo,'r')
    listas=f.readlines()
    archivo_grafico=str('graf_'+archivo.split('_')[-1]+'pw.png')
    
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
    
    """
    GRAFICO
    """
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.xaxis.set_major_formatter(date_formatter)
    ax2.xaxis.set_major_formatter(date_formatter)
    ax3.xaxis.set_major_formatter(date_formatter)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    
#    plt.ion()
    ax1.plot_date( x, y1,'r--',label='Coordenada V')
    ax1.plot_date(x, data1,'x')
    ax1.set_ylabel('Km')
    ax2.plot_date(x, data2,'x',label='Coordenada N')
    ax2.plot_date(x, y2,'r--')
    ax2.set_ylabel('Km')
    ax3.plot_date(x, data3,'x',label='Coordenada C')
    ax3.plot_date(x, y3,'r--')
    ax3.set_ylabel('Km')
    
    fig.suptitle('Diferencias y Funcion de Ajuste (CODS vs TLE+SGP4)')
    plt.xlabel('Epoca')
    plt.savefig('../visual/archivos/'+archivo_grafico)
    plt.show()
    
    return archivo_grafico