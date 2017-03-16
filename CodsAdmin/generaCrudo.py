'''
Created on 22/12/2016

Se encarga de ordenar y procesar los archivos TOD de CODS.
Finalmente genera un unico archivo que lista la informacion
en forma ordenada, con un unico sv (state vector) por fecha y epoca.

@author: mcvalenti
'''

import os, glob
from datetime import datetime
from gi.overrides.keysyms import Pause


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
    orden=0
    for nombre in lista:
        print 'ordenando fila = ', orden
        nombreCode = nombre.split('_')
        if nombre == lista[1164]:
             print 'dejame ver nombre', nombre
             break
        yy=int(nombreCode[2][0:4])
        mes=int(nombreCode[2][4:6])
        dia=int(nombreCode[2][6:8])
        hs=int(nombreCode[3][0:2])
        mi=int(nombreCode[3][2:4])
        seg=int(nombreCode[3][4:6])
        fecha = datetime(yy,mes,dia,hs,mi,seg)
        archCods[fecha]=nombre
        orden=orden+1
    codsOrdenados=sorted(archCods.items())
    return codsOrdenados

def generaTOD(lista):    
    ephemFile = open('TOD_O/TOD_CODS_SACD_xyz.txt','a')
    listafechas=[]
    claveUnica=' '
    m=0
    for i in TODlista:
        print 'Procesando archivo numero = ',m
        f=open(i[1],'r')
        contenido=f.readlines()
        contenido.reverse()
        for c in contenido:
            c1=c.split(' ')
            if c1[0]=='*HEADER':
                continue
            claveUnica=c1[0]+c1[1]
            if claveUnica in listafechas:
                continue
            ephemFile.write(c)
            listafechas.append(claveUnica)
        m=m+1

if __name__ == '__main__':  
    """
    Se listan los archivos TOD de CODS
    """
#    os.remove('TOD_O/TOD_CODS_SACD_xyz.txt')
    lista=glob.glob('TOD_O/*')
    print ('Cantidad de archivos a procesar= %s' % (len(lista)))
    """
    Se ordenan los archivos en una lista de listas.
    """
    TODlista=ordenaTOD(lista) 
    TODlista.reverse()
    
    generaTOD(TODlista)

    print 'FIN'


