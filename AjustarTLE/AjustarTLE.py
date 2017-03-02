'''
Created on Aug 26, 2016

Toma 10 tles de un archivo y realiza un metodo de ajuste,
a fin de obtener una matriz de covarianza con el error.

@author: mcvalenti
'''
import glob
import operator
import numpy as np
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import Tle
from SistReferencia.sist_deCoordenadas import vncSis, ricSis

def seleccionSat():
    """
    --------------------------------------------------------
    Preprocesamiento del dato crudo bajado de Space-track
    Preparacion de los archivos TLE, para el procesamiento.
    La funcion busca en la carpeta TleAdmin/crudosTLE.
    (el archivo debe contener solo las lineas de los tle)
    La funcion guarda los archivos tle generados en la carpeta
    TleAdmin/tle
    -------------------------------------------------------------
    input
        xxxx_fechainicio_fechafin:  archivo de texto plano 
        (xxxx corresponde al cat_id del satelite de interes)
    output
        tle#: lista de archivos con 1 TLE por fecha.
    """
    satelites_datos=glob.glob('../TleAdmin/crudosTLE/*')
    nombres=[]
 
    condicion=True
     
    while(condicion):
        for arch in satelites_datos:
            nombre_archivo=arch.split('/')[-1]
            print nombre_archivo
            nombres.append(nombre_archivo)
        print "Seleccione el Satelite a analizar"
        
        
        crudo=raw_input()
        id_sat=crudo.split('_')[0]
         
        if crudo in nombres:
            setTLE(id_sat, crudo)
            condicion=False
        else:
            print '-------------------------------'
            print "Error en el nombre del archivo"
            print '--------------------------------'
            print '...'
         
    print 'El archivo seleccionado es = ', crudo
    print 'Ud. Selecciono el satelite con ID= ', id_sat  
    return crudo


def generadorDatos(lista):
    """
    ----------------------------------------------------------------------
    Genera un diccionario, cuyas claves son tle1, tle2, tle3...tle10
    y para cada campo, se indica la fecha del tle asociado.
    -----------------------------------------------------------------------
    input
        lista: lista de nombres de los archivos del directorio 'tle' - (string)
    output
        tledic: diccionario
    """
    tledic={}
    datos=[]
    for arch in lista:
        nombre=arch.split('/')[-1]
        tle=Tle(arch) # instancia un objeto de la clase  TLE
        datos.append(tle.epoca()) # ejecuta un metodo de la clase TLE
        tledic[nombre]= datos
        datos=[]
    
    return tledic

def ordenaTles(tledic):
    """
    -----------------------------------------------------------------
    Toma el diccionario de TLEs y los ordena de acuerdo a sus fechas.
    -----------------------------------------------------------------
    input
        tledic: diccionario
    output
        tleOrdenados: lista de listas
            tleOrdenados[0]: 'tle#', numero de tle (string)
            tleOrdenados[1]: lista, (fecha, linea1, linea2)
    """
    ve=open('verif','w')
    ve1=open('verif1','w')
    for k,v in tledic.iteritems():
        info1=str(k)+' '+str(v)+'\n'
        ve.write(info1)
    tleOrdenados=sorted(tledic.items(), key=operator.itemgetter(1))
    for k in tleOrdenados:
        info2=str(k)+'\n'
        ve1.write(info2)
    return tleOrdenados


def tuplaFloat(tupla):
    """
    transforma las tuplas a sus componentes en flotante
    """
    x=float(tupla[0])
    y=float(tupla[1])
    z=float(tupla[2])
    
    return x,y,z

def tlePrimario(tlepri):
    """
    -----------------------------------------------------------------
    Devuelve el vector de estado y la epoca
    correspondiente a la referencia como dato primario
    -----------------------------------------------------------------
    input
        tlepri: nombre del archivo con el TLE primario (string)
    output
        r,v: vector posicion y velocidad para el TLE primario (array)
        ffin: epoca del TLE primario (datetime)
    """
    whichconst = wgs72
    archivo='../TleAdmin/tle/'+tlepri
    tle0=Tle(archivo)
    line1=tle0.linea1
    line2=tle0.linea2
    r,v = tle0.propagaTLE()
    satrec = twoline2rv(line1, line2, whichconst)
    ffin=satrec.epoch
#    r,v = sgp4(satrec,0)
    xf,yf,zf=tuplaFloat(r)
    xv,yv,zv=tuplaFloat(v)
    r=np.array([xf,yf,zf])
    v=np.array([xv,yv,zv])

    return r,v,ffin

