'''
Created on 05/04/2017

@author: mcvalenti
'''
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime 

def grafica_set_principal(sat_id,path,grafico_arch,data):
    """
    MANDAR SET DE DATOS. 
    """
    dt_frac=data[0]
    dv=data[1]
    dn=data[2]
    dc=data[3]
#     archivo=open(path+grafico_arch,'r')
#     contenido = archivo.readlines()
#     dt=[]
#     dt_frac=[]
#     dv=[]
#     dn=[]
#     dc=[]
# 
#     for c in contenido:
#         fecha=c[:19]
#         anio=fecha[0:4]
#         mes=fecha[5:7]
#         dia=fecha[8:10]
#         hora=fecha[11:13]
#         minutos=fecha[14:16]
#         segundos=fecha[17:19]
#         dt.append(datetime(int(anio),int(mes),int(dia),int(hora),int(minutos),int(segundos)))
#         campos=c.split(' ')
#         dv.append(float(campos[2]))
#         dn.append(float(campos[3]))
#         dc.append(float(campos[4]))
# 
#     for kt in dt:
#         dt_frac.append((kt-dt[0]).total_seconds()/86400.0)
        
#     plt.plot(dt_frac, dv, 'rd', label='V')
#     plt.plot(dt_frac, dn, 'bo', label='N')
#     plt.plot(dt_frac, dc, 'kx', label='C')
#     plt.grid()
#     plt.title('Diferencias en las Coordenadas V,N,C [km] del set principal')
#     plt.ylabel('Diferencia en Km')
#     plt.legend(loc=4)
#     plt.savefig('../visual/archivos/setPri_cods_'+sat_id+'.png')
#     plt.show()
#     plt.close()
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)

    ax1.plot(dt_frac, dv, 'rd', label='V')
    ax1.set_ylabel('Km')
    plt.legend(loc=4)
    ax2.plot(dt_frac, dn, 'bo', label='N')
    ax2.set_ylabel('Km')
    plt.legend(loc=4)
    ax3.plot(dt_frac, dc, 'kx', label='C')
    ax3.set_ylabel('Km')
    fig.suptitle('Diferencias en las Coordenadas V,N,C [km] del set principal')
    plt.xlabel('Epoca')
    plt.legend(loc=4)
    plt.savefig('../visual/archivos/setPri_cods_'+sat_id+'.png')
    plt.show()
    plt.close()
    

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
    