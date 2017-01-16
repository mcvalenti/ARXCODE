'''
Created on 22/12/2016

Se encarga de ordenar y procesar los archivos TOD de CODS.
Finalmente genera un unico archivo que lista la informacion
en forma ordenada, con un unico sv (state vector) por fecha y epoca.

@author: mcvalenti
'''

import os, glob
import numpy as np
from datetime import datetime
from StateVector import StateVector


def ordenaTOD(lista):
    """
    ----------------------------------------------------------------------
    Recibe la lista de archivos de CODS y genera una lista que los 
    contiene ordenados segun las fechas
    ----------------------------------------------------------------------
    input
        lista: lista de archivos (list)
    output
        codsOrdenados: lista de lista ordenada (fecha, nombre de archivo)
    """
    archCods = {}
    for nombre in lista:
        nombreCode = nombre.split('_')
        yy=int(nombreCode[2][0:4])
        mes=int(nombreCode[2][4:6])
        dia=int(nombreCode[2][6:8])
        hs=int(nombreCode[3][0:2])
        mi=int(nombreCode[3][2:4])
        seg=int(nombreCode[3][4:6])
        fecha = datetime(yy,mes,dia,hs,mi,seg)
        archCods[fecha]=nombre
    codsOrdenados=sorted(archCods.items())
    return codsOrdenados

# for arch in lista:
#     datos=open(arch,'r').readlines()
#     print '-----------------------------------------------------------------------------'
#     print '-----------------------------------------------------------------------------'
#     print arch
#     for i in datos:
#         datos1=i.split(' ')
#         campos=len(datos1)
#         if datos1[0]=='*HEADER':
#             continue
#         sv1=StateVector(i)
#        print sv1.fecha, sv1.hora, sv1.x, sv1.y, sv1.z, sv1.vx, sv1.vy, sv1.vz


if __name__ == '__main__':  
    """
    Se listan los archivos TOD de CODS
    """
    os.remove('TOD_O/TOD_CODS_SACD_xyz.txt')
    lista=glob.glob('TOD_O/*')
    print ('Cantidad de archivos a procesar= %s' % (len(lista)))
    """
    Se ordenan los archivos en una lista de listas.
    """
    TODlista=ordenaTOD(lista) 
    TODlista.reverse()
    

    ephemFile = open('TOD_O/TOD_CODS_SACD_xyz.txt','a')
    
    nuevalista=[] 
    claveUnica=' '
    for i in TODlista:
        f=open(i[1],'r')
        contenido=f.readlines()
        for c in contenido:
            c1=c.split(' ')
            if c1[0]=='*HEADER':
                continue
            if claveUnica != c1[0]:
                nuevalista.append(c)
                claveUnica=c1[0]
            


