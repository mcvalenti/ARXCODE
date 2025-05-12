'''
Created on 16/03/2017

@author: mcvalenti
'''

import os, glob
import numpy as np
import numpy.polynomial as P
from scipy.interpolate import barycentric_interpolate
from datetime import datetime, timedelta
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TLE import Tle
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from funcionesUtiles.funciones import toTimestamp
#from Comparar.TleVsCods import interpola, encuentraBordes
from SistReferencia.sist_deCoordenadas import vncSis, teme2tod, xv2eo
from CodsAdmin.EphemCODS import EphemCODS
from Estadistica.ajusteMinCuad import ajustar_diferencias
from Estadistica.tendenciaTle import grafica_tendencia, grafica_EO
from visual.ploteos import grafica_set15dias
from time import sleep
import progressbar

def generaTOD(tles,sat_id):
    listaTle={}
    for i in tles:
        tle1=Tle(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        r_teme=[r[0],r[1],r[2]]
        r_tod=teme2tod(fecha, r_teme)
        r_todx=np.array(r_tod[0][0])
        listaTle[fecha]=str(r_todx[0][0])+' '+str(r_todx[0][1])+' '+str(r_todx[0][2])+'\n'#+str(v[0])+' '+str(v[1])+' '+str(v[2])
    listaTle=sorted(listaTle.items())
    archivo=str(sat_id)+'_TOD_xyz.txt'
    salidaTle=open('../TleAdmin/crudosTLE/'+archivo,'w+')
    for k in listaTle:        
        infoa=str(k[0])
        infob=k[1]
        linea=infoa+' '+infob+'\n'
        salidaTle.write(linea)
    salidaTle.close()    
    return archivo
        
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
    yvz_new=barycentric_interpolate(x_array, fvz_array, x_new)
    lineaInterpol=lcampos[0]+' '+lcampos[1]+' '+str(yx_new)+' '+str(yy_new)+' '+str(yz_new)+' '+str(yvx_new)+' '+str(yvy_new)+' '+str(yvz_new)+'\n'
    
    return lineaInterpol

def FiltraArchivos(tle):
    """
    Extrae la fecha del TLE y busca los
    archivos CODS que podrian contener la fecha necesaria.
    Toma el nombre del archivo cuyo nombre contiene la fecha el TLE
    primario y agrega a su vez el nombre de los proximos 3 archivos
    ya que tambien contendran esa fecha y con valores mas actualizados.
    ----------------------------------------------------------------
    input
        tle: nombre del archivo del TLE a procesar (String)
    output
        archivos_datos: nombres de los archivos CODS que contienen la fecha
                        del TLE primario - (Lista)
    """
    tle1=Tle.creadoxArchivo(tle)
    fecha=tle1.epoca()
    fechas_busqueda=[datetime(fecha.year,fecha.month,fecha.day)+timedelta(days=2),
                     datetime(fecha.year,fecha.month,fecha.day)+timedelta(days=1),
                     datetime(fecha.year,fecha.month,fecha.day)]
    
    nombre_archivos = glob.glob('../CodsAdmin/TOD_O/*')
    lista_fechas=[]
    archivos_datos=[]
    for nom in nombre_archivos:        
        e_CODS=EphemCODS(nom.split('/')[-1])
        anio, mes, dia, hora, minu, seg = EphemCODS.parsea_epoca_nombre(e_CODS)
        fecha_cods_nombre=datetime(int(anio),int(mes),int(dia))
        lista_fechas.append(fecha_cods_nombre)

    for f in fechas_busqueda:
        if f in lista_fechas:
            indice = lista_fechas.index(f)
            archivos_datos.append(nombre_archivos[indice])
        else:
            pass
        
    return archivos_datos

def sv_interpolados(tles):
    """
    Arma la lista de TLEs y busca los valores
    del Vector de Estado de CODS interpolado para las fechas
    correspondientes a los TLEs. 
    """
    gpsf=open('../CodsAdmin/TOD_O/TOD_CODS_SACD_xyz.txt','r')
    gpslista=gpsf.readlines()
    lineaInterpol=[]
    for i in tles:
        tle1=Tle(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        fila=str(fecha)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
        inferior, superior= encuentraBordes(gpslista,fila)
        lineaInterpol.append(interpola(fila,inferior,superior))
    return lineaInterpol

def interpola_3sv(tle,arch3_cods):
    """
    Extrale del tle primario la epoca y luego busca entre los archivos
    CODS cual de los mas actualizados contiene la epoca del TLE.
    Luego interpola los valores de CODS para la epoca del TLE 
    y devuelve el vector de estado interpolado correspondiente a la epoca.
    ----------------------------------------------------------------------------------------
    input
        tle: nombre del archivo del TLE primario (String)
        arch3_cods: nombre de los archivos CODS que contienen la epoca del TLE. (Lista)
    output
        linea_interpol: linea con el vector de estado interpolado a la epoca del TLE. (String)
    """
    tle1=Tle.creadoxArchivo(tle)
    fecha_tle=tle1.epoca()
    r,v=tle1.propagaTLE()
    fila=str(fecha_tle)+' '+str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
    fecha_minutos = datetime(int(fecha_tle.year),int(fecha_tle.month),int(fecha_tle.day),int(fecha_tle.hour),int(fecha_tle.minute),0)
    inferior = 'NULO' 
    m=0
    for arch in arch3_cods:
        a=open(arch,'r')
        contenido = a.readlines()
        lista_epocas=[]
        for c in contenido:
            c1=c.split(' ')
            if c1[0]=='*HEADER':
                continue
            fecha=c[:16]
            hr=fecha[11:13]
            if hr != '24':
                d=datetime.strptime(fecha,'%Y/%m/%d %H:%M')
            lista_epocas.append(d)
        if fecha_minutos in lista_epocas and m==0:
            indice = lista_epocas.index(fecha_minutos)
            inferior = contenido[indice+1]
            if indice+2 >= len(contenido):
                superior=contenido[indice]
            else: 
                superior = contenido[indice+2]
            m=m+1   
    if inferior != 'NULO':         
        linea_interpol=interpola(fila,inferior,superior)    
        return linea_interpol
    else:
        return None

def diferencias_tleCODS(salida,tles,linea_interpol,data):
    """
    Toma la lista de archivos TLEs y propaga cada uno hasta la epoca de la
    linea interpolada. Luego compara los valores de las coordenadas propagadas
    con los valores de la linea interpolada y genera las diferencias. 
    Imprime los resultados en el archivo salida.     
    ----------------------------------------------------------------------------------------------------------
    input
        salida: archivo donde se escribe (Instancia de apertura de archivo)
        tles: lista de nombres de archivos tle (diccionario)
        linea_interpol: Linea interpolada de los datos CODS para la epoca del TLE primario. (String)
    output
        difTot_satId_fini_ffin.cods: Archivo con todas las diferencias ('../Comparar/diferencias/')
    """
    fecha=linea_interpol[:26]
    d=datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S.%f')
    r=np.array([float(linea_interpol.split()[2]),float(linea_interpol.split()[3]),float(linea_interpol.split()[4])])
    rp=np.array([float(linea_interpol.split()[5]),float(linea_interpol.split()[6]),float(linea_interpol.split()[7])])
    item=range(0,len(tles))
    whichconst=wgs72
    for j in item:
        tle0=Tle.creadoxArchivo('../TleAdmin/tle/'+tles[j][0])
        fecha_tle=tle0.epoca()
        if fecha_tle <= d:
            dif_fechas=(d-fecha_tle).total_seconds()/86400.0
            line1=tle0.linea1
            line2=tle0.linea2
            satrec = twoline2rv(line1, line2, whichconst)
            pos1, vel1=satrec.propagate(d.year, d.month, d.day,d.hour, d.minute, d.second)
            pos=teme2tod(fecha_tle, pos1)
            vel=teme2tod(fecha_tle, vel1)
            difx=[pos[0,0]-r[0],pos[0,1]-r[1],pos[0,2]-r[2]]
            difv=[vel[0,0]-rp[0],vel[0,1]-rp[1],vel[0,2]-rp[2]]
#             difx=[pos1[0]-r[0],pos1[1]-r[1],pos1[2]-r[2]]
#             difv=[vel1[0]-rp[0],vel1[1]-rp[1],vel1[2]-rp[2]]
            v,n,c=vncSis(r,rp,difx)
            vv,nn,cc=vncSis(r,rp,difv)
            dato=str(fecha_tle)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+'\n'
            salida.write(dato)
            data[0].append(fecha_tle)
            data[1].append(v)
            data[2].append(n)
            data[3].append(c)
            data[4].append(vv)
            data[5].append(nn)
            data[6].append(cc)
            data[7].append(dif_fechas)
    return data

def dif_tleCODS15dias():
    
    t=[]
    dv=[]
    du=[]
    dc=[]
    dvv=[]
    dnn=[]
    dcc=[]
    dt_frac=[]
    #===============
    # Set de Datos
    #===============
    data=[t,dv,du,dc,dvv,dnn,dcc,dt_frac]   
    
#    print 'PROCESANDO DATOS DE MISION...'
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    salida=open('../Comparar/diferencias/difPri_prueba','w')
     
    
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_ffin  = tle_primario.epoca()
    cat_id = tle_primario.catID()
    linea1 = tle_primario.linea1
    linea2 = tle_primario.linea2
    epoca15dias=epoca_ffin-timedelta(days=15)
    
    tle_inicio=Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[0][0])
    epoca_ini  = tle_inicio.epoca()
    
    arch3_cods=FiltraArchivos('../TleAdmin/tle/'+tle_ordenados[-1][0])
    linea_interpol=interpola_3sv('../TleAdmin/tle/'+tle_ordenados[-1][0], arch3_cods)
    
    archivo = cat_id+'_'+epoca_ini.strftime("%Y-%m-%d %H:%M:%S.%f")+'_'+epoca_ffin.strftime("%Y-%m-%d %H:%M:%S.%f")+'.cods' 
    #===============================================
    # Bucle de comparacion total  (tiene sentido?)
    #===============================================
    for m in range(len(tle_ordenados)-1,0,-1):
        tle0 = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[m][0])
        epoca_tle0 = tle0.epoca()
        if epoca_tle0 >= epoca15dias:          
            data=diferencias_tleCODS(salida,tle_ordenados, linea_interpol,data)
            if m == len(tle_ordenados)-1:
                for k in range(len(data[0])):
                    info = data[0][k].strftime("%Y-%m-%d %H:%M:%S.%f")+' '+str(data[1][k])+' '+str(data[2][k])+' '+str(data[3][k])+' '+str(data[4][k])+' '+str(data[5][k])+' '+str(data[6][k])+'\n'
                    salida.write(info)
        else:
            continue
    
    dt,coef,statsReport=ajustar_diferencias(epoca_ffin,data,2)    
