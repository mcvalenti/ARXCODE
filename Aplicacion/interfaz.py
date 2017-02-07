'''
Created on 26/01/2017

@author: mcvalenti
'''
import glob
import numpy as np

def listarCrudos():
    """
    Seleccion de satelite y ventana de evaluacion.
    """
    
    satelites_datos=glob.glob('../main/DATOS/*')
    nombres=[]
    for arch in satelites_datos:
        nombre_archivo=arch.split('/')[-1]
        nombres.append(nombre_archivo)

    return nombres

def Resultado():
    """
    Genera un csv con el resultado e
    Imprime en pantalla la ventana el resultado.
    """
    M=np.array([[1,2,3],[4,5,6],[7,8,8]])