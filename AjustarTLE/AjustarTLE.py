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
        bin : lista de listas, con las diferencias por bin. 
    """

    dtot=open('../AjustarTLE/diferencias/difTotal','w')

    bin=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in range(cantidad_tles-1,0,-1):       
#         print '********************************************'
#         print 'procesando TLE primario numero = ', i
#         print '********************************************'
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
            """
            Clasificacion por bin.
            """
            rangos=np.array([[0,0.5],[0.5,1.5],[1.5,2.5],[2.5,3.5],[3.5,4.5],
                     [4.5,5.5],[5.5,6.5],[6.5,7.5],[7.5,8.5],[8.5,9.5],
                     [9.5,10.5],[10.5,11.5],[11.5,12.5],[12.5,13.5],[13.5,14.5]])
            for i in range(15):
                if dtfracdias >= rangos[i][0] and dtfracdias < rangos[i][1]:
                    bin[i].append(infodiftot)
            
#         for i in range(15):
#             print bin[i]
            
    dtot.close()
    return bin

def genera_estadisticaBin(bin_lista):
    
    lista_k=[]
    mx_list=[]
    my_list=[]
    mz_list=[]
    vx_list=[]
    vy_list=[]
    vz_list=[]
    stdx_list=[]
    stdy_list=[]
    stdz_list=[]
    for k in range(len(bin_lista)):
        lista_k.append(k)
        bin_x=[]
        bin_y=[]
        bin_z=[]

        
        if len(bin_lista[k]) > 2:
            for m in bin_lista[k]:
                campo=m.split(',')
                bin_x.append(float(campo[1]))
                bin_y.append(float(campo[2]))
                bin_z.append(float(campo[3]))
                
            media_x=np.mean(bin_x)
            mx_list.append(media_x)
            media_y=np.mean(bin_y)
            my_list.append(media_y)
            media_z=np.mean(bin_z)
            mz_list.append(media_z)
            
            varianza_x=np.var(bin_x)
            vx_list.append(varianza_x)
            varianza_y=np.var(bin_y)
            vy_list.append(varianza_y)
            varianza_z=np.var(bin_z)
            vz_list.append(varianza_z)
            
            desviacion_x=np.std(bin_x)
            stdx_list.append(desviacion_x)
            desviacion_y=np.std(bin_y)
            stdy_list.append(desviacion_y)
            desviacion_z=np.std(bin_z)
            stdz_list.append(desviacion_z)
    
#             print '********************************************************************************'
#             print 'BIN'+str(k)
#             print '********************************************************************************'
    print lista_k
    print stdx_list
    print stdy_list
    print stdz_list
#             info ='MEDIA'+' '+str(media_x)+' '+str(media_y)+' '+str(media_z) 
#             info2 = 'VARIANZA'+' '+str(varianza_x)+' '+str(varianza_y)+' '+str(varianza_z)
#             info3 = 'Desviacion Standard'+' '+str(desviacion_x)+' '+str(desviacion_y)+' '+str(desviacion_z)+'\n'
#             print info
#             print info2
#             print info3
   
    return{}
 
    

def difPrimario(nombre,largo):
    """
    Tabla para la estimacion de la Ma. de Covarianza.
    archivo: difPrimario 
    ----------------------------------------------------------------
    input
        nombre: nombre de archivo que identifica el procesamiento. (string)
        largo: cantidad de TLEs en el set, menos  uno. (integer)
    output
        salida: nombre del archivo que contiene la diferencias solo contra 
        el SV de referencia. (string), path: '../AjustarTLE/diferencias/'
    """
     
    difG=open('../AjustarTLE/diferencias/difTotal','r')
    contenido=difG.readlines()
    difP=open('../AjustarTLE/diferencias/'+nombre,'w')
    for c in range(largo):
        campos=contenido[c].split(',')
        info=campos[7]+' '+campos[1]+' '+campos[2]+' '+campos[3]+' '+campos[4]+' '+campos[5]+' '+campos[6]+'\n'
        difP.write(info)
        
    return nombre

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