#    print statsReport
    
    
    set_data15=[str(cat_id),linea1,linea2,epoca_ini.strftime("%Y-%m-%d %H:%M:%S.%f"),epoca_ffin.strftime("%Y-%m-%d %H:%M:%S.%f"),dt,data,coef,archivo]
    return set_data15
    
#     """
#     Toma la lista de archivos TLEs y propaga cada uno hasta la epoca de la
#     linea interpolada. Luego compara los valores de las coordenadas propagadas
#     con los valores de la linea interpolada y genera las diferencias. 
#     Imprime los resultados en el archivo salida.     
#     ----------------------------------------------------------------------------------------------------------
#     input
#         salida: archivo donde se escribe (Instancia de apertura de archivo)
#         tles: lista de nombres de archivos tle (diccionario)
#         linea_interpol: Linea interpolada de los datos CODS para la epoca del TLE primario. (String)
#     output
#         difTot_satId_fini_ffin.cods: Archivo con todas las diferencias ('../Comparar/diferencias/')
#     """
#     fecha=linea_interpol[:26]
#     d=datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S.%f')
#     d15=d-timedelta(days=15)
#     r=np.array([float(linea_interpol.split()[2]),float(linea_interpol.split()[3]),float(linea_interpol.split()[4])])
#     rp=np.array([float(linea_interpol.split()[5]),float(linea_interpol.split()[6]),float(linea_interpol.split()[7])])
#     item=range(0,len(tles))
#     whichconst=wgs72
#     for j in item:
#         tle0=Tle('../TleAdmin/tle/'+tles[j][0])
#         fecha_tle=tle0.epoca()
#         if fecha_tle <= d and fecha_tle > d15:
#             dif_fechas=(d-fecha_tle).total_seconds()/86400.0
#             line1=tle0.linea1
#             line2=tle0.linea2
#             satrec = twoline2rv(line1, line2, whichconst)
#             pos1, vel1=satrec.propagate(d.year, d.month, d.day,d.hour, d.minute, d.second)
#             pos=teme2tod(fecha_tle, pos1)
#             vel=teme2tod(fecha_tle, vel1)
#             difx=[pos[0,0]-r[0],pos[0,1]-r[1],pos[0,2]-r[2]]
#             difv=[vel[0,0]-rp[0],vel[0,1]-rp[1],vel[0,2]-rp[2]]
# #             difx=[pos1[0]-r[0],pos1[1]-r[1],pos1[2]-r[2]]
# #             difv=[vel1[0]-rp[0],vel1[1]-rp[1],vel1[2]-rp[2]]
#             v,n,c=vncSis(r,rp,difx)
#             vv,nn,cc=vncSis(r,rp,difv)
#             dato=str(fecha_tle)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+'\n'
#             salida.write(dato)
#             data[0].append(fecha_tle)
#             data[1].append(v)
#             data[2].append(n)
#             data[3].append(c)
#             data[4].append(vv)
#             data[5].append(nn)
#             data[6].append(cc)
#             data[7].append(dif_fechas)
#     return data

