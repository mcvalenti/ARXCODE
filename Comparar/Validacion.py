'''
Created on 22/02/2017

@author: mcvalenti
'''
"""
Procesar las diferencias para cierto intervalo.
Generar las funciones de ajuste.
Utilizar las funciones de ajuste para obtener
los datos del mes siguiente: 1 semana, 2 y 4.
Calcular las diferencias de los datos obtenidos
vs los datos CODS.
Comparar con las diferencias anteriores (diferenciasTOD)
Graficar la comparacion.
El mecanismo debe repetirse para varios set de datos.
"""
import datetime
import matplotlib.dates as mdates
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from Comparar.TleVsCods import encuentraBordes, interpola

def filtroAjuste(fi,ff,delta_t):
    a=open('../visual/archivos/diferenciasTOD','r')
    """
    -------------------------------------------------
    Filtro de diferencias en el intervalo de ajuste
    -------------------------------------------------
    delta_t: (en dias)
    """
    
    contenido=a.readlines()
    print 'Procesando'
    
    """
    archivo de Ajuste
    """
    d0=[]
    coordx=[]
    coordy=[]
    coordz=[]
    velx=[]
    vely=[]
    velz=[]
    
    for l in contenido:
        d=l[:19]
        d=datetime.datetime.strptime(d,'%Y-%m-%d %H:%M:%S')
        if d >= fi and d <= ff:
            d0.append(d)
            coordx.append(float(l.split()[2]))
            coordy.append(float(l.split()[3]))
            coordz.append(float(l.split()[4]))
            velx.append(float(l.split()[5]))
            vely.append(float(l.split()[6]))
            velz.append(float(l.split()[7]))
                 
    ephem_ajuste=[d0,coordx,coordy,coordz,velx,vely,velz]            
    return ephem_ajuste


def filtroExtapola(ff,delta_t):
    """
    Extraccion de datos en el intervalo de Extrapolacion.
    """
    
    atle=open('../TleAdmin/crudosTLE/TEME_SGP4_SACD_xyz.txt','r')
    acods=open('../CodsAdmin/TOD_O/TOD_CODS_SACD_xyz.txt','r')
    contenido1=atle.readlines()
    contenido2=acods.readlines()
    
    d0tle=[]
    xtle=[]
    ytle=[]
    ztle=[]
    vxtle=[]
    vytle=[]
    vztle=[]   
    coordx1=[]
    coordy1=[]
    coordz1=[]
    velx1=[]
    vely1=[]
    velz1=[] 
    for l in contenido1:
        d1=l[:19]
        d1=datetime.datetime.strptime(d1,'%Y-%m-%d %H:%M:%S')
        if d1 > ff and d1 <= ff+datetime.timedelta(days=delta_t):
            d0tle.append(d1)  
            xtle.append(float(l.split()[2]))
            ytle.append(float(l.split()[3]))
            ztle.append(float(l.split()[4]))
            vxtle.append(float(l.split()[5]))
            vytle.append(float(l.split()[6]))
            vztle.append(float(l.split()[7]))
            inferior, superior= encuentraBordes(contenido2,l)
            lineaInterpol=interpola(l,inferior,superior)
            interpol_ephem=lineaInterpol.split()
            coordx1.append(float(interpol_ephem[2]))
            coordy1.append(float(interpol_ephem[3]))
            coordz1.append(float(interpol_ephem[4]))
            velx1.append(float(interpol_ephem[5]))
            vely1.append(float(interpol_ephem[6]))
            velz1.append(float(interpol_ephem[7])) 
            print interpol_ephem

    ephem_tle=[d0tle,xtle,ytle,ztle,vxtle,vytle,vztle]
    ephem_extrap=[d0tle,coordx1,coordy1,coordz1,velx1,vely1,velz1]
    return ephem_tle, ephem_extrap

def funcionAjuste(x,y,x_extrap):
    """
    Funcion de Ajuste Lineal
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    g1=np.poly1d([slope,intercept])
    y_extrap=g1(x_extrap)
    
    return y_extrap

if __name__=='__main__':
    """
    Intervalo de ajuste
    """
    fi=datetime.datetime(2013,11,16)
    ff=datetime.datetime(2013,11,30)
    delta_t=10
    
    ephem_ajuste =  filtroAjuste(fi,ff,delta_t)   
    x_ajuste = [mdates.date2num(i) for i in ephem_ajuste[0]]    
    
    ephem_tle, ephem_extrap =filtroExtapola(ff,delta_t)
    t = [mdates.date2num(i) for i in ephem_tle[0]]
    
    x_exptrap = funcionAjuste(x_ajuste,ephem_ajuste[1],t)
    y_exptrap = funcionAjuste(x_ajuste,ephem_ajuste[2],t)
    z_exptrap = funcionAjuste(x_ajuste,ephem_ajuste[3],t)
    
    dif_x=ephem_extrap[1]-(ephem_tle[1]-x_exptrap)
    dif_y=ephem_extrap[2]-(ephem_tle[2]-y_exptrap)
    dif_z=ephem_extrap[3]-(ephem_tle[3]-z_exptrap)
    
    """
    Grafico
    """
     
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    date_formatter = mdates.DateFormatter('%d-%m-%y')
     
    ax1.xaxis.set_major_formatter(date_formatter)
    ax2.xaxis.set_major_formatter(date_formatter)
    ax3.xaxis.set_major_formatter(date_formatter)
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
     
    ax1.plot_date(t, dif_x, 'd')
    ax2.plot_date(t,dif_y, 'x')
    ax3.plot_date(t, dif_z,'v')
     
    plt.show()
        
    
    print 'FIN'
