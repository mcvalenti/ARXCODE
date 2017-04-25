'''
Created on 24/04/2017

@author: mcvalenti
'''
import numpy as np
from datetime import datetime, timedelta
from TleAdmin.TLE import Tle
from SistReferencia.sist_deCoordenadas import teme2tod

if __name__=='__main__':
    path_arch='../TleAdmin/validacion/'
    tle_arch='37673tle12146.tle'
    tle=Tle(path_arch+tle_arch)
    fecha=tle.epoca()
    salida=open('../TleAdmin/validacion/SacD_TEME.txt','w')
    salida2=open('../TleAdmin/validacion/SacD_TOD.txt','w')
    fecha_inicio=datetime(fecha.year,fecha.month,fecha.day,0,0,0)
    for i in range(1440):
        r_f,v_f=tle.propagaTLE(fecha_inicio)
        info=fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')+' '+str(r_f[0])+' '+str(r_f[1])+' '+str(r_f[2])+' '+str(v_f[0])+' '+str(v_f[1])+' '+str(v_f[2])+'\n'
        salida.write(info)
        r_teme=[r_f[0],r_f[1],r_f[2]]
        v_teme=[v_f[0],v_f[1],v_f[2]]
        r_tod=teme2tod(fecha_inicio,r_teme)
        r_tod=np.array(r_tod[0])
        v_tod=teme2tod(fecha_inicio,v_teme)
        v_tod=np.array(v_tod[0])
        info2=fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')+' '+str(r_tod[0][0])+' '+str(r_tod[0][1])+' '+str(r_tod[0][2])+' '+str(v_tod[0][0])+' '+str(v_tod[0][1])+' '+str(v_tod[0][2])+'\n'
        salida2.write(info2)
        fecha_inicio = fecha_inicio + timedelta(minutes=1)
        
    print 'Archivo creado: SacD_TEME.txt'
    print 'Archivo creado: SacD_TOD.txt'
    