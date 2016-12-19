'''
Created on 19/12/2016
Unifica en un unico archivo todos los archivos de GPS
ofrecidos por CODS. 
@author: mcvalenti
'''

import os, glob

lista=glob.glob('*')
for nombre in lista:
    fecha=nombre.split('.')[0]
    fecha1=fecha.split('d')[1]
    print fecha1
    print '\n'