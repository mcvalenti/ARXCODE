'''
Created on 26/05/2017

Parseo del CDM en formato XML.

@author: mcvalenti
'''
import xml.etree.ElementTree as ET


def extraeCMD(archivo):
    """
    Extrae los datos de un CDM en formato XML.
    inputs
        archivos: nombre de archivo CDM en formato .xml (string)
    Outputs
        TCA: tiempo de maximos acercamiento. (string)
        Obj1, Obj2: nombre de objetos implicados (string)
        miss_dist: minima distancia (string)
        poc: probabilidad de colision (string)
    """
    tree = ET.parse(archivo)
    root = tree.getroot()
    
    obj_m=[]
    obj_d=[]

    for bod in root.iter('body'):
        TCA=bod[0][1].text
        MISS_DISTANCE=bod[0][2].text
        POC=bod[0][14].text
        
    n=0    
    for meta in root.iter('metadata'):
        if n == 0:
            obj_m.append(meta[1].text)
            obj_m.append(meta[2].text)
        else:
            obj_d.append(meta[1].text)
            obj_d.append(meta[2].text)
        n=n+1

    obj_list=[obj_m,obj_d]    
    return TCA,MISS_DISTANCE,POC,obj_list
    
    
if __name__=='__main__':
    
    archivo='cdmTest.xml'
    TCA,MISS_DISTANCE,POC,obj_list=extraeCMD(archivo)
    """
    Impresion por pantalla.
    """
    info1='Acercamiento entre '+str(obj_list[0][0])+' y '+str(obj_list[1][0])
    print '=============================================================='
    print info1
    print '=============================================================='
    print 'Mision Id= ', str(obj_list[0][1])
    print 'Target Id= ', str(obj_list[1][1])
    print 'Tiempo de maximo acercamiento= ', TCA
    print 'Minima Distancia = ', MISS_DISTANCE
    print 'Probabilidad de Colision = ', POC