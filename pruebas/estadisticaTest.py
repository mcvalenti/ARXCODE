'''
Created on 15/02/2017

@author: mcvalenti
'''
import numpy as np
# from Estadistica.maCovar import EjecutaMaCovar
# 
# EjecutaMaCovar('dif_sat29268.txt')

a=[2,3]
ma=np.mean(a)
b=np.sqrt(np.dot(a-ma,a-ma)/len(a))
varianza=np.var(a)
desviacion=np.std(a)

print b, desviacion