'''
Created on 01/06/2017

@author: mcvalenti
'''
import numpy as np
import sys
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from sgp4.propagation import sgp4
from sgp4.ext import days2mdhms
from sgp4.ext import jday
from requests import session, exceptions
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import TleAdmin
from SistReferencia.sist_deCoordenadas import ricSis
from visual.trackencuentro import grafica_track

class Posicion:

    def __init__(self,r,v,epoca):   
        self.r=r
        self.v=v
        self.epoca=epoca
        
    def getCoordenadasGEOD(self):
        """
        Transforma coordenadas del sistem cartesiano (TEME)
        al sistema geodesico aprox.
        REVISAR!!! 
        ---------------
        outputs
            alpha, delta: angulos Geodesicos (float) [grados]
        """
        deg=np.divide(180,np.pi)
        r_mod=np.sqrt(self.r[0]*self.r[0]+self.r[1]*self.r[1]+self.r[2]*self.r[2])
        l=np.divide(self.r[0],r_mod)
        m=np.divide(self.r[1],r_mod)
        n=np.divide(self.r[2],r_mod)
        self.delta=np.arcsin(n)
        if m>0:
            self.alpha = np.arccos(np.divide(l,np.cos(self.delta)))
        else:
            self.alpha = 2*np.pi-np.arccos(np.divide(l,np.cos(self.delta)))
         
        return self.delta*deg, self.alpha*deg
    
class Tle:  
    
    @classmethod
    def creadoxParam(cls, usuario,clave,sat_id,epoca):
        inst1=cls()
        inst1.noradId=sat_id
        inst1.anio1=epoca.year
        inst1.mes1=epoca.month
        inst1.dia1=epoca.day
        inst1.clave=clave
        epoca=epoca-timedelta(days=2)
        inst1.anio0=epoca.year
        inst1.mes0=epoca.month
        inst1.dia0=epoca.day
        
        try:
            inst1.sincero=[inst1.mes0,inst1.mes1,inst1.dia0,inst1.dia1]
            i=0
            for i in range(len(inst1.sincero)):           
                if inst1.sincero[i] < 10:
                    inst1.sincero[i]='0'+str(inst1.sincero[i])
                i= i+1
            inst1.sincero=[str(inst1.sincero[0]),str(inst1.sincero[1]),str(inst1.sincero[2]),str(inst1.sincero[3])]
            inst1.f0=str(inst1.anio0)+'-'+inst1.sincero[0]+'-'+inst1.sincero[2]
            inst1.f1=str(inst1.anio1)+'-'+inst1.sincero[1]+'-'+inst1.sincero[3]
            data = {'identity': 'macecilia' , 'password': 'MaCeciliaSpace17'}
            s=session() 
            s.post('https://www.space-track.org/auth/login',data)
            fquery1='https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/'+inst1.f0+'--'+inst1.f1+'/NORAD_CAT_ID/'+inst1.noradId+'/orderby/TLE_LINE1 ASC/format/tle'
            r = s.get(fquery1)
            inst1.tle_text=r.text
            inst1.lineas=inst1.tle_text.split('\n')
            inst1.linea1=inst1.lineas[0]
            inst1.linea2=inst1.lineas[1]
            if inst1.tle_text !='' and r.status_code == 200:
                pass #rint 'Se ha generado el tle'
            else:
                print 'No pudo completarse la solicitud'
    
        except exceptions.HTTPError as e:
            return "Error: " + str(e)

        return inst1
    
    @classmethod    
    def creadoxArchivo(cls, archivo):
        inst2=cls()
        inst2.tle = open(archivo,'r')
        lineas = inst2.tle.readlines()
        inst2.linea1 = lineas[0]
        inst2.linea2 = lineas[1]
        inst2.tle.close() 
        inst2.i=inst2.linea2.split()[2]
        inst2.Omega=inst2.linea2.split()[3]
        inst2.e=inst2.linea2.split()[4]
        inst2.ap=inst2.linea2.split()[5]
        inst2.m=inst2.linea2.split()[6]
        inst2.n=inst2.linea2.split()[7]
            
        return inst2
    
    def catID(self):
        self.catID=self.linea1.split(' ')[1]
        return self.catID
        
    def epoca(self):
        whichconst = wgs72
        satrec = twoline2rv(self.linea1, self.linea2, whichconst)
        self.epoca=satrec.epoch
        return self.epoca
    
    def propagaTLE(self,date=None):
        whichconst = wgs72
        satrec = twoline2rv(self.linea1, self.linea2, whichconst)
        if date==None:
            ffin=satrec.epoch
            self.r,self.v = satrec.propagate(ffin.year,ffin.month,ffin.day,ffin.hour,ffin.minute,ffin.second)
        else:
            segundos=date.second+date.microsecond
            self.r,self.v = satrec.propagate(date.year,date.month,date.day,date.hour,date.minute,segundos)
        return self.r,self.v
    


