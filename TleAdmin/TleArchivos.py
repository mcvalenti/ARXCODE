'''
Created on Sep 21, 2016
@author: mcvalenti
'''

def setTLE(id_sat,crudo):
    """
    Obtiene un dato con un listado de TLEs para todo un intervalo temporal.
    El mismo es para un satelite en particular.
    Esta funcion particiona el archivo en muchos archivos, uno por cada tle.
    Y los guarda en TleAdmin/tle
    """
    
    
    lista=open('../TleAdmin/crudosTLE/'+crudo,'r')
    filas=lista.readlines()
    largo=len(filas) # indicara la cantidad total de lineas
        
    
    m=0
    for i in range(0,largo-1,2):
        salida=open('../TleAdmin/tle/'+id_sat+'tle'+str(m),'w+')
        linea1=filas[i]
        linea2=filas[i+1]
        doslineas=linea1+linea2
        salida.write(doslineas)
        m=m+1
        salida.close()