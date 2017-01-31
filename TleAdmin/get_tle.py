"""
Created on Tue Jul 12 14:21:56 2016

@author: curso
"""

from requests import session
from datetime import datetime

class importar_tle():
    
    def __init__(self, cat_id,tca0,tca1):
        self.f=open(cat_id+'.txt','w')
        self.noradId=cat_id
        self.epoca=tca0
        self.fini=datetime.strftime(tca0,'%Y-%m-%d')
        self.ffin=datetime.strftime(tca1,'%Y-%m-%d')
        self.tleDato=self.solicitudTle()
        self.f.write(self.tleDato)
        print 'Se ha generado el archivo= ', cat_id,'.txt'

    def ConsultaAutentica(self):
        print 'Ingrese su Usuario: '
        usuario=raw_input()
        print 'Ingrese su Clave' # MaCeciliaSpace17
        clave= raw_input()
        data = {'identity': usuario , 'password': clave}
        return data
    
    def solicitudTle(self):
        data = self.ConsultaAutentica()
        s=session() 
        s.post('https://www.space-track.org/auth/login',data)
        f1='2013-03-01'
        f2='2013-03-03'
        fquery1='https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/'+f1+'--'+f2+'/NORAD_CAT_ID/37673/orderby/TLE_LINE1 ASC/format/tle'
        r = s.get(fquery1)
        return r.text
