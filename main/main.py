'''
Created on 26/01/2017

@author: mcvalenti
'''
import os

"""
listar las epocas de todos los tles.
interpolar el sv de cods para esas fechas
ordenarlas de mayor a menor
reproducir el metodo de Osweiler tomando como  dato el sv interpolado
"""



if __name__ == '__main__':
    
    """
    Se crean los directorios necesarios.
    """
    
    d1='../TleAdmin/tle'
    if not os.path.exists(d1):
        os.mkdir(d1)
    d2='../AjustarTLE/diferencias'
    if not os.path.exists(d2):
        os.mkdir(d2)
    d3='../main/matrices/'
    if not os.path.exists(d3):
        os.mkdir(d3)
    d4='../visual/archivos'
    if not os.path.exists(d4):
        os.mkdir(d4)


    print 'FIN'