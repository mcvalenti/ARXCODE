"""
Created on Fri Jul  1 11:47:12 2016

Extrae la informacion de los TLE

@author: mcvalenti
"""
import os,glob
from datetime import datetime
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from requests import session, exceptions
from datetime import timedelta
from Aplicacion.globals import clave, usuario

class Tle:
    @classmethod
    def creadoxParam(cls,sat_id,epocaf):
        """
        Descarga el TLE correspondiente a la epoca que
        se le ingresa.
        Nota:toma como epoca final un dia despues por como 
        ofrece las descargas Space-track.
        """
        inst1=cls()
        inst1.noradId=sat_id
        inst1.anio0=epocaf.year
        inst1.mes0=epocaf.month
        inst1.dia0=epocaf.day
        epocaf=epocaf+timedelta(days=1)
        inst1.anio1=epocaf.year
        inst1.mes1=epocaf.month
        inst1.dia1=epocaf.day
        inst1.usuario=usuario
        inst1.clave=clave
        
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
            data = {'identity': inst1.usuario , 'password': inst1.clave}
            s=session() 
            s.post('https://www.space-track.org/auth/login',data)
            inst1.tle_text=''
            cont=0
            while inst1.tle_text=='':
                fquery1='https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/'+inst1.f0+'--'+inst1.f1+'/NORAD_CAT_ID/'+inst1.noradId+'/orderby/TLE_LINE1 ASC/format/tle'
                r = s.get(fquery1)
                inst1.tle_text=r.text
                inst1.lineas=inst1.tle_text.split('\n')
                inst1.f0=datetime.strptime(inst1.f0,'%Y-%m-%d')-timedelta(days=1)
                inst1.f0=datetime.strftime(inst1.f0,'%Y-%m-%d')
                cont=cont+1
            if cont > 1:
                    print 'El proceso cambio la fecha inicial del set = ', inst1.f0
            fquery1='https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/'+inst1.f0+'--'+inst1.f1+'/NORAD_CAT_ID/'+inst1.noradId+'/orderby/TLE_LINE1 ASC/format/tle'
            r = s.get(fquery1)
            inst1.tle_text=r.text
            inst1.lineas=inst1.tle_text.split('\n')
            if len(inst1.lineas) > 1 and r.status_code == 200:
                print 'Se ha generado el tle para el objeto de NORAD_ID= ',inst1.noradId
                inst1.linea1=inst1.lineas[-3]
                inst1.linea2=inst1.lineas[-2]
            else:
                print 'No pudo completarse la solicitud para el objeto de NORAD_ID= ',inst1.noradId                      
    
        except exceptions.HTTPError as e:
            print "Error: " + str(e)
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
#        self.catID=self.linea1.split()[1]
        return self.linea1.split()[1] #self.catID
        
    def epoca(self):
        whichconst = wgs72
        satrec = twoline2rv(self.linea1, self.linea2, whichconst)
        return satrec.epoch
    
    def propagaTLE(self,date=None):
        whichconst = wgs72
        satrec = twoline2rv(self.linea1, self.linea2, whichconst)
        if date==None:
            ffin=satrec.epoch
            r,v = satrec.propagate(ffin.year,ffin.month,ffin.day,ffin.hour,ffin.minute,ffin.second)
        else:
            #segundos=date.second+date.microsecond/100000.0
            r,v = satrec.propagate(date.year,date.month,date.day,date.hour,date.minute,date.second)
        return r,v
    
    
class SetTLE():
    
    def __init__(self,cat_id,tca0,tca1,archivo):
        """
        ----------------------------------------------------------------------
        Hace el Request de los TLEs a Space-Track de NORAD.
        ----------------------------------------------------------------------
        input:
            usuario: usuario del operador en Space-Track - (string)
            clave: clave del operador en Space-Track - (string)
            cat_id: numero de catalogo del Objeto en la base NORAD -(string)
            tca0: fecha de inicio del intervalo de analisis - (datetime)
            tca1: fecha de fin del intervalo de analisis - (datetime)
        output:
            xxxx.txt: archivo con los datos crudos (TleAdmin/crudosTLE/.)
        """
        
        self.noradId=cat_id
        self.anio0=tca0.year
        self.mes0=tca0.month
        self.dia0=tca0.day
        self.anio1=tca1.year
        self.mes1=tca1.month
        self.dia1=tca1.day
        self.usuario=usuario
        self.clave=clave
        self.archivo=archivo
        self.tleDato=self.solicitudTle()
        self.f=open('../TleAdmin/crudosTLE/'+archivo,'w')
        self.f.write(self.tleDato)
        self.f.close()
        

    def ConsultaAutentica(self):
        usuario=self.usuario
        clave=self.clave
        data = {'identity': usuario , 'password': clave}
        return data
    
    def solicitudTle(self):
        try:
            self.sincero=[self.mes0,self.mes1,self.dia0,self.dia1]
            i=0
            for i in range(len(self.sincero)):           
                if self.sincero[i] < 10:
                    self.sincero[i]='0'+str(self.sincero[i])
                i= i+1
            self.sincero=[str(self.sincero[0]),str(self.sincero[1]),str(self.sincero[2]),str(self.sincero[3])]
            self.f0=str(self.anio0)+'-'+self.sincero[0]+'-'+self.sincero[2]
            self.f1=str(self.anio1)+'-'+self.sincero[1]+'-'+self.sincero[3]
            print self.f0, self.f1
            data = self.ConsultaAutentica()
    #        data = {'identity': 'macecilia' , 'password': 'MaCeciliaSpace17'}
            s=session() 
            s.post('https://www.space-track.org/auth/login',data)
            fquery1='https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/'+self.f0+'--'+self.f1+'/NORAD_CAT_ID/'+self.noradId+'/orderby/TLE_LINE1 ASC/format/tle'
            r = s.get(fquery1)
            if r.text !='' and r.status_code == 200:
                print 'Se ha generado el archivo= ', self.archivo
            else:
                print 'No pudo completarse la solicitud'
            
        except exceptions.HTTPError as e:
            return "Error: " + str(e)
          
        return r.text
    
    def divide_setTLE(self):
        """
        Obtiene un dato con un listado de TLEs para todo un intervalo temporal.
        El mismo es para un satelite en particular.
        Esta funcion particiona el archivo en muchos archivos, uno por cada tle.
        Y los guarda en TleAdmin/tle
        """
        files=glob.glob('../TleAdmin/tle/*')
        for filename in files:
            os.unlink(filename)
        
        lista=open('../TleAdmin/crudosTLE/'+self.archivo,'r')
        filas=lista.readlines()
        largo=len(filas) # indicara la cantidad total de lineas
            
        
        m=0
        for i in range(0,largo-1,2):
            salida=open('../TleAdmin/tle/'+self.noradId+'tle'+str(m),'w+')
            linea1=filas[i]
            linea2=filas[i+1]
            doslineas=linea1+linea2
            salida.write(doslineas)
            m=m+1
            salida.close()