def ejecutaProcesamientoCods():
#if __name__ == '__main__':
    """
    REVISAR - FUE MODIFICADO
    Lista y ordena los nombres de los archivos de la carpeta: TleAdmin/tles.
    Recupera la informacion del ultimo TLE del set (TLE primario), en particular la epoca.
    Busca entre los archivos de CODS, la epoca coincidente con la epoca del TLE primario.
    Interpola para la fecha al nivel del segundo. 
    Luego propaga todos los TLEs del set a la epoca del CODS interpolado y calcular las 
    diferencias. 
    ---------------------------------------------------------------------------------------
    Nota! LOS DATOS CODS SON SOLO DE LA MISION SAC-D.
    Luego los tles, previamente procesados y archivados en la carpeta de TleAdmin/tles, deben
    corresponderse con esa mision.
    """

#    print 'PROCESANDO DATOS DE MISION...'
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
#     tles=glob.glob('../TleAdmin/tle/*')
#     dic_tles=generadorDatos(tles)
#     tle_ordenados=ordenaTles(dic_tles)
    
    tle_inicio = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[0][0])
    cat_id = tle_inicio.catID()
    epoca_ini = tle_inicio.epoca()
    
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_fin  = tle_primario.epoca()
    epoca_ffin = epoca_fin
    epoca15dias=epoca_ffin-timedelta(days=15)
    
    """
    Impresiones de info de TLEs.
    """
    tle_inicio = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[0][0])
    cat_id = tle_inicio.catID()
    epoca_ini = tle_inicio.epoca()
    
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_fin  = tle_primario.epoca()
    epoca_ffin = epoca_fin
    linea1 = tle_primario.linea1
    linea2 = tle_primario.linea2
    fecha_ini=str(epoca_ini.year)+str(epoca_ini.month).zfill(2)+str(epoca_ini.day).zfill(2)
    fecha_fin=str(epoca_fin.year)+str(epoca_fin.month).zfill(2)+str(epoca_fin.day).zfill(2)
