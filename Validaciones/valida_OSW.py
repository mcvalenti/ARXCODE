'''
Created on 25 jun. 2017

Modulo para validar las funciones de generacion de matrices
mediante el metodo de Osweiler.

@author: ceci
'''
from datetime import datetime
from Estadistica.matrizOsweiler import calcula_matriz_Tles
from Estadistica.maCovar import EjecutaMaCovar

"""
Toma los set de Tles de la bibliografia del trabajo de 
Osewiler y valida el metodo para el calculo de la matriz. 
"""

#===========================================================================
# -------- ESCENARIO ICESAT 27642- ventana ... 1 ...
#===========================================================================
sat_id='27642'
ini_epoca=datetime(2003,3,1)
fin_epoca=datetime(2003,3,16)
crudo='27642_escenario51.setTle'

nombre_archivo_sat,var_r_sat,var_t_sat,var_n_sat=calcula_matriz_Tles(sat_id,ini_epoca,fin_epoca,crudo)
maCovar_sat, ma_archivo_sat=EjecutaMaCovar(nombre_archivo_sat)

print '*******************************************************'
print '-----------------Varianzas MISION---------------------------'
print '*******************************************************'
print 'Var en R = ', var_r_sat
print 'Var en T = ', var_t_sat
print 'Var en N = ', var_n_sat
print '*******************************************************'
print '-----------------Ma. MISION---------------------------'
print '*******************************************************'
for k in maCovar_sat[:3]:
    print k[:3]
    