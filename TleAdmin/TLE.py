"""
Created on Fri Jul  1 11:47:12 2016

Extrae la informacion de los TLE

@author: mcvalenti
"""

from sgp4.ext import days2mdhms
from sgp4.ext import jday
from datetime import datetime

class tle_info:
    
    def __init__(self,archivo):
        
        self.tle = open(archivo,'r')
        lineas = self.tle.readlines()
        self.linea1 = lineas[0].split()
        self.linea2 = lineas[1].split()
        self.tle.close() 
        self.i=self.linea2[2]
        self.Omega=self.linea2[3]
        self.e=self.linea2[4]
        self.ap=self.linea2[5]
        self.m=self.linea2[6]
        self.n=self.linea2[7]

    def catID(self):
        self.catID=self.linea1[1]
        return self.catID
        
    def epoca(self):
        self.fecha = str(self.linea1[3])  # Extraemos fecha del TLE
        self.anio = str(self.fecha[0:2])
        self.dias = str(self.fecha[2:14])
        self.a = int(self.anio)
        self.d = float(self.dias)
        self.mon, self.day, self.hr, self.minu, self.sec = days2mdhms(self.a,self.d)
        self.mes=int(self.mon)
        self.dia1=int(self.day)
        self.hora=int(self.hr)
        self.minuto=int(self.minu)
        self.seg=int(self.sec)
        self.jd1 = jday(self.a, self.mon, self.d, self.hr, self.minu, self.sec)
        self.epoca=datetime(2000+self.a, self.mes, self.dia1, self.hora, self.minuto, self.seg)
        return self.epoca