#     print '------------------------------------------------------------------------'
#     print '-------------------------TLE PRIMARIO-----------------------------------'
#     print linea1
#     print linea2
#     print epoca_ffin
#     print '------------------------------------------------------------------------'
    t=[]
    dv=[]
    du=[]
    dc=[]
    dvv=[]
    dnn=[]
    dcc=[]
    dt_frac=[]
    t15=[]
    dv15=[]
    du15=[]
    dc15=[]
    dvv15=[]
    dnn15=[]
    dcc15=[]
    dt_frac15=[]
    #===============
    # Set de Datos
    #===============
    data=[t,dv,du,dc,dvv,dnn,dcc,dt_frac]
    data15=[t15,dv15,du15,dc15,dvv15,dnn15,dcc15,dt_frac15]
    #======================
    # Nomenclatura Archivos
    #======================
    archivo = cat_id+'_'+fecha_ini+'_'+fecha_fin+'.cods'    
    salida=open('../Comparar/diferencias/difTot_'+archivo,'w')
    salida1=open('../Comparar/diferencias/'+archivo,'w')
    salida15=open('../Comparar/diferencias/dif_15dias_'+archivo,'w')
    #===============================================
    # Bucle de comparacion total  (tiene sentido?)
    #===============================================
    for m in range(len(tle_ordenados)-1,0,-1):
        tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[m][0])
        epoca_fin = tle_primario.epoca()
        arch3_cods=FiltraArchivos('../TleAdmin/tle/'+tle_ordenados[m][0])
        linea_interpol=interpola_3sv('../TleAdmin/tle/'+tle_ordenados[m][0], arch3_cods)
        if linea_interpol != None:                 
            data=diferencias_tleCODS(salida,tle_ordenados, linea_interpol,data)
            if m == len(tle_ordenados)-1:
                for k in range(len(data[0])):
                    info = data[0][k].strftime("%Y-%m-%d %H:%M:%S.%f")+' '+str(data[1][k])+' '+str(data[2][k])+' '+str(data[3][k])+' '+str(data[4][k])+' '+str(data[5][k])+' '+str(data[6][k])+'\n'
                    salida1.write(info)
        else:
            continue
    #================================================== 
    # Bucle de comparacion del set primario (15 TLEs)
    #==================================================
    
    epoca15=epoca_ffin-timedelta(days=15)
    for m in range(len(tle_ordenados)-1,0,-1):
        tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[m][0])
        epoca_fin = tle_primario.epoca()
        if epoca_fin > epoca15:
            arch3_cods=FiltraArchivos('../TleAdmin/tle/'+tle_ordenados[m][0])
            linea_interpol=interpola_3sv('../TleAdmin/tle/'+tle_ordenados[m][0], arch3_cods)
            if linea_interpol != None:                   
                data15=dif_tleCODS15dias()
                if m == len(tle_ordenados)-1:
                    for k in range(len(data15[0])):
                        info = data15[0][k]+' '+str(data15[1][k])+' '+str(data15[2][k])+' '+str(data15[3][k])+' '+str(data15[4][k])+' '+str(data15[5][k])+' '+str(data15[6][k])+'\n'
                       # info = data15[0][k].strftime("%Y-%m-%d %H:%M:%S.%f")+' '+str(data15[1][k])+' '+str(data15[2][k])+' '+str(data15[3][k])+' '+str(data15[4][k])+' '+str(data15[5][k])+' '+str(data15[6][k])+'\n'
                        salida15.write(info)
            else:
                continue 
        else:
            continue  
        
    salida1.close()
    
    """
    AJUSTE Y GENERACION DE COEFICIENTES.
    """
    
