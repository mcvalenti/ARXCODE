'''
Created on 17/01/2017
Compara cada SV, de los TLEs
con los valores interpolados de los datos CODS.
Realiza un ajuste y grafica.

@author: mcvalenti
'''
import os, glob
from datetime import datetime, timedelta
import numpy as np
from Estadistica.ajusteMinCuad import ajustar_diferencias
from scipy.interpolate import barycentric_interpolate
from funcionesUtiles.funciones import toTimestamp
#from TleAdmin.TleArchivos import divide_setTLE
from TleAdmin.TLE import Tle,SetTLE
from SistReferencia.sist_deCoordenadas import ricSis, teme2tod
from Comparar.TlevsCodsOSW import FiltraArchivos
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# def generaTEME(tles,sat_id):
#     listaTle={}
#     for i in tles:
#         tle1=Tle(i)
#         fecha=tle1.epoca()
#         r,v=tle1.propagaTLE()
#         listaTle[fecha]=str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
#     listaTle=sorted(listaTle.items())
#     archivo=str(sat_id)+'_xyz.txt'
#     salidaTle=open('../TleAdmin/crudosTLE/'+archivo,'w+')
#     for k in listaTle:        
#         infoa=str(k[0])
#         infob=k[1]
#         linea=infoa+' '+infob+'\n'
#         salidaTle.write(linea)
#     salidaTle.close()    
#     return archivo
        
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
        if campof[0]=='*HEADER':
            continue
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
            superior=gpslista[indice+2]
        else:
            indice=fechasgps.index(d1)
            inferior=gpslista[indice]
            superior=gpslista[indice+2]
    else:
        if d1 in fechasgps[:tot*3/4]:
            indice=fechasgps.index(d1)
            inferior=gpslista[indice]
            superior=gpslista[indice+2]
        else:
            indice=fechasgps.index(d1)
            inferior=gpslista[indice]
            superior=gpslista[indice+2]
                
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
    yvz_new=barycentric_interpolate(x_array, fvz_array, x_new)
    lineaInterpol=lcampos[0]+' '+lcampos[1]+' '+str(yx_new)+' '+str(yy_new)+' '+str(yz_new)+' '+str(yvx_new)+' '+str(yvy_new)+' '+str(yvz_new)+'\n'
    
    return lineaInterpol
 
if __name__=='__main__':   
#def EjecutaComparacion(sat_id,ArchivoTLE,ArchivoCODS):   
    """
    Ajusta TLE.
    Propaga un TLE de SAC-D dos dias hacia adelante.
    y compara con efemerides precisas. 
    Hace los promedios de las diferencias. 
    """
    #========================
    # Descarga un  TLE
    #========================
    fecha_tle=datetime(2013,1,1,0,0,0,0)
    fecha_ini=fecha_tle+timedelta(days=1)
    sat_id='37673'
    tle0=Tle.creadoxParam(sat_id,fecha_tle)
    #archivo de efemeride precisa.
    cods_arch='../CodsAdmin/TOD_O/CODS_20130103_135713_SACD_ORBEPHEM_TOD_XYZ_O.TXT'
    cods_efem=open(cods_arch,'r')
    lista_efem=cods_efem.readlines()
    
    #=======================================
    # Propaga TLE y compara con CODS
    #=======================================   

    while fecha_ini < datetime(2013,1,2,0,0,0,0)+timedelta(minutes=5):
        r_teme,v_teme=tle0.propagaTLE(fecha_ini)
        r_tod=np.array(teme2tod(fecha_ini,r_teme))
        v_tod=np.array(teme2tod(fecha_ini, v_teme))
        linea_tle=fecha_ini.strftime('%Y-%m-%d %H:%M:%S')+' '+str(r_tod[0][0])+' '+str(r_tod[0][1])+' '+str(r_tod[0][2])+' '+str(v_tod[0][0])+' '+str(v_tod[0][1])+' '+str(v_tod[0][2])
        # Busco los bordes del archivo CODS para interpolar.
        inferior,superior=encuentraBordes(lista_efem, linea_tle)
        linea_interp=interpola(linea_tle, inferior, superior)
        #-------------------------------------------------------
        fecha_ini=fecha_ini+timedelta(minutes=1)

    print 'linea inferior = ', inferior
    print 'linea del TLE  = ', linea_tle
    print 'linea superior = ', superior
    print 'linea superior = ', linea_interp
