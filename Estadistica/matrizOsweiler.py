'''
Created on 23/06/2017

@author: mcvalenti
'''
import os,glob
import numpy as np
from TleAdmin.TLE import Tle, SetTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from SistReferencia.sist_deCoordenadas import ricSis

def calcula_matriz_Tles(cat_id,tca0,tca1,crudo):
    """
    Metodo de Osweiler
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
    r0,rp=tle_primario.propagaTLE() # En TEME
    r0=np.array([r0[0],r0[1],r0[2]])
        
    nombre='difRTN_'+str(cat_id)+'_'+tca1.strftime('%Y%m%d')+'.TLE'
    archivo_dif_rsw=open('../AjustarTLE/diferencias/'+nombre+'','w')
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
        d_v=vel-rp
        r,t,n=ricSis(r0, rp, d_r)
        rr,tt,nn=ricSis(r0,rp,d_v)
        '''
        Sistema RTN
        '''
        dr.append(r)
        dt.append(t)
        dn.append(n)
        drr.append(rr)
        dtt.append(tt)
        dnn.append(nn)
        
        infodifRST=fsec.strftime('%Y%m%d')+' '+str(r)+' '+str(t)+' '+str(n)+' '+str(rr)+' '+str(tt)+' '+str(nn)+'\n'
        archivo_dif_rsw.write(infodifRST)
    
    var_r=np.var(dr)
    var_t=np.var(dt)
    var_n=np.var(dn)
    
    return var_r,var_t,var_n

def calcula_matriz_mision():
    pass