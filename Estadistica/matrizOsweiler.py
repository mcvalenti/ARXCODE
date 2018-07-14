'''
Created on 23/06/2017

@author: mcvalenti
'''
import os,glob
import numpy as np
from TleAdmin.TLE import Tle, SetTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from SistReferencia.sist_deCoordenadas import ricSis, vncSis

def calcula_matriz_Tles(cat_id,tca0,tca1,crudo):
    """
    Metodo de Osweiler.
    Dado un objeto y un intervalo temporal.
    Ejecuta el metodo de Osweiler de pair-wise para comparar las 
    propagaciones de cada TLE a la epoca del ultimo TLE del set,
     y generar el archivo de diferencias.
    ------------------------------------------------------------------
    inputs
        cat_id: identificador NORAD del objeto (String)
        tca0: epoca de inicio del intervalo (Datetime)
        tca1: epoca de fin del intervalo (Datetime)
        crudo: nombre del archivo con el set de TLEs (String)
               '../TleAdmin/tle/*' - viene vacio.
    outputs
        nombre_archivo: nombre de archivo donde se imprimen las diferencias
                       ('../AjustarTle/ diferencias/') (String) 
        var_x: varianzas en r,t,n (Float)
    """
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
    
    set_deb=SetTLE(cat_id,tca0,tca1,crudo)
    set_deb.divide_setTLE()
    
    tles=glob.glob('../TleAdmin/tle/*')
#     print "=============================================="
#     print "Cantidad de TLE: ", len(tles)
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)        
    
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_primario=tle_primario.epoca()
    r0,rp0=tle_primario.propagaTLE() # En TEME
    r0=np.array([r0[0],r0[1],r0[2]])
        
    nombre_archivo='difRTN_'+str(cat_id)+'_'+tca1.strftime('%Y%m%d')+'.TLE'
    archivo_dif_rsw=open('../AjustarTLE/diferencias/'+nombre_archivo,'w')
    # listas de diferencias (RTN)
    dr=[]
    dt=[]
    dn=[]
    drr=[]
    dtt=[]
    dnn=[]

    item=range(len(tle_ordenados)-2,-1,-1)       
    for j in item:
        tle1=Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[j][0])
        fsec=tle1.epoca()
#        print '======================================='
#        print 'Epoca del TLE: ',fsec
#        print '=======================================
        pos,vel=tle1.propagaTLE(epoca_primario)
        pos=np.array([pos[0],pos[1],pos[2]])
        vel=np.array([vel[0],vel[1],vel[2]]) 
        # Calculo de Diferencias
        d_r=pos-r0
        d_v=vel-rp0
#         r,t,n=vncSis(r0, rp0, d_r)
#         rr,tt,nn=vncSis(r0,rp0,d_v)
        r,t,n=ricSis(r0, rp0, d_r)
        rr,tt,nn=ricSis(r0,rp0,d_v)
        '''
        Sistema RTN
        '''
        dr.append(r)
        dt.append(t)
        dn.append(n)
        drr.append(rr)
        dtt.append(tt)
        dnn.append(nn)
        
        infodifRST=fsec.strftime('%Y-%m-%d %H:%M:%S')+' '+str(r)+' '+str(t)+' '+str(n)+' '+str(rr)+' '+str(tt)+' '+str(nn)+'\n'
        archivo_dif_rsw.write(infodifRST)
    
    var_r=np.var(dr)
    var_t=np.var(dt)
    var_n=np.var(dn)
    
    return nombre_archivo,var_r,var_t,var_n


def calcula_matriz_OSWcorregido(cat_id,tca0,tca1,crudo,diferencias):
    """
    Metodo de Osweiler pero contra el vector de estado
    del Tle primario corregido.
    """
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
    
    set_deb=SetTLE(cat_id,tca0,tca1,crudo)
    set_deb.divide_setTLE()
    
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)        
    
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    epoca_primario=tle_primario.epoca()
    # En TEME
    r0=np.array([diferencias[0],diferencias[1],diferencias[2]])
    rp0=np.array([diferencias[3],diferencias[4],diferencias[5]])
        
    nombre_archivo='difRTN_'+str(cat_id)+'_'+tca1.strftime('%Y%m%d')+'.TLE'
    archivo_dif_rsw=open('../AjustarTLE/diferencias/'+nombre_archivo+'','w')
    # listas de diferencias (RTN)
    dr=[]
    dt=[]
    dn=[]
    drr=[]
    dtt=[]
    dnn=[]

    item=range(len(tle_ordenados)-2,-1,-1)       
    for j in item:
        tle1=Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[j][0])
        fsec=tle1.epoca()
        pos,vel=tle1.propagaTLE(epoca_primario)
        pos=np.array([pos[0],pos[1],pos[2]])
        vel=np.array([vel[0],vel[1],vel[2]]) 
        # Calculo de Diferencias
        d_r=pos-r0
        d_v=vel-rp0
        r,t,n=vncSis(r0, rp0, d_r)
        rr,tt,nn=vncSis(r0,rp0,d_v)
#         r,t,n=ricSis(r0, rp0, d_r)
#         rr,tt,nn=ricSis(r0,rp0,d_v)
        '''
        Sistema RTN
        '''
        dr.append(r)
        dt.append(t)
        dn.append(n)
        drr.append(rr)
        dtt.append(tt)
        dnn.append(nn)
        
        infodifRST=fsec.strftime('%Y-%m-%d %H:%M:%S')+' '+str(r)+' '+str(t)+' '+str(n)+' '+str(rr)+' '+str(tt)+' '+str(nn)+'\n'
        archivo_dif_rsw.write(infodifRST)
    
    var_r=np.var(dr)
    var_t=np.var(dt)
    var_n=np.var(dn)
    
    return nombre_archivo,var_r,var_t,var_n