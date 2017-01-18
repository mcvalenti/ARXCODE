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
    d=datetime(2013,12,31,10,12,00)
    print fechasgps[0]
    print fechasgps.index(d)
    """
    Metodo de biseccion para encontrar la coincidencia
    """
    tot=len(gpslista)
    print 'Total de filas de GPS = ',tot
    print 'Total de Tles = ', len(tlelista)
    for l in tlelista:
        print '---------------------------------------------------------------'
        print '------------------NUEVO TLE------------------------------------'
        print '---------------------------------------------------------------'
        campos=l.split()
        campos1=campos[0].split('-')
        yy=int(campos1[0])
        mm=int(campos1[1])
        dd=int(campos1[2])
        campos2=campos[1].split(':')
        hh=int(campos2[0])
        minu=int(campos2[1])
        segu=0
        d1=datetime(yy,mm,dd,hh,minu,segu)      
        print 'FECHA DEL TLE= ',d1
        if d1 < fechasgps[tot/2]:
            if d1 in fechasgps[:tot/4]:
                indice=fechasgps.index(d1)
                print 'Inferior = ',gpslista[indice]
                print 'Superior =', gpslista[indice-1]
            else:
                indice=fechasgps.index(d1)
                print 'Inferior = ',gpslista[indice]
                print 'Superior =', gpslista[indice-1]
        else:
            if d1 in fechasgps[:tot*3/4]:
                indice=fechasgps.index(d1)
                print 'Inferior = ',gpslista[indice]
                print 'Superior =', gpslista[indice-1]
            else:
                indice=fechasgps.index(d1)
                print 'Inferior = ',gpslista[indice]
                print 'Superior =', gpslista[indice-1]
             
    
    print 'FIN'
    
    