'''
Created on Aug 26, 2016

Toma 10 tles de un archivo y realiza un metodo de ajuste,
a fin de obtener una matriz de covarianza con el error.

@author: mcvalenti
'''
import glob, os
import operator
import numpy as np
import numpy.polynomial as P
import matplotlib.pylab as plt
from datetime import datetime, timedelta
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from TleAdmin.TLE import Tle
from SistReferencia.sist_deCoordenadas import vncSis, ricSis, teme2tod
from Estadistica.ajusteMinCuad import ajustar_diferencias


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
        tle=Tle.creadoxArchivo(arch) # instancia un objeto de la clase  TLE
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
            tleOrdenados[1]: lista, (fecha)
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
    tle0=Tle.creadoxArchivo(archivo)
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
    tle1=Tle.creadoxArchivo(archivo)
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
        [AjustarTLE/diferencias/difTotal_satID_fechaIni#]
        bin : lista de listas, con las diferencias por bin. 
        data: lista de listas, [dt_frac,dv,dn,dc]
    """  
    
    print 'Procesando datos TLE...'
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
    tle_inicio = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[0][0])
    cat_id = tle_inicio.catID()
    epoca_ini = tle_inicio.epoca()
    
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_fin  = tle_primario.epoca()
    epoca_ffin = epoca_fin
    
    nombre='difTot_'+str(cat_id)+'_'+epoca_ffin.strftime('%Y%m%d')+'_'+epoca_ini.strftime('%Y%m%d')+'.TLE'
    nombre2='difTot_xyz_'+str(cat_id)+'_'+epoca_ffin.strftime('%Y%m%d')+'_'+epoca_ini.strftime('%Y%m%d')+'.TLE'
    dtot=open('../AjustarTLE/diferencias/'+nombre+'','w')
    dtot2=open('../AjustarTLE/diferencias/'+nombre2+'','w')
    dt_tle=[]
    dt_frac=[]
    dv=[]
    dn=[]
    dc=[]
    dvv=[]
    dnn=[]
    dcc=[]
    dx=[]
    dy=[]
    dz=[]
    dxx=[]
    dyy=[]
    dzz=[]
    bin=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
    m=0
    for i in range(cantidad_tles-1,0,-1):       
        tlepri=tleOrdenados[i][0]
        r,rp,ffin=tlePrimario(tlepri)     
        item=range(i-1,-1,-1)       
        for j in item:
            tlesec=tleOrdenados[j][0]
            pos,vel,fsec=tleSecundario(tlesec, ffin)
            dt_tle.append(fsec)
            dr=pos-r
            d_v=vel-rp
            x=dr[0]
            y=dr[1]
            z=dr[2]
            xx=d_v[0]
            yy=d_v[1]
            zz=d_v[2]
            dt=abs(fsec-ffin)
            dtfracdias=dt.total_seconds()/86400.0
            v,n,c=vncSis(r, rp, dr)
            vv,nn,cc=vncSis(r,rp,d_v)
#             v,n,c=ricSis(r, rp, dr)
#             vv,nn,cc=ricSis(r,rp,dv)
            infodiftot=str(fsec)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+' '+tlesec+'\n'
            infodiftot2=str(fsec)+' '+str(x)+' '+str(y)+' '+str(z)+' '+str(xx)+' '+str(yy)+' '+str(zz)+' '+tlesec+'\n'
            dtot.write(infodiftot)
            dtot2.write(infodiftot2)
            dt_frac.append(dtfracdias)
            '''
            Sistema VNC
            '''
            dv.append(v)
            dn.append(n)
            dc.append(c)
            dvv.append(vv)
            dnn.append(nn)
            dcc.append(cc)
            '''
            Sistema TEMA
            '''
            dx.append(x)
            dy.append(y)
            dz.append(z)
            dxx.append(xx)
            dyy.append(yy)
            dzz.append(zz)           
            """
            Clasificacion por bin.
            """
            rangos=np.array([[0,0.5],[0.5,1.5],[1.5,2.5],[2.5,3.5],[3.5,4.5],
                     [4.5,5.5],[5.5,6.5],[6.5,7.5],[7.5,8.5],[8.5,9.5],
                     [9.5,10.5],[10.5,11.5],[11.5,12.5],[12.5,13.5],[13.5,14.5]])
            for k in range(len(rangos)):
                if dtfracdias >= rangos[k][0] and dtfracdias < rangos[k][1]:
                    bin[k].append(infodiftot)
                    
            
        m=m+1 
            
    dataPri=[dt_tle[:15],dv[:15],dn[:15],dc[:15],
             dvv[:15],dnn[:15],dcc[:15],dt_frac[:15]]    
    data1=[dt_tle,dv,dn,dc,dvv,dnn,dnn,dt_frac]
    
    print '++++++++++++GRADO 2++++++++++++++++++'
    dt,coef,statsReport=ajustar_diferencias(epoca_ffin,dataPri,2)
    print coef
    print statsReport
    
    print '++++++++++++GRADO 1++++++++++++++++++'
    dt1,coef1,statsReport1=ajustar_diferencias(epoca_ffin,dataPri,1)
    print coef1
    print statsReport1
    
    data=[dt,data1,coef,nombre]
        
    dtot.close()
    return bin, data, dataPri, coef1

def genera_estadisticaBin(bin_lista):
    
    lista_k=[]
    cantxbin=[]
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
        cantxbin.append(len(bin_lista[k]))
        if len(bin_lista[k]) > 2:
            for m in bin_lista[k]:
                campo=m.split(' ')
                bin_x.append(float(campo[2]))
                bin_y.append(float(campo[3]))
                bin_z.append(float(campo[4]))
                
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
    
    mediaxbin=[mx_list,my_list,mz_list]
    return cantxbin, mediaxbin  

def difPrimario():
    """
    Extrae todos los TLEs que contiene la carpeta tle del administrador
    de TLEs. Propaga cada TLEs a la epoca del ultimo del set y calcula 
    las diferencias. (falta que sea opcional el sistema de ref)
    NOTA: Transforma los resultados al sistema TOD.
    ----------------------------------------------------------------
    output:
        set de datos ... describir. 
    """
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
    tle_inicio = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[0][0])
    cat_id = tle_inicio.catID()
    epoca_ini = tle_inicio.epoca()
    
    #=========================
    # Ultimo TLE del set
    #=========================
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_fin  = tle_primario.epoca()
    epoca_ffin = epoca_fin
    epoca15dias=epoca_ffin-timedelta(days=15)
    
    nombre='difPri_'+str(cat_id)+'_'+epoca_ffin.strftime('%Y%m%d')+'_'+epoca_ini.strftime('%Y%m%d')+'.TLE'
    nombre2='difPri_xyz_'+str(cat_id)+'_'+epoca_ffin.strftime('%Y%m%d')+'_'+epoca_ini.strftime('%Y%m%d')+'.TLE'
    dtot=open('../AjustarTLE/diferencias/'+nombre+'','w')
    dtot2=open('../AjustarTLE/diferencias/'+nombre2+'','w')
    
    dt_tle=[]
    dt_frac=[]
    dv=[]
    dn=[]
    dc=[]
    dvv=[]
    dnn=[]
    dcc=[]
    dx=[]
    dy=[]
    dz=[]
    dxx=[]
    dyy=[]
    dzz=[]

    tlepri=tle_ordenados[-1][0]
    r,rp,ffin=tlePrimario(tlepri) # En TEME
    """
    Transformacion del TEME al TOD.
    """ 
    r=teme2tod(ffin, r)
    r=np.array([r[0,0],r[0,1],r[0,2]])
    rp=teme2tod(ffin, rp) 
    rp=np.array([rp[0,0],rp[0,1],rp[0,2]])
    """
    fin de la transformacion
    """
    item=range(len(tle_ordenados)-2,-1,-1)       
    for j in item:
        tlesec=tle_ordenados[j][0]
        tle1=Tle.creadoxArchivo('../TleAdmin/tle/'+tlesec)
        tle1_epoca=tle1.epoca()
        if tle1_epoca >= epoca15dias:
            pos,vel,fsec=tleSecundario(tlesec, ffin)
            """
            Transformacion del TEME al TOD.
            """ 
            pos=teme2tod(fsec, pos)
            pos=np.array([pos[0,0],pos[0,1],pos[0,2]])
            vel=teme2tod(fsec, vel)
            vel=np.array([vel[0,0],vel[0,1],vel[0,2]])
            """
            fin de la transformacion
            """
            dt_tle.append(fsec)
            dr=pos-r
            d_v=vel-rp
            x=dr[0]
            y=dr[1]
            z=dr[2]
            xx=d_v[0]
            yy=d_v[1]
            zz=d_v[2]
            dt=abs(fsec-ffin)
            dtfracdias=dt.total_seconds()/86400.0
            v,n,c=vncSis(r, rp, dr)
            vv,nn,cc=vncSis(r,rp,d_v)
    #             v,n,c=ricSis(r, rp, dr)
    #             vv,nn,cc=ricSis(r,rp,dv)
            infodifpri=str(fsec)+' '+str(v)+' '+str(n)+' '+str(c)+' '+str(vv)+' '+str(nn)+' '+str(cc)+' '+tlesec+'\n'
            infodifpri2=str(fsec)+' '+str(x)+' '+str(y)+' '+str(z)+' '+str(xx)+' '+str(yy)+' '+str(zz)+' '+tlesec+'\n'
            dtot.write(infodifpri)
            dtot2.write(infodifpri2)
            dt_frac.append(dtfracdias)
            '''
            Sistema VNC
            '''
            dv.append(v)
            dn.append(n)
            dc.append(c)
            dvv.append(vv)
            dnn.append(nn)
            dcc.append(cc)
            '''
            Sistema TEME
            '''
            dx.append(x)
            dy.append(y)
            dz.append(z)
            dxx.append(xx)
            dyy.append(yy)
            dzz.append(zz)       
            
    data1=[dt_tle,dv,dn,dc,dvv,dnn,dnn,dt_frac]
    var_v=np.var(dv)
    var_n=np.var(dn)
    var_c=np.var(dc)
    
    print '*******************************************************'
    print '-----------------Varianzas---------------------------'
    print '*******************************************************'
    print 'Var en R = ', var_v
    print 'Var en T = ', var_n
    print 'Var en N = ', var_c
    
#     print '++++++++++++GRADO 2++++++++++++++++++'
    dt,coef,statsReport=ajustar_diferencias(epoca_ffin,data1,2)
#     print coef
#     print statsReport
#     
#     print '++++++++++++GRADO 1++++++++++++++++++'
    dt1,coef1,statsReport1=ajustar_diferencias(epoca_ffin,data1,1)
#     print coef1
#     print statsReport1

    data=[dt,data1,coef,nombre]  
    dtot.close()
    dtot2.close() 

    return data     

#if __name__=='__main__':
# 
#     d1='../TleAdmin/tle'
#     if not os.path.exists(d1):
#         os.mkdir(d1)
#     d2='../AjustarTLE/diferencias'
#     if not os.path.exists(d2):
#         os.mkdir(d2)
#     d3='../main/matrices/'
#     if not os.path.exists(d3):
#         os.mkdir(d3)
#     d4='../visual/archivos'
#     if not os.path.exists(d4):
#         os.mkdir(d4)







# #    ejecuta_procesamiento_TLE():
#     """
#     Se crean los directorios necesarios.
#     """
# 
#     d1='../TleAdmin/tle'
#     if not os.path.exists(d1):
#         os.mkdir(d1)
#     d2='../AjustarTLE/diferencias'
#     if not os.path.exists(d2):
#         os.mkdir(d2)
#     d3='../main/matrices/'
#     if not os.path.exists(d3):
#         os.mkdir(d3)
#     d4='../visual/archivos'
#     if not os.path.exists(d4):
#         os.mkdir(d4)
#         
#     files=glob.glob('../AjustarTLE/diferencias/*')
#     for filename in files:
#         os.unlink(filename)
#         
#     self.bin=difTle(self.tleOrdenados, self.tles)
#     self.cantxbin,self.mediaxbin=genera_estadisticaBin(self.bin)
#     self.diferencias=difPrimario(self.filename,self.tles-1)
# 
#     t=[]
#     dv=[]
#     dn=[]
#     dc=[]
#     
#     
#     archivo=open('../AjustarTLE/diferencias/difTotal','r')
#     contenido=archivo.readlines()
#     
#     for c in contenido:
#         campos=c.split(',')
#         t.append(float(campos[0]))
#         dv.append(float(campos[1]))
#         dn.append(float(campos[2]))
#         dc.append(float(campos[3]))
#         
#     c, b, a = P.polynomial.polyfit(t, dv, deg=2)
#     print c,b,a
#     
#     x=np.linspace(0,30, 60)
#     y=[]
#     for i in x:
#         y.append(-0.002373*i*i+0.061160*i-0.077031)
#     
#     plt.plot(t,dv,'x')
#     plt.plot(x,y,'-')
#     plt.show()
    

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