class Encuentro():
    
    def __init__(self,tle_sat,tle_deb,tca):
        
        self.tle_sat=tle_sat
        self.tle_deb=tle_deb
        self.tca=tca
        
        """
        Genera Archivos
        """
        sat_id=self.tle_sat.catID()
        deb_id=self.tle_deb.catID()
        salida1=open('../Encuentro/archivos/'+str(sat_id),'w+')
        salida2=open('../Encuentro/archivos/'+str(deb_id),'w+')
        salida3=open('../Encuentro/archivos/'+str(sat_id)+'_'+str(deb_id)+'_rtn','w+')

        """
        Calcula las diferencias relativas entre los dos 
        objetos en el sistema RTN.
        (agregar la diferencias en rtn)
        """

        self.epoca_ini=self.tca-timedelta(minutes=90)
        epoca_fin=self.tca+timedelta(minutes=10)
        
        self.mod_minDist=sys.float_info.max
        while self.epoca_ini < epoca_fin:
            r,v=self.tle_sat.propagaTLE(self.epoca_ini)
            r1,v1=self.tle_deb.propagaTLE(self.epoca_ini)
            
            r=np.array([float(r[0]),float(r[1]),float(r[2])])
            v=np.array([float(v[0]),float(v[1]),float(v[2])])
            r1=np.array([float(r1[0]),float(r1[1]),float(r1[2])])
            v1=np.array([float(v1[0]),float(v1[1]),float(v1[2])])
            
            pos1=Posicion(r,v,self.epoca_ini)
            pos2=Posicion(r1,v1,self.epoca_ini)
            
            self.DistVector=pos1.r-pos2.r
            x_ric,y_ric,z_ric=ricSis(pos1.r,pos1.v,self.DistVector)
            self.DistRic=np.array([x_ric,y_ric,z_ric])
            self.VelVector=pos1.v-pos2.v
            self.mod_Dist1=np.sqrt(np.dot(self.DistRic,self.DistRic))
            if self.mod_Dist1 < self.mod_minDist:
                self.mod_minDist=self.mod_Dist1
                self.tca_c=self.epoca_ini
            self.epoca_ini=self.epoca_ini+timedelta(minutes=1)
            
            # Transformo a Coordenadas Geodesicas.
            delta1, alpha1=pos1.getCoordenadasGEOD()
            delta2, alpha2=pos2.getCoordenadasGEOD()
            # GUARDAR EN ARCHIVO Posiciones en TEME.
            salida1.write(str(alpha1)+' '+str(delta1)+' '+datetime.strftime(pos1.epoca,'%Y-%m-%d %H:%M:%S')+'\n')
            salida2.write(str(alpha2)+' '+str(delta2)+' '+datetime.strftime(pos2.epoca,'%Y-%m-%d %H:%M:%S')+'\n')
 
            # GUARDAR EN ARCHIVO Posiciones en TEME.
            salida3.write(datetime.strftime(pos1.epoca,'%Y-%m-%d %H:%M:%S')+' '+str(self.DistRic[0])+' '+str(self.DistRic[1])+' '+str(self.DistRic[2])+'\n')

        salida1.close()
        salida2.close()
        salida3.close()

#     
# if __name__=='__main__':
#     
# #     TCA=datetime(2008,1,9,19,0,30)
# #     sat_id='27386' #ENVISAT
# #     deb_id='15482' #COSMOS
# #     usuario='macecilia'
# #     clave='MaCeciliaSpace17'
# # 
# #     tle_sat=Tle(usuario,clave,sat_id,TCA)
# #     tle_deb=Tle(usuario,clave,deb_id,TCA)
# #     
# #     encuentro1=Encuentro(tle_sat,tle_deb,TCA)
# #     dif_r,dif_v=encuentro1.svDif()
#     
#     tle_archivo=Tle.creadoxArchivo(archivo='../TleAdmin/tle/37673tle0')
#     print tle_archivo.epoca()
    
    