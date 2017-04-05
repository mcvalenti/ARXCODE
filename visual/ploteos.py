'''
Created on 05/04/2017

@author: mcvalenti
'''
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

def grafica_set_principal(archivo):
    """
    MANDAR SET DE DATOS. 
    """
    archivo=open('','r')
    dtt=[]

def grafica_diferenciasTotales(sat_id,dt,data,coef):
    """
    Hace un grafico general con todos los datos.
    Contiene las tres componentes en un unico grafico.
    """
    xx=data[1]
    yy=data[2]
    zz=data[3]
    plt.plot(dt, xx, 'rd', label='V')
    plt.plot(dt, yy, 'bo', label='N')
    plt.plot(dt, zz, 'kx', label='C')
    plt.grid()
    plt.title('Diferencias en las Coordenadas V,N,C [km]')
    plt.ylabel('Diferencia en Km')
    plt.legend(loc=4)
    plt.savefig('../visual/difTot'+sat_id+'.png')
    plt.show()
    plt.close()
    
    
def grafica_setcompleto(dt,data,coef):
    """
    Realiza tres graficos, uno por coordenada.
    En cada grafico incorpora la funcion de ajuste,
    cuyos coeficientes fueron previamente calculados y
    se pasan como parametros.
    """
    a=coef[0]
    b=coef[1]
    c=coef[2]
    a1=coef[3]
    b1=coef[4]
    c1=coef[5]
    a2=coef[6]
    b2=coef[7]
    c2=coef[8]
    dv=data[1]
    dn=data[2]
    dc=data[3]
    largo=np.max(dt)
    """
    Funcion de Ajuste.
    """
    x=np.linspace(0,int(largo), 60)
    yv=[]
    yn=[]
    yc=[]
    for i in x:
        yv.append(a*i*i+b*i+c)
        yn.append(a1*i*i+b1*i+c1) 
        yc.append(a2*i*i+b2*i+c2)    
    """
    GRAFICO
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax1.plot( x, yv,'r--',label='Coordenada V')
    ax1.plot(dt, dv,'x')
    ax1.set_ylabel('Km')
    ax2.plot(dt, dn,'x',label='Coordenada N')
    ax2.plot(x, yn,'r--')#
    ax2.set_ylabel('Km')
    ax3.plot(dt, dc,'x',label='Coordenada C')
    ax3.plot(x, yc,'r--')
    ax3.set_ylabel('Km')
    fig.suptitle('Diferencias y Funcion de Ajuste (CODS vs TLE+SGP4)')
    plt.xlabel('Epoca')
    plt.savefig('../visual/archivos/ajustes.png')
    plt.show()
    plt.close()
    
