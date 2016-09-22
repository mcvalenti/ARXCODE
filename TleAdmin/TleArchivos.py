'''
Created on Sep 21, 2016

@author: mcvalenti
'''
from os import listdir

archivos=listdir('../tles_cods')

diezarchivos=archivos[0:10]

for k in diezarchivos:
    print k, type(k)
#    lineas=open('../tle_cods/'+k,'r')
#    lineas1=file.readlines()