#     dt,coef,statsReport=ajustar_diferencias(epoca_ffin,data15,2)
#     dt1,coef1,statsReport1=ajustar_diferencias(epoca_ffin,data15,1)
    coef1=0
    """
    Guarda en archivos las diferencias que se corresponden al
    ultimo TLE del set. (Estadistica/archivos)
    tendenciaTle.py toma luego esos archivos, y grafica.
    """

    estadistica_salida=open('../Estadistica/archivos/'+fecha_ini+'_'+fecha_fin+'_difEst.txt','w')
    info_esta=fecha_fin+' '+str(data[1][len(tles)])+' '+str(data[2][len(tles)])+' '+str(data[3][len(tles)])
    estadistica_salida.write(info_esta)
    estadistica_salida.close()
    
    print ('DIFERENCIAS:')
    print ('-------------------------------------------------------------------------')
    diferencias=[data[1][len(tles)-1],data[2][len(tles)-1],data[3][len(tles)-1],data[4][len(tles)-1],data[5][len(tles)-1],data[6][len(tles)-1]]
    print ('dv =',data[1][len(tles)-1])
    print ('dn =',data[2][len(tles)-1])
    print ('dc =',data[3][len(tles)-1])
    print ('-------------------------------------------------------------------------')
    print ('Fin del Calculo de Diferencias')

