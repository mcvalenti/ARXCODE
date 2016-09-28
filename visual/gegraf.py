"""
Created on Thu Nov 12 10:30:56 2015

GEGRAF: Gestor de graficos
Grafica las diferencias en la posicion.

@author: mcvalenti
"""
#-----------------------------
# INPUT :: diferencias
#-----------------------------

import matplotlib.pylab as plt
import matplotlib.dates as mdates
from datetime import datetime

def gegraf(datos):  
    f1=open(datos,'r')
    fechas=[]
    xx=[]
    yy=[]
    zz=[]
    lineas=f1.readlines()
    
    for i in lineas:
        ls = i.split(' ')
        fecha=datetime.strptime(ls[0], "%Y-%m-%d")
        fechas.append(fecha)
        xx.append(ls[2])
        yy.append(ls[3])
        zz.append(ls[4])
    
    """
    Coordenada U
    """

    fig, ax = plt.subplots(1)
    plt.grid()
    plt.title('Diferencias en la Coordenada U [km]')
    plt.ylabel('U [km]')
    plt.ylim(-2.0,18.0)
    ax.plot(fechas,xx, label='modulo de distancia')
    fig.autofmt_xdate() # rotate and align the tick labels so they look better
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.savefig('../visual/difcoordenadasU.png')
    plt.show()

    """
    Coordenada V
    """
    fig, ax = plt.subplots(1)
    plt.grid()
    plt.title('Diferencias en la Coordenada V [km]')
    plt.ylabel('V [km]')
    plt.ylim(-2.0,18.0)
    ax.plot(fechas,yy, label='modulo de distancia')
    fig.autofmt_xdate() # rotate and align the tick labels so they look better
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.savefig('../visual/difcoordenadasV.png')
    plt.show()

    """
    COMPONENTE W
    """
    fig, ax = plt.subplots(1)
    plt.grid()
    plt.title('Diferencias en la Coordenada W [km]')
    plt.ylabel('W [km]')
    plt.ylim(-2.0,18.0)
    ax.plot(fechas,zz, label='modulo de distancia')
    fig.autofmt_xdate() # rotate and align the tick labels so they look better
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))

    plt.savefig('../visual/difcoordenadasW.png')
    plt.show()


