'''
Created on 05/04/2017

@author: mcvalenti
'''
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime 
from matplotlib.dates import datestr2num


def grafica_diferenciasRIC(archivo):

    data0=[]
    dr=[]
    di=[]
    dc=[]
    min_dist=[]
    archivo=open(archivo,'r')
    contenido=archivo.readlines()

    for c in contenido:
        columna=c.split(' ')
        data0.append(c[0:19])
        dr.append(columna[2])
        di.append(columna[3])
        dc.append(columna[4])
        min_dist.append(np.sqrt(float(columna[2])*float(columna[2])+float(columna[3])*float(columna[3])+float(columna[4])*float(columna[4])))
        
    """
    Gestion de Fechas
    """
    date_fmt = '%Y-%m-%d %H:%M:%S'
    epoca=[datetime.strptime(str(i), date_fmt) for i in data0]
    x = [mdates.date2num(i) for i in epoca]
    date_formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')

    plt.grid()
    plt.plot_date(x, min_dist, fmt='M')
    grafico_dif='../Encuentro/archivos/'+'min_dist.png'
    plt.savefig(grafico_dif)
    return grafico_dif
    
def grafica_set_principal(sat_id,path,data,coef):
    """
   
    """
    salida=path.split('/')[1]
    if salida=='AjustarTLE':
        archivo1='TLE/TLE_difPri_'+sat_id
    else:
        archivo1='CODS/CODS_difPri_'+sat_id
    
    dt=data[7]
    dv=data[1]
    dn=data[2]
    dc=data[3]
    largo=np.max(dt)
    
    if len(coef[0])==3:
        a=coef[0][0]
        b=coef[0][1]
        c=coef[0][2]
        a1=coef[1][0]
        b1=coef[1][1]
        c1=coef[1][2]
        a2=coef[2][0]
        b2=coef[2][1]
        c2=coef[2][2]

        """
        Funcion de Ajuste.
        """
        x=np.linspace(0,int(largo), 60)
        yv=[]
        yn=[]
        yc=[]
        for i in x:
            yv.append(c*i*i+b*i+a)
            yn.append(c1*i*i+b1*i+a1) 
            yc.append(c2*i*i+b2*i+a2)            
    elif len(coef[0]) ==2:
        a=coef[0][0]
        b=coef[0][1]
        a1=coef[1][0]
        b1=coef[1][1]
        a2=coef[2][0]
        b2=coef[2][1]
        dt=data[7]
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
            yv.append(b*i+a)
            yn.append(b1*i+a1) 
            yc.append(b2*i+a2)    
    
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax1.plot( x, yv,'r--',label='Coordenada V')
    ax1.plot(dt, dv,'o')
    ax1.set_ylabel('Km')
    ax2.plot(dt, dn,'o',label='Coordenada N')
    ax2.plot(x, yn,'r--')#
    ax2.set_ylabel('Km')
    ax3.plot(dt, dc,'o',label='Coordenada C')
    ax3.plot(x, yc,'r--')
    ax3.set_ylabel('Km')
    fig.suptitle('Diferencias y Funcion de Ajuste')
    plt.xlabel('Epoca')
    plt.savefig('../visual/archivos/'+archivo1+'_'+str(len(coef[0])))
    plt.show()
    plt.close()


def grafica_diferenciasTotales(sat_id,path,data,coef):
    """
    Hace un grafico general con todos los datos.
    Contiene las tres componentes en un unico grafico.
    """
    salida=path.split('/')[1]
    if salida=='AjustarTLE':
        archivo1='TLE/TLE_difTot_'+sat_id
    else:
        archivo1='CODS/CODS_difTot_'+sat_id
    
    dt=data[7]
    xx=data[1]
    yy=data[2]
    zz=data[3]
    fecha=data[0]

    """
    Grafico
    """
    plt.plot(dt, xx, 'rd', label='V (in-track)')
    plt.plot(dt, yy, 'bo', label='N (normal)')
    plt.plot(dt, zz, 'kx', label='C (cross-track)')
    plt.grid()
    plt.title('Diferencias en las Coordenadas V,N,C [km]')
    plt.ylabel('Diferencia en Km')
    plt.xlabel('Diferencia en dias')
    plt.legend(loc=1)
    f_ini=datetime.strftime(fecha[0],'%Y-%m-%d')
    f_fin=datetime.strftime(fecha[len(data[0])-1],'%Y-%m-%d')
    plt.savefig('../visual/archivos/'+archivo1+'_'+f_ini+'_'+f_fin+'.png')
    plt.show()
    plt.close()

    
