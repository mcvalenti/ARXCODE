'''
Created on 17/01/2017

@author: mcvalenti
'''
import os, glob
import numpy as np
from datetime import datetime
from time import time
from jdcal import gcal2jd, jd2gcal
from scipy.interpolate import barycentric_interpolate
from AjustarTLE.AjustarTLE import seleccionSat
from funcionesUtiles.funciones import toTimestamp
from TleAdmin.TLE import tle_info
from visual.gegraf import gegrafTot
from SistReferencia.sist_deCoordenadas import vncSis

"""
Hace las diferencias
Grafica
"""
def generaTEME(tles):
    listaTle={}
    for i in tles:
        tle1=tle_info(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        listaTle[fecha]=str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
    listaTle=sorted(listaTle.items())
    salidaTle=open('../TleAdmin/tle/TEME_SGP4_SACD_xyz.txt','a')
    for k in listaTle:        
        infoa=str(k[0])
        infob=k[1]
        linea=infoa+' '+infob+'\n'
        salidaTle.write(linea)
        
def encuentraBordes(gpslista,l):
    """
    ------------------------------------------------------------------------------------
    Dada una linea de efemerides Cartesianas procesadas desde un TLE. 
    Este metodo se encarga de buscar en la lista de lineas de efemerides que genera CODS
    cuales son las filas que encierran  la fecha del tle, para que luego se pueda
    interpolar la informacion, con el metodo Interpola
    ------------------------------------------------------------------------------------
    input
        gpslista: lista de lineas con efemerides [fecha epoca x y z vx vy vz]
        l: linea con efemerides [fecha epoca x y z vx vy vz]
    output
        inferior: linea interpolada inferior (str) [fecha epoca x y z vx vy vz]
        superior: linea interpolada superior (str) [fecha epoca x y z vx vy vz]
    """
    fechasgps=[]
    for fg in gpslista:
        campof=fg.split()
        fechas=campof[0]+' '+campof[1]
        dg=datetime.strptime(fechas[:19],'%Y/%m/%d %H:%M:%S')
        fechasgps.append(dg)
    tot=len(fechasgps)
    campos=l.split()
    campos1=campos[0].split('-')
    yy=int(campos1[0])
    mm=int(campos1[1])
    dd=int(campos1[2])
    campos2=campos[1].split(':')
    hh=int(campos2[0])
    minu=int(campos2[1])
    segu=0
    d1=datetime(yy,mm,dd,hh,minu,segu)      
    if d1 < fechasgps[tot/2]:
        if d1 in fechasgps[:tot/4]:
            indice=fechasgps.index(d1)
            inferior=gpslista[indice]
            superior=gpslista[indice-1]
        else:
            indice=fechasgps.index(d1)
            inferior=gpslista[indice]
            superior=gpslista[indice-1]
    else:
        if d1 in fechasgps[:tot*3/4]:
            indice=fechasgps.index(d1)
            inferior=gpslista[indice]
            superior=gpslista[indice-1]
        else:
            indice=fechasgps.index(d1)
            inferior=gpslista[indice]
            superior=gpslista[indice-1]
                
    return inferior,superior
             


def interpola(l,inferior,superior):
    """
    ---------------------------------------------------------------------
    Recibe las lineas con la informacion a interpolar.
    La primera linea es el dato TLE y las otras dos son las lineas
    de los datos CODS cuyas fechas encierran a la fecha del TLE.

    ---------------------------------------------------------------------
    input
        l: cadena con fecha hora x y z vx vy vz (str)
        inferior: cadena con fecha hora x y z vx vy vz (str)
        superior: cadena con fecha hora x y z vx vy vz (str)
    output
        lineaInterpol: cadena con fecha & hora(TLE) + datos interpolados 
    """

    lcampos=l.split()
    dicampos=inferior.split()
    dscampos=superior.split()
    # fecha inferior
    di=inferior[:19]
    di=datetime.strptime(di,'%Y/%m/%d %H:%M:%S')
    di_int=toTimestamp(di)
    #fecha superior
    ds=superior[:19]
    ds=datetime.strptime(ds,'%Y/%m/%d %H:%M:%S')
    ds_int=toTimestamp(ds)
    #fecha tle
    dt=l[:19]
    dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
    dt_int=toTimestamp(dt)
    
    x_array=[di_int,ds_int]
    x_new=dt_int
    # Interpolacion en x
    fx_array=[float(dicampos[2]),float(dscampos[2])]
    yx_new=barycentric_interpolate(x_array, fx_array, x_new)

    # Interpolacion en y
    fy_array=[float(dicampos[3]),float(dscampos[3])]
    yy_new=barycentric_interpolate(x_array, fy_array, x_new)
    
    # Interpolacion en z
    fz_array=[float(dicampos[4]),float(dscampos[4])]
    yz_new=barycentric_interpolate(x_array, fz_array, x_new)
#    lineaInterpol=lcampos[0]+' '+lcampos[1]+' '+str(yx_new)+' '+str(yy_new)+' '+str(yz_new)+'\n'
    
    # Interpolacion en vx
    fvx_array=[float(dicampos[5]),float(dscampos[5])]
    yvx_new=barycentric_interpolate(x_array, fvx_array, x_new)
 
    # Interpolacion en vy
    fvy_array=[float(dicampos[6]),float(dscampos[6])]
    yvy_new=barycentric_interpolate(x_array, fvy_array, x_new)
     
    # Interpolacion en vz
    fvz_array=[float(dicampos[7]),float(dscampos[7])]
    yvz_new=barycentric_interpolate(x_array, fz_array, x_new)
    lineaInterpol=lcampos[0]+' '+lcampos[1]+' '+str(yx_new)+' '+str(yy_new)+' '+str(yz_new)+'\n'
    
    return lineaInterpol
 
if __name__=='__main__':   
# def EjecutaComparacion():   
    """
    Borro los archivos generados para otro satelite.
        carpeta de tles: TleAdmin/tle
        carpeta de diferencias: AjustarTLE/diferencias
        carpeta de graficos: Visual/graficos
    """
    inicio=time()
    
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)  
    seleccionSat()
    
    tles = glob.glob('../TleAdmin/tle/*')
    generaTEME(tles) 
    
    """
    Comparacion HARDCODEADO!!!!!
    """
    
    gpsf=open('../CodsAdmin/TOD_O/TOD_CODS_SACD_xyz.txt','r')
    tlef=open('../TleAdmin/tle/TEME_SGP4_SACD_xyz.txt','r')
    
    gpslista=gpsf.readlines()
    tlelista=tlef.readlines()
    
    
    tot=len(gpslista)
    print 'Total de filas de GPS = ',tot
    print 'Total de Tles = ', len(tlelista)
    print 'Procesando ... '
    
    
    r=[]
    difTOD=open('diferenciasTOD','w')
    difUVW=open('../Ajustar/diferencias/diferenciasUVW','w')
    r=[]
    rp=[]
    df=[]
    d=gcal2jd(2013,6,2.2)
    d1=gcal2jd(2013, 6, 2.7)
    for l in tlelista:
        tle_ephem=l.split()
        inferior, superior= encuentraBordes(gpslista,l)
        lineaInterpol=interpola(l,inferior,superior)
        interpol_ephem=lineaInterpol.split()
        xx=float(tle_ephem[2])
        yy=float(tle_ephem[3])
        zz=float(tle_ephem[4])
        r=[xx,yy,zz]
        vx=float(tle_ephem[5])
        vy=float(tle_ephem[6])
        vz=float(tle_ephem[7])
        rp=[vx,vy,vz]
        dif_x=xx-float(interpol_ephem[2])
        dif_y=yy-float(interpol_ephem[3])
        dif_z=zz-float(interpol_ephem[4])
        df=[dif_x,dif_y,dif_z]
        dif_vx=vx-float(interpol_ephem[5])
        dif_vy=vy-float(interpol_ephem[6])
        dif_vz=vz-float(interpol_ephem[7])
        dfv=[dif_vx,dif_vy,dif_vz]
        info=tle_ephem[0]+' '+tle_ephem[1]+' '+str(dif_x)+' '+str(dif_y)+' '+str(dif_z)+' '+str(dif_vx)+' '+str(dif_vy)+' '+str(dif_vz)+'\n'
        difTOD.write(info)
        u,v,w=vncSis(r,rp,df)
        uu,vv,ww=vncSis(r, rp, dfv)
        info1=tle_ephem[0]+' '+tle_ephem[1]+' '+str(u)+' '+str(v)+' '+str(w)+' '+str(uu)+' '+str(vv)+' '+str(ww)+'\n'
        difUVW.write(info1)
        

    fin=time()  
            
    print 'FIN', 'Tiempo de Ejecucion = ', fin-inicio
    
    