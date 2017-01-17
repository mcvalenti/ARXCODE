'''
Created on 17/01/2017

@author: mcvalenti
'''
import os, glob
from datetime import datetime
from AjustarTLE.AjustarTLE import seleccionSat
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import tle_info


"""
Busca Crudo TLE con el listado total de TLEs del intervalo a comparar.
Genera un archivo por TLE: TleAdmin/TleArchivos/setTLE
Propaga cada TLE para obtener los r,v: TleAdmin/TLE/propagaTLE
Guarda las fechas de los TLE
Busca las dos fechas CODS que encierren a los TLEs
Interpola los valores x,y,z de los datos CODS
Hace las diferencias
Grafica
"""
def generaTEME(tles):
    listaTle={}
    for i in tles:
        tle1=tle_info(i)
        fecha=tle1.epoca()
        r,v=tle1.propagaTLE()
        listaTle[fecha]=str(r[0])+' '+str(r[1])+' '+str(r[2])+' '+str(v[0])+' '+str(v[1])+' '+str(v[2])
    listaTle=sorted(listaTle.items())
    salidaTle=open('../TleAdmin/tle/TEME_SGP4_SACD_xyz.txt','a')
    for k in listaTle:        
        infoa=str(k[0])
        infob=k[1]
        linea=infoa+' '+infob+'\n'
        salidaTle.write(linea)
    
    
    
    
    
if __name__ == '__main__':   
    """
    Borro los archivos generados para otro satelite.
        carpeta de tles: TleAdmin/tle
        carpeta de diferencias: AjustarTLE/diferencias
        carpeta de graficos: Visual/graficos
    """
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
        
    seleccionSat()
    tles = glob.glob('../TleAdmin/tle/*')
    generaTEME(tles) # ver de mover a TleAdmin
    
    """
    Comparacion
    """
    
    gpsf=open('../CodsAdmin/TOD_O/TOD_CODS_SACD_xyz.txt','r')
    tlef=open('../TleAdmin/tle/TEME_SGP4_SACD_xyz.txt','r')
    
    gpslista=gpsf.readlines()
    tlelista=tlef.readlines()
    
    fechasgps=[]
    for fg in gpslista:
        campof=fg.split()
        fechas=campof[0]+' '+campof[1]
        dg=datetime.strptime(fechas[:19],'%Y/%m/%d %H:%M:%S')
        fechasgps.append(dg)
    
    for l in tlelista:
        campos=l.split()
        d=datetime.strptime(campos[0]+' '+campos[1],'%Y-%m-%d %H:%M:%S')            
        for i in range(len(gpslista)):
            if fechasgps[i] > d:
                print 'hay que seguir'
            else:
                print d,fechasgps[0]
    
    
    print 'FIN'
    
    