def grafica_setcompleto(sat_id,path,data,coef):
    """
    Realiza tres graficos, uno por coordenada.
    En cada grafico incorpora la funcion de ajuste,
    cuyos coeficientes fueron previamente calculados y
    se pasan como parametros.
    """
    salida=path.split('/')[1]
    if salida=='AjustarTLE':
        archivo1='TLE/TLE_setCom_'+sat_id
    else:
        archivo1='CODS/CODS_setCom_'+sat_id
    
    if len(coef[0])==3:
        a=coef[0][0]
        b=coef[0][1]
        c=coef[0][2]
        a1=coef[1][0]
        b1=coef[1][1]
        c1=coef[1][2]
        a2=coef[2][0]
        b2=coef[2][1]
        c2=coef[2][2]
        dt=data[7]
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
            yv.append(c*i*i+b*i+a)
            yn.append(c1*i*i+b1*i+a1) 
            yc.append(c2*i*i+b2*i+a2)            
    elif len(coef[0]) ==2:
        a=coef[0][0]
        b=coef[0][1]
        a1=coef[1][0]
        b1=coef[1][1]
        a2=coef[2][0]
        b2=coef[2][1]
        dt=data[7]
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
            yv.append(b*i+a)
            yn.append(b1*i+a1) 
            yc.append(b2*i+a2)    
           
    """
    GRAFICO
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax1.plot( x, yv,'r--',label='Coordenada V')
    ax1.plot(dt, dv,'o')
    ax1.set_ylabel('Km')
    ax2.plot(dt, dn,'o',label='Coordenada N')
    ax2.plot(x, yn,'r--')#
    ax2.set_ylabel('Km')
    ax3.plot(dt, dc,'o',label='Coordenada C')
    ax3.plot(x, yc,'r--')
    ax3.set_ylabel('Km')
    fig.suptitle('Diferencias y Funcion de Ajuste')
    plt.xlabel('Epoca')
    plt.savefig('../visual/archivos/'+archivo1+'_'+str(len(coef[0])))
    plt.show()
    plt.close()
    
def grafica_set15dias(data15,coef):
    """
    Realiza tres graficos, uno por coordenada.
    En cada grafico incorpora la funcion de ajuste,
    cuyos coeficientes fueron previamente calculados y
    se pasan como parametros.
    """
    dt=data15[7]
    dv=data15[1]
    dn=data15[2]
    dc=data15[3]

    a=coef[0][0]
    b=coef[0][1]
    a1=coef[1][0]
    b1=coef[1][1]
    a2=coef[2][0]
    b2=coef[2][1]
    """
    Funcion de Ajuste.
    """
    x=np.linspace(0,int(np.max(dt)), 60)
    yv=[]
    yn=[]
    yc=[]
    for i in x:
        yv.append(b*i+a)
        yn.append(b1*i+a1) 
        yc.append(b2*i+a2)    
           
    """
    GRAFICO
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax1.plot( dt, dv,'o',label='Coordenada V') #'_draw_dotted'
    ax1.plot(x, yv,'r--')
    ax1.set_ylabel('Km')
    ax2.plot(dt, dn,'o',label='Coordenada N')
    ax2.plot(x, yn,'r--')
    ax2.set_ylabel('Km')
    ax3.plot(dt, dc,'o',label='Coordenada C')
    ax3.plot(x, yc,'r--')
    ax3.set_ylabel('Km')
    fig.suptitle('Diferencias y Funcion de Ajuste')
    plt.xlabel('Epoca')
    plt.savefig('../visual/archivos/pepe15.png')
    plt.show()
    plt.close()


# if __name__=='__main__':
#     archivo='../Encuentro/archivos/27386U_15482U_rtn'
#     grafica_diferenciasRIC(archivo)