#    set_datos=[str(cat_id),linea1,linea2,epoca_ini.strftime("%Y-%m-%d %H:%M:%S.%f"),epoca_ffin.strftime("%Y-%m-%d %H:%M:%S.%f"),dt,data,coef,archivo]
    set_data15=[str(cat_id),linea1,linea2,epoca_ini.strftime("%Y-%m-%d %H:%M:%S.%f"),epoca_ffin.strftime("%Y-%m-%d %H:%M:%S.%f"),data15,coef1,archivo]
    return diferencias,set_data15

def analizaEO():
    """
    Transforma x,y,z a eo, para ver el comportamiento
    en etapas de maniobras. 
    """
    salida=open('eo.txt','w')
    arch3_cods=glob.glob('../CodsAdmin/Validacion/*')
    tiempo=[] 
    prom_a=[]
    prom_i=[]
    n=0
    with progressbar.ProgressBar(max_value=len(arch3_cods)) as progress:
        for arch in arch3_cods:
            sleep(0.1)
            progress.update(n)
            n=n+1
            """
            parseo nombre del archivo
            """
            nombre=arch.split('_')
            dia=nombre[1]
            yy=dia[:4]
            mes=dia[4:6]
            dd=dia[6:8]
            hora=nombre[2]
            fecha_base=datetime(int(yy),int(mes),int(dd))
            tiempo.append(fecha_base)
            """
            Acumulo promedios
            """
            a=open(arch,'r')
            contenido = a.readlines()
            t=[]
            a=[]
            i=[]
            for c in contenido:
                c1=c.split()
                if c1[0]=='*HEADER':
                    continue
                fecha=c[:16]
                hr=fecha[11:13]
                if hr != '24':
                    d=datetime.strptime(fecha,'%Y/%m/%d %H:%M')
                    t.append(d)
                    r=[float(c1[2]),float(c1[3]),float(c1[4])]
                    v=[float(c1[5]),float(c1[6]),float(c1[7])]
                    semi,e,inc,Omega,w,nu=xv2eo(r,v)
                    a.append(semi)
                    i.append(inc*180.0/(np.pi))
            prom_a.append(np.mean(a))
            prom_i.append(np.mean(i))
            info=fecha_base.strftime('%Y-%m-%d')+' '+str(np.mean(a))+' '+str(np.mean(i))+'\n'
            salida.write(info)
    #        print 'procesando archivo: ', n
    dt_frac=[]            
    f_ini=np.min(t)
    for dt in t:
        dt_frac.append((dt-f_ini).total_seconds()/86400.0)
         
    eo=[tiempo,prom_a,prom_i]
 