#     #==============================
#     #Realiza un ajuste lineal
#     #==============================
#     g=1
#     dt,coef,statsReport=ajustar_diferencias(fecha_fin,data,g)
#     print coef
#     
#     a=coef[0][0]
#     b=coef[0][1]
#     a1=coef[1][0]
#     b1=coef[1][1]
#     a2=coef[2][0]
#     b2=coef[2][1]
#     y_x=[]
#     y_y=[]
#     y_z=[]
#     for i in dt:
#         y_x.append(b*i+a)
#         y_y.append(b1*i+a1) 
#         y_z.append(b2*i+a2) 
#         
#     #=======================================
#     # Compara con TLE y con valor del ajuste
#     # Para el valor siguiente
#     #=======================================
#     
#     tle1=Tle.creadoxParam(sat_id, fecha_fin+timedelta(days=1))
#     r,v=tle1.propagaTLE()
#     fecha_tle=tle1.epoca().strftime('%Y-%m-%d %H:%M:%S')
#     fecha1=datetime(2013,01,31,21,54,50,188895)
#     linea_tle=fecha_tle+' '+str(r[0])+' '+str(r[1])+' '+str(r[1])+' '+str(v[0])+' '+str(v[1])+' '+str(v[1])+'\n'
#     inferior='2013/01/31 21:54:00.00000000    3346.818557    1833.651642    5898.653401  -4.4348366300  -4.6345210202   3.9476584869'
#     superior='2013/01/31 21:55:00.00000000    3074.012362    1551.992075    6123.158672  -4.6555716778  -4.7509012148   3.5332839498'
#     linea_interp=interpola(linea_tle, inferior, superior)
#     
#     
#     #=========================
#     # Comparacion resultados
#     #=========================
#     x_tle1=r[0]
#     y_tle1=r[1]
#     x_interp=linea_interp.split()[2]
#     y_interp=linea_interp.split()[3]
#     i_extr=(fecha1-fecha_fin).total_seconds()/86400.0
#     x_extrap=b*i_extr+a
#     y_extrap=b1*i_extr+a1
#     
#     print 'Valor del TLE = ', y_tle1
#     print 'Valor de CODS = ', y_interp
#     print 'Valor de Funcion de AJuste = ', y_extrap
#     
#     
#     """
#     Grafico
#     """
#     plt.plot(dt, x_tod, 'rd', label='X')
#     plt.plot(dt, y_tod, 'bo', label='Y')
#     plt.plot(dt, z_tod, 'kx', label='Z')
#     plt.plot(30+i_extr,y_tle1,'go')
#     plt.plot(30+i_extr,y_interp,'gx')
#     plt.plot(30+i_extr,y_extrap,'gd')
#     plt.grid()
#     plt.title('Coordenadas X,Y,Z [km]')
#     plt.ylabel('Km')
#     plt.xlabel('Diferencia en dias')
#     plt.plot(dt, y_x, 'r-', label='Ajuste en X')
#     plt.plot(dt, y_y, 'b-', label='Ajuste en Y')
#     plt.plot(dt, y_z, 'k-', label='Ajueste en Z')
#     plt.legend(loc=3)
#     plt.show()
#     plt.close()
    
    
#     inicio=time()
# 
#     tlelista=glob.glob('../TleAdmin/tle/*')
#     
#     FiltraArchivos()
# 
#     fin=time()  
#     difVNC.close()       
#     print 'FIN', 'Tiempo de Ejecucion = ', fin-inicio
#     
#     return archivo
