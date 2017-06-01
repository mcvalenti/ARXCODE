'''
Created on 01/06/2017

@author: mcvalenti
'''
import numpy as np
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from sgp4.propagation import sgp4
from sgp4.ext import days2mdhms
from sgp4.ext import jday
from requests import session, exceptions
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
import TleAdmin

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
            r,v = satrec.propagate(ffin.year,ffin.month,ffin.day,ffin.hour,ffin.minute,ffin.second)
        else:
            segundos=date.second+date.microsecond/1000000.0
            r,v = satrec.propagate(date.year,date.month,date.day,date.hour,date.minute,segundos)
        return r,v

class Encuentro():
    
    def __init__(self,tle_sat,tle_deb,tca):
        
        self.tle_sat=tle_sat
        self.tle_deb=tle_deb
        self.tca=tca
        
    def svDif(self):
        """
        Calcula las diferencias relativas entre los dos 
        objetos.
        (agregar la diferencias en rtn)
        """
        self.dif_r=[]
        self.dif_v=[]
        
        self.epoca_ini=self.tca-timedelta(minutes=90)
        self.epoca_fin=self.tca+timedelta(minutes=10)
        self.epoca=self.epoca_ini
        
        """
        archivos de salida para graficar.
        """
        self.sat_id=self.tle_sat.catID()
        self.deb_id=self.tle_deb.catID()
        salida1=open('../Encuentro/archivos/'+self.sat_id,'w')
        salida2=open('../Encuentro/archivos/'+self.deb_id,'w')
        
        
        while self.epoca < self.epoca_fin:
            r,v=self.tle_sat.propagaTLE(self.epoca)
            r1,v1=self.tle_deb.propagaTLE(self.epoca)
    
            self.x=float(r[0])
            self.y=float(r[1])
            self.z=float(r[2])
            self.x1=float(r1[0])
            self.y1=float(r1[1])
            self.z1=float(r1[2])

            r=np.array([self.x,self.y,self.z])
            ve=np.array([float(v[0]),float(v[1]),float(v[2])])
            r1=np.array([self.x1,self.y1,self.z1])
            ve1=np.array([float(v1[0]),float(v1[1]),float(v1[2])])
            
            fila1=self.cart2geod(self.x,self.y,self.z)
            fila2=self.cart2geod(self.x1,self.y1,self.z1)
            salida1.write(fila1)
            salida2.write(fila2)
            
            self.dif_r.append(r-r1)
            self.dif_v.append(ve-ve1)
            print self.epoca,np.sqrt(np.dot(r-r1,r-r1))
            self.epoca=self.epoca+timedelta(minutes=1)
            
        
        return self.dif_r,self.dif_v
    
    def cart2geod(self,x,y,z):
        """
        Transforma coordenadas del sistem cartesiano (TEME)
        al sistema geodesico aprox. 
        """
        deg=np.divide(180,np.pi)
        r=np.sqrt(x*x+y*y+z*z)
        l=np.divide(x,r)
        m=np.divide(y,r)
        n=np.divide(z,r)
        delta=np.arcsin(n)
        if m>0:
            alpha = np.arccos(np.divide(l,np.cos(delta)))
        else:
            alpha = 2*np.pi-np.arccos(np.divide(l,np.cos(delta)))
        fila=str(alpha*deg)+' '+str(delta*deg)+'\n'
    
        return fila
    
    def minDistancia(self):
        self.dif_r,self.dif_v=self.svDif()
        self.minDist=np.sqrt(np.dot(self.dif_r,self.dif_r))
        return self.minDist
    
if __name__=='__main__':
    
#     TCA=datetime(2008,1,9,19,0,30)
#     sat_id='27386' #ENVISAT
#     deb_id='15482' #COSMOS
#     usuario='macecilia'
#     clave='MaCeciliaSpace17'
# 
#     tle_sat=Tle(usuario,clave,sat_id,TCA)
#     tle_deb=Tle(usuario,clave,deb_id,TCA)
#     
#     encuentro1=Encuentro(tle_sat,tle_deb,TCA)
#     dif_r,dif_v=encuentro1.svDif()
    
    tle_archivo=Tle.creadoxArchivo(archivo='../TleAdmin/tle/37673tle0')
    print tle_archivo.epoca()
    
    