#    grafica_tendencia(data)
    grafica_EO(eo)
    print ('fin')

if __name__=='__main__':
#    analizaEO()
    """
    #def comparaTodos():
    """    
    tlelista=glob.glob('../TleAdmin/tle/*')
    dic_tle=generadorDatos(tlelista)
    tle_ord=ordenaTles(dic_tle)
    lista_tle_ord=tle_ord[1]
    """
    Validacion con STK de coordenadas TOD.
    """
    listar=[]
    for tle in tle_ord:
        listar.append('../TleAdmin/tle/'+tle[0])
    generaTOD(listar, 37673)
    t=[]
    dv=[]
    dn=[]
    dc=[]
    dx=[]
    dy=[]
    dz=[]
    dvv=[]
    dnn=[]
    dcc=[]
    dt_frac=[]
    a=[]
    i=[]
    data=[t,dv,dn,dc,dt_frac]
    data_xyz=[t,dv,dn,dc,dt_frac]
    whichconst=wgs72
    n=0
    # set de 15 dias.
    corte=len(tle_ord)-15
    tle_15=tle_ord[corte:]
    with progressbar.ProgressBar(max_value=len(tle_ord)) as progress:
        for k in tle_15:
            sleep(0.1)
            progress.update(n)
            n=n+1
            tle=k[0]
            tres_archivos=FiltraArchivos('../TleAdmin/tle/'+tle)
            linea_interpol=interpola_3sv('../TleAdmin/tle/'+tle, tres_archivos)
            if linea_interpol != None:
                fecha=linea_interpol[:26]
                d=datetime.strptime(fecha,'%Y-%m-%d %H:%M:%S.%f')
                r=np.array([float(linea_interpol.split()[2]),float(linea_interpol.split()[3]),float(linea_interpol.split()[4])])
                rp=np.array([float(linea_interpol.split()[5]),float(linea_interpol.split()[6]),float(linea_interpol.split()[7])])
                tle0=Tle.creadoxArchivo('../TleAdmin/tle/'+tle)        
                line1=tle0.linea1
                line2=tle0.linea2
                satrec = twoline2rv(line1, line2, whichconst)
                pos1, vel1=tle0.propagaTLE(d)
                #satrec.propagate(d.year, d.month, d.day,d.hour, d.minute, d.second)
                r_teme=[pos1[0],pos1[1],pos1[2]]
                v_teme=[vel1[0],vel1[1],vel1[2]]
                semi,e,inc,Omega,w,nu=xv2eo(r,rp)
                a.append(semi/1000.0)
                i.append(inc*180.0/(np.pi))
                r_tod=teme2tod(d,r_teme)
                r_tod=np.array(r_tod[0])
                v_tod=teme2tod(d,v_teme)
                v_tod=np.array(v_tod[0])
                t.append(tle0.epoca())
                dv.append(r_tod[0][0]-r[0])
                dn.append(r_tod[0][1]-r[1])
                dc.append(r_tod[0][2]-r[2])
                dx.append(r_teme[0]-r[0])
                dy.append(r_teme[0]-r[1])
                dz.append(r_teme[0]-r[2])
            else:
                pass
         
    f_ini=np.min(t)
    for dt in t:
        dt_frac.append((dt-f_ini).total_seconds()/86400.0)
    
    g=2
    c, stats = P.polynomial.polyfit(dt_frac, dv, deg=g, full=True)
    c1, stats = P.polynomial.polyfit(dt_frac, dn, deg=g, full=True)
    c2, stats = P.polynomial.polyfit(dt_frac, dc, deg=g, full=True)
    coef=[c,c1,c2]
    print (stats)     
#    eo=[t,a,i]
 
    grafica_set15dias(data,coef)
#    grafica_tendencia(data,c)
#    grafica_EO(eo)
    