def tleSecundario(tlesec,ffin):
    """
    ---------------------------------------------------------------------------------
    Calcula la posicion del satelite propagada a la fecha del TLE primario.
    ---------------------------------------------------------------------------------
    input
        tlesec: nombre del archivo que contiene el TLE secundario (string)
    output
        pos,vel: vector posicion y velocidad que resultan de la propagacion del
                TLE secundario hasta la fecha del TLE primario (array)
        fsec: epoca del TLE secundario
    """
    whichconst = wgs72
    archivo='../TleAdmin/tle/'+tlesec
    tle1=Tle(archivo)
    line1=tle1.linea1
    line2=tle1.linea2
    satrec1 = twoline2rv(line1, line2, whichconst)
    ffin_anno=ffin.year
    ffin_mes=ffin.month
    ffin_dia=ffin.day
    ffin_hora=ffin.hour
    ffin_min=ffin.minute
    ffin_s=ffin.second
#    pos, vel = sgp4(satrec1,0)
    pos, vel=satrec1.propagate(ffin_anno, ffin_mes, ffin_dia, ffin_hora, ffin_min, ffin_s)
    x,y,z=tuplaFloat(pos)
    vx,vy,vz=tuplaFloat(vel)
    pos=np.array([x,y,z])
    vel=np.array([vx,vy,vz])
    fsec=satrec1.epoch
    return pos,vel,fsec

def difTle(tleOrdenados,cantidad_tles):
    """
    ---------------------------------------------------------------
    Diferencias de Osweiler. (Pair-Wise Differencing)
    Calcula las diferencias entre TLE primario y secundarios
    en el sistema v,n y c;  o (ric). 
    Lo hace en forma iterativa, recorriendo todos los TLE a fin
    de que todos son primarios en algun momento.
    ---------------------------------------------------------------
    input:
        tleOrdeandos: lista de TLEs y sus 2-lineas (lista de lista)
    output:
        difTotal# : archivo de texto plano (4 columnas) para cada set
        [AjustarTLE/diferencias/difTotal#]
    """

    dtot=open('../AjustarTLE/diferencias/difTotal','w')
    for i in range(cantidad_tles-1,0,-1):
        tlepri=tleOrdenados[i][0]
        r,rp,ffin=tlePrimario(tlepri)        
        item=range(i-1,-1,-1)
       
        for j in item:
            tlesec=tleOrdenados[j][0]
            pos,vel,fsec=tleSecundario(tlesec, ffin)
            dr=pos-r
            dv=vel-rp
            dt=abs(fsec-ffin)
            dtfracdias=dt.total_seconds()/86400.0
            v,n,c=vncSis(r, rp, dr)
            vv,nn,cc=vncSis(r,rp,dv)
#             v,n,c=ricSis(r, rp, dr)
#             vv,nn,cc=ricSis(r,rp,dv)
            infodiftot=str(dtfracdias)+','+str(v)+','+str(n)+','+str(c)+','+str(vv)+','+str(nn)+','+str(cc)+','+str(fsec)+','+tlesec+'\n'
            dtot.write(infodiftot)
#     
    return {}

def difPrimario(nombre,largo):
    """
    Tabla para la estimacion de la Ma. de Covarianza.
    archivo: difPrimario 
    """
     
    difG=open('../AjustarTLE/diferencias/difTotal','r')
    contenido=difG.readlines()
    salida='dif_'+nombre
    difP=open('../AjustarTLE/diferencias/'+salida,'w')
    for c in range(largo):
        campos=contenido[c].split(',')
        info=campos[7]+' '+campos[1]+' '+campos[2]+' '+campos[3]+' '+campos[4]+' '+campos[5]+' '+campos[6]+'\n'
        difP.write(info)
        
    return salida

#     """
#     Verificacion de generacion del archivo con las diferencias
#     """
#     print '---------------------------------------------------------------------------------'
#     print "Verifiacion de la Generacion del archivo de diferencias: ",salida
#     print "Ultima modificacion %s" % time.ctime(os.path.getmtime('../AjustarTLE/diferencias/difTotal'))
#     print "creado: %s" % time.ctime(os.path.getctime('../AjustarTLE/diferencias/difTotal'))
#     print ' '
#     print ' '
#     """
#     generacion de graficos
#     """ 
        # gegrafTot('../AjustarTLE/diferencias/difTotal'+setID,setID)
    
    #     #gegraf('../AjustarTLE/diferencias/diferencias'+tlepri,tlepri)

    

