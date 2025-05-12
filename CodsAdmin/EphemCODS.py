'''
Created on 17/03/2017

@author: mcvalenti
'''

from datetime import datetime

class EphemCODS():
    '''
    Facilita la manipulacion de los datos CODS.
    * Considera la informacion del nombre del archivo para saber el intervalo
    de fechas que incluye.
    * Genera un diccionario con cada linea del archivo: fecha: coordenadas y velocidades.
    '''
    def __init__(self, nombre_archivo):
        '''
        Constructor
        '''
        self.nombre_arch = nombre_archivo
        self.data={}

    def parsea_epoca_nombre(self):
        campos      = self.nombre_arch.split('_')
        self.anio   = campos[1][0:4]
        self.mes    = campos[1][4:6]
        self.dia    = campos[1][6:8]
        self.hora   = campos[2][0:2]
        self.minu    = campos[2][2:4]
        self.seg    = campos[2][4:6]
 #       self.epoca_archivo = datetime(self.anio,self.mes,self.dia,self.hora,self.minu,self.seg)
        
        return self.anio, self.mes, self.dia, self.hora, self.minu, self.seg
    
    def genera_diccionario(self):
        archivo=open(self.nombre_arch,'r')
        contenido=archivo.readlines()
        for c in contenido:
            c1=c.split()           
            if c1[0]=='*HEADER':
                continue
            fecha=c[:26]
            x=c1[2]
            y=c1[3]
            z=c1[4]
            vx=c1[5]
            vy=c1[6]
            vz=c1[7]
            self.epoca_ephem=datetime.strptime(fecha,'%Y/%m/%d %H:%M:%S.%f')
            self.data[self.epoca_ephem]={'x':x,'y':y,'z':z,'vx':vx,'vy':vy,'vz':vz}

        return self.data
    
if __name__=='__main__':
     
    archivo='CODS_20130602_135850_SACD_DENSEPHEM_TOD_XYZ_O.TXT'
    ephem=EphemCODS('../CodsAdmin/CUSS_CODS/DENSEPHEM_TOD_XYZ/'+archivo)
     
    ephem_dic=ephem.genera_diccionario()
    d1=datetime(2013,5,31,14,10,10)
    print (ephem_dic[d1]['x'])
      
         