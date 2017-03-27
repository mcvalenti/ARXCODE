"""
Created on Thu Nov 12 10:30:56 2015

GEGRAF: Gestor de graficos
Grafica las diferencias en la posicion.

@author: mcvalenti
"""
import matplotlib.pylab as plt
import matplotlib.dates as mdates
from datetime import datetime
from funcionesUtiles.funciones import toTimestamp

def gegrafTot(difTot,setID):
    archivo=open(difTot,'r')
    dtt=[]
    xx=[]
    yy=[]
    zz=[]
    lineas=archivo.readlines()
    if len(lineas)==0:
        print 'El archivo: '+difTot+' tiene algun problema'
    else:
        for i in lineas:
            ls = i.split(',')
            dtt.append(float(ls[0]))
            xx.append(float(ls[1]))
            yy.append(float(ls[2]))
            zz.append(float(ls[3]))
        plt.plot(dtt, xx, 'rd', label='V')
        plt.plot(dtt, yy, 'bo', label='N')
        plt.plot(dtt, zz, 'kx', label='C')
        plt.grid()
        plt.title('Diferencias en las Coordenadas V,N,C [km]')
        plt.ylabel('Diferencia en Km')
# #         plt.xlim(0,16)
# #         plt.ylim(-5.0,2.0)
#         plt.legend(loc=4)
        plt.savefig('../visual/difTot'+setID+'.png')
        plt.close()

def gegraf(datos,sufijo):  
    f1=open(datos,'r')
    fechas=[]
    xx=[]
    yy=[]
    zz=[]
    lineas=f1.readlines()
    
    for i in lineas:
        ls = i.split(',')
        fechas.append(float(ls[0]))
        xx.append(ls[1])
        yy.append(ls[2])
        zz.append(ls[3])
    
    """
    Coordenada U
    """

    fig, ax = plt.subplots()
    ax.plot(fechas, xx, 'rx', label='V')
    ax.plot(fechas, yy, 'bs', label='N')
    ax.plot(fechas, zz, 'g.', label='C')
    plt.grid()
    plt.title('Diferencias en las Coordenadas V,N,C [km]')
    plt.ylabel('Diferencia en Km')
#     plt.ylim(-20.0,20.0)
#     ax.plot(fechas,xx,'r--',fechas,yy,'bs',fechas,zz,label='U')#,label='modulo de distancia')
#     fig.autofmt_xdate() # rotate and align the tick labels so they look better
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.savefig('../visual/'+sufijo+'.png')
    plt.close()

    """
    Coordenada V
    """
#     fig, ax = plt.subplots(1)
#     plt.grid()
#     plt.title('Diferencias en la Coordenada V [km]')
#     plt.ylabel('V [km]')
#     plt.ylim(-2.0,18.0)
#     ax.plot(fechas,yy, label='modulo de distancia')
#     fig.autofmt_xdate() # rotate and align the tick labels so they look better
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
#     plt.savefig('../visual/difcoordenadasV.png')
#     plt.show()

    """
    COMPONENTE W
    """
#     fig, ax = plt.subplots(1)
#     plt.grid()
#     plt.title('Diferencias en la Coordenada W [km]')
#     plt.ylabel('W [km]')
#     plt.ylim(-2.0,18.0)
#     ax.plot(fechas,zz, label='modulo de distancia')
#     fig.autofmt_xdate() # rotate and align the tick labels so they look better
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
# 
#     plt.savefig('../visual/difcoordenadasW.png')
#    plt.show()

if __name__=='__main__':
    difTot='../AjustarTLE/diferencias/difTotal'
    setID=str(8820)
    gegrafTot(difTot,setID)
    gegraf(difTot,setID)
