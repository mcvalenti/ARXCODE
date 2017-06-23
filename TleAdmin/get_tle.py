"""
Created on Tue Jul 12 14:21:56 2016

@author: curso
"""
from requests import session, exceptions
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

class importarSetTLE():
    
    def __init__(self, usuario,clave, cat_id,tca0,tca1,archivo):
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

