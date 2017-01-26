'''
Created on Aug 26, 2016

Toma 10 tles de un archivo y realiza un metodo de ajuste,
a fin de obtener una matriz de covarianza con el error.

@author: mcvalenti
'''
import glob, os, os.path, time
import operator
import numpy as np
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import tle_info
from SistReferencia.sist_deCoordenadas import uvwSis

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
    return {}

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
        tle=tle_info(arch) # instancia un objeto de la clase  TLE
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
    archivotle=open('../TleAdmin/tle/'+tlepri,'r')
    lineas=archivotle.readlines()
    line1=lineas[0]
    line2=lineas[1]
    satrec = twoline2rv(line1, line2, whichconst)
    ffin=satrec.epoch
    r,v = satrec.propagate(ffin.year,ffin.month,ffin.day,ffin.hour,ffin.minute,ffin.second)
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
    archivotle=open('../TleAdmin/tle/'+tlesec,'r')
    lineas=archivotle.readlines()
    line1=lineas[0]
    line2=lineas[1]
    satrec1 = twoline2rv(line1, line2, whichconst)
    ffin_anno=ffin.year
    ffin_mes=ffin.month
    ffin_dia=ffin.day
    ffin_hora=ffin.hour
    ffin_min=ffin.minute
    ffin_s=ffin.second
    pos, vel=satrec1.propagate(ffin_anno, ffin_mes, ffin_dia, ffin_hora, ffin_min, ffin_s)
    x,y,z=tuplaFloat(pos)
    pos=np.array([x,y,z])
    fsec=satrec1.epoch
    return pos,vel,fsec

def difTle(setID,tleOrdenados,cantidad_tles):
    """
    ---------------------------------------------------------------
    Calcula las diferencias entre TLE primario y secundarios
    en el sistema u,v y w. 
    Lo hace en forma iterativa, recorriendo todos los TLE a fin
    de que todos son primarios en algun momento.
    ---------------------------------------------------------------
    input:
        setID: numero de set a ser analizado (string)
        tleOrdeandos: lista de TLEs y sus 2-lineas (lista de lista)
    output:
        difTotal# : archivo de texto plano (4 columnas) para cada set
        [AjustarTLE/diferencias/difTotal#]
    """

    dtot=open('../AjustarTLE/diferencias/difTotal'+setID,'w')
    for i in range(cantidad_tles-1,0,-1):
        tlepri=tleOrdenados[i][0]
        r,rp,ffin=tlePrimario(tlepri)        
        item=range(i-1,0,-1)
        print '------------------------------------------------------------------------------------'
        print 'TLE Primario: ', tlepri, ffin, r, rp
        print '------------------------------------------------------------------------------------'
        for j in item:
            tlesec=tleOrdenados[j][0]
            pos,vel,fsec=tleSecundario(tlesec, ffin)
            dr=pos-r
            dt=abs(fsec-ffin)
            dtfracdias=dt.total_seconds()/86400.0
            v,n,c=uvwSis(r, rp, dr)
            infodiftot=str(dtfracdias)+','+str(v)+','+str(n)+','+str(c)+','+str(fsec)+','+tlesec+'\n'
            dtot.write(infodiftot)
            inforepo=tlesec+' '+str(fsec)+' '+str(v)+' '+str(n)+' '+str(c)+'\n'
    #        inforepo=tlesec+' '+str(fsec)+' '+str(pos[0])+' '+str(pos[1])+' '+str(pos[2])+str(vel[0])+' '+str(vel[1])+' '+str(vel[2])+'\n'
            print inforepo
    return {}

def EjecutaAjustarTLE():
    """
    -----------------------------------------------------------------------------------------
    Ejecuta el Metodo de Osweiler [ref] para la obtencion de diferencias de a pares.
    (aunque ofrece la variante de agrupar de a 15 TLEs y aceptar listados mayores) 
    Solicita el ingreso de un dato crudo  (luego sera un sat id y un intervalo temporal)
    El dato crudo es un listado continuo de mas de un TLE. ('TleAdmin/crudosTLE')
    Ordena los TLE de acuerdo a sus fechas y genera un archivo por TLE   (TleAdmin/tle).
    El codigo solo puede procesar un TLE por dia.    
    -----------------------------------------------------------------------------------------
    """
    """
    Borro los archivos generados para otro satelite.
        carpeta de tles: TleAdmin/tle
        carpeta de diferencias: AjustarTLE/diferencias
        carpeta de graficos: Visual/graficos
    """
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
        
    files=glob.glob('../TleAdmin/diferencias/*')
    for filename in files:
        os.unlink(filename)
        
    files=glob.glob('../visual/graficos/*')
    for filename in files:
        os.unlink(filename)
        
    """
    Se comienza el procesamiento
    Se elije el satelite a procesar entre los datos crudos disponibles.
    """
    seleccionSat() # se selecciona el satelite y se generan sus datos crudos

    """
    Administra los archivos TLEs
    """
    lista=glob.glob('../TleAdmin/tle/*')
    total_tles=len(lista)
    tledic=generadorDatos(lista)
    """
    Ordena los TLEs segun sus fechas.
    """
    tleOrdenados=ordenaTles(tledic)

    """
    Propagacion de TLEs y calculo de las diferencias
    """
    cantidad_tles=len(tleOrdenados)
    print 'Cantidad de TLE a procesar= ',cantidad_tles
    print 'Procesando ...'

    set15=cantidad_tles/15 # generaliza y hace el estudio para ventanas temporales superiores a los 15 dias.
    for s in range(set15):
        a=s*15
        b=a+15
        tleOrdenados1=tleOrdenados[a:b]
        setID=str(s)
        cantidad_tles=len(tleOrdenados1)
        difTle(setID, tleOrdenados1, cantidad_tles)
       
    """
    Tabla para la estimacion de la Ma. de Covarianza.
    archivo: difPrimario - automatizar
    """
    
    difG=open('../AjustarTLE/diferencias/difTotal0','r')
    contenido=difG.readlines()
    difP=open('../AjustarTLE/diferencias/difPrimario','w')
    for c in range(13):
        campos=contenido[c].split(',')
        info=campos[4]+' '+campos[1]+' '+campos[2]+' '+campos[3]+'\n'
        difP.write(info)
    
    """
    Verificacion de generacion del archivo con las diferencias
    """
    print '---------------------------------------------------------------------------------'
    print "Verifiacion de la Generacion del archivo de diferencias"
    print "Ultima modificacion %s" % time.ctime(os.path.getmtime('../AjustarTLE/diferencias/difTotal0'))
    print "creado: %s" % time.ctime(os.path.getctime('../AjustarTLE/diferencias/difTotal0'))
    print ' '
    print ' '
    """
    generacion de graficos
    """ 
        # gegrafTot('../AjustarTLE/diferencias/difTotal'+setID,setID)
    
    #     #gegraf('../AjustarTLE/diferencias/diferencias'+tlepri,tlepri)



