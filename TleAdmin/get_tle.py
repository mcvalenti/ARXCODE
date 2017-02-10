"""
Created on Tue Jul 12 14:21:56 2016

@author: curso
"""

from requests import session
from datetime import datetime

class importar_tle():
    
    def __init__(self, usuario,clave, cat_id,tca0,tca1):
        self.f          =open('../TleAdmin/crudosTLE/'+cat_id+'.txt','w')
        self.usuario    =usuario
        self.clave      =clave
        self.noradId    =cat_id
#         self.f0         =tca0
#         self.f1         =tca1
        self.anio0      =tca0.year
        self.mes0       =tca0.month
        self.dia0       =tca0.day        
        self.anio1      =tca1.year
        self.mes1       =tca1.month
        self.dia1       =tca1.day

        
#         self.f1=str(tca0.year())+'-'+str(tca0.month())+'-'+str(tca0.day())
#         self.f2=str(tca1.year())+'-'+str(tca1.month())+'-'+str(tca1.day())
#         self.fini=datetime.strftime(tca0,'%Y-%m-%d')
#         self.ffin=datetime.strftime(tca1,'%Y-%m-%d')



        self.tleDato=self.solicitudTle()
#        self.f.write(self.tleDato)
        print 'Se ha generado el archivo= ', cat_id,'.txt'

    def ConsultaAutentica(self):
        print 'Ingrese su Usuario: '
        usuario=raw_input()
        print 'Ingrese su Clave' # MaCeciliaSpace17
        clave= raw_input()
        data = {'identity': usuario, 'password': clave}
        return data
    
    def solicitudTle(self):
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
        s=session() 
        s.post('https://www.space-track.org/auth/login',data)
        fquery1='https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/2012-06-11--2012-06-15/NORAD_CAT_ID/37673/orderby/TLE_LINE1 ASC/format/tle'
        r = s.get(fquery1)
        s.close()
        return r.text
