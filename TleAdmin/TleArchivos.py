'''
Created on Sep 21, 2016
@author: mcvalenti
'''
#from os import listdir
#import shutil

lista=open('cods/tlesSACDNov13Feb14','r')
filas=lista.readlines()
total=len(filas)/2 # indicara el total de archivos, o tles, cada uno con dos lineas.
largo=len(filas) # indicara la cantidad total de lineas

m=0
for i in range(0,largo,2):    
    salida=open('tle/tle'+str(m),'w')
    linea1=filas[i]
    linea2=filas[i+1]
    doslineas=linea1+linea2
    salida.write(doslineas)
    m=m+1

#shutil.rmtree('../tles', ignore_errors=False, onerror=None)
#===============================================================================
# archivos=listdir('cods')
# diezarchivos=archivos[0:10]
# 
# for k in diezarchivos:
#     origen = 'cods/' + k
#     destino = 'tle/' + k
#     print origen, destino
#     shutil.copy2(origen, destino)
#===============================================================================

