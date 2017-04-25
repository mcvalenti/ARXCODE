'''
Created on 17/04/2017
@author: mcvalenti
'''

import glob
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.dates import date2num


def grafica_tendencia(data):
    dt=data[4]
    dv=data[1]
    dn=data[2]
    dc=data[3]
    fecha=data[0]    
    f_ini=datetime.strftime(fecha[0],'%Y%m%d')
    f_fin=datetime.strftime(fecha[-1],'%Y%m%d')
    
    """
    GRAFICO
    -----------------
    Gestion de Fechas
    """
#    x = [datetime.strftime(d,'%Y-%m-%d').date() for d in fecha]
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax1.plot(dt,dv,'r--',label='V')
    ax1.set_ylabel('Km')
    ax1.legend(loc=1)
    ax2.plot(dt,dn,'r--',label='N')
    ax2.set_ylabel('Km')
    ax2.legend(loc=4)
    ax3.plot(fecha,dc,'r--',label='C')
    ax3.set_ylabel('Km')
    ax3.legend(loc=4)
    fig.suptitle('Diferencias CODS vs TLE+SGP4')
    plt.xlabel('Epoca')
    plt.savefig('../Estadistica/'+'tend_'+f_ini+'_'+f_fin+'.png')
    plt.show()
    plt.close()

def grafica_EO(data):
    t=data[0]
    a=data[1]
    i=data[2]
    plt.plot(t,a, marker='o', linestyle='--',label='Semieje')
#    plt.plot(t,i, marker='o', linestyle='--',label='Inclinacion')
    plt.legend(loc=1)
    plt.show()
    
# """
# A partir de las diferencias entre los valores de los TLE
# y los datos GPS, graficar. 
# """
# 
# lista=glob.glob('../Estadistica/archivos/*')
# 
# fechas=[]
# dv=[]
# dn=[]
# dc=[]
# 
# for lis in lista:
#     f=open(lis,'r')
#     contenido=f.readline()
#     campo=contenido.split(' ')
#     yy=int(campo[0][:4])
#     mes=int(campo[0][4:6])
#     dia=int(campo[0][6:8])
#     fecha=datetime(yy,mes,dia)
#     fechas.append(fecha.strftime('%Y-%m-%d'))
#     dv.append(float(campo[1]))
#     dn.append(float(campo[2]))
#     dc.append(float(campo[3]))
# 
# dv_media=np.mean(dv)
# dn_media=np.mean(dn)
# dc_media=np.mean(dc)        
