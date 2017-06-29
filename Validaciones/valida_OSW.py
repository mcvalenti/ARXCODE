'''
Created on 25 jun. 2017

Modulo para validar las funciones de generacion de matrices
mediante el metodo de Osweiler.

@author: ceci
'''
import numpy as np
from datetime import datetime
from TleAdmin.TLE import Tle,SetTLE
from AjustarTLE.AjustarTLE import difPrimario
from Estadistica.matrizOsweiler import calcula_matriz_Tles
from Estadistica.maCovar import EjecutaMaCovar

"""
Toma los set de Tles de la bibliografia del trabajo de 
Osewiler y valida el metodo para el calculo de la matriz. 
"""

#===========================================================================
# ESCENARIO ICESAT(sat 5) 27642- ventana #1 (1 Marzo 2003 - 16 Marzo 2003)
#===========================================================================
sat_id='27642'
ini_epoca=datetime(2003,3,1)
fin_epoca=datetime(2003,3,16)
crudo='27642_escenario51.setTle'
#===========================================================================
# ESCENARIO ICESAT(sat 5) 27642- ventana #5 (14 Feb 2004 - 29 Feb 2004)
#===========================================================================
# sat_id='27642'
# ini_epoca=datetime(2004,2,14)
# fin_epoca=datetime(2004,2,29)
# crudo='27642_escenario55.setTle'
#===========================================================================
# ESCENARIO ICESAT(sat 5) 27642- ventana #6 (5 Marzo 2004 - 20 Marzo 2004)
#===========================================================================
# sat_id='27642'
# ini_epoca=datetime(2004,3,5)
# fin_epoca=datetime(2004,3,20)
# crudo='27642_escenario56.setTle'


set_deb=SetTLE(sat_id,ini_epoca,fin_epoca,crudo)
set_deb.divide_setTLE()

print '********************************'
nombre_archivo_sat,var_r_sat,var_t_sat,var_n_sat=calcula_matriz_Tles(sat_id,ini_epoca,fin_epoca,crudo)
maCovar_sat, ma_archivo_sat=EjecutaMaCovar(nombre_archivo_sat)

l1=[maCovar_sat[0][0],maCovar_sat[0][1],maCovar_sat[0][2]]
l2=[maCovar_sat[1][0],maCovar_sat[1][1],maCovar_sat[1][2]]
l3=[maCovar_sat[2][0],maCovar_sat[2][1],maCovar_sat[2][2]]

for k in maCovar_sat[:3]:
    print k[:3]
# 
# print '********************************'
# print 'Varianza en R =', var_r_sat
# print 'Varianza en T =', var_t_sat  
# print 'Varianza en N =', var_n_sat
# print '********************************' 

#=========================================================
# Matrices de validacion
#=========================================================
#Ventana 1
linea1=np.array([2667.377375,27.248658,-8.222212216])
linea2=np.array([27.248658,0.343232694,-0.123143789])
linea3=np.array([-8.222212216,-0.123143789,0.073164435])
osw1=np.array([linea1,linea2,linea3])
print '********************************'
for k in osw1:
    print k[:3]
#DIFERENCIA
dif_l1=l1-linea1
dif_l2=l2-linea2
dif_l3=l3-linea3
dif_vent1=np.array([dif_l1,dif_l2,dif_l3])
print '********************************'
for k in dif_vent1:
    print k[:3]
# Porcentajes
por=dif_l1[0]/2667.377375
print por
#==============
# Ventana 5
#==============
# linea15=np.array([7681.2499484,125.8222111,17.34549846])
# linea25=np.array([125.8222111,2.130025404,0.272198739])
# linea35=np.array([17.34549846,0.272198739,0.044290481])
# osw5=np.array([linea15,linea25,linea35])
# for k in osw5:
#     print k[:3]
# #DIFERENCIA
# dif_l1=l1-linea15
# dif_l2=l2-linea25
# dif_l3=l3-linea35
# dif_vent1=np.array([dif_l1,dif_l2,dif_l3])
# for k in dif_vent1:
#     print k[:3]
#==============
# Ventana 6
#==============
# print '********************************'
# linea16=np.array([2189.869023,1.63345356,5.507059425])
# linea26=np.array([1.63345356,0.310134944,-0.066750327])
# linea36=np.array([5.507059425,-0.066750327,0.077123])
# osw6=np.array([linea16,linea26,linea36])
# #DIFERENCIA
# dif_l1=l1-linea16
# dif_l2=l2-linea26
# dif_l3=l3-linea36
# dif_vent6=np.array([dif_l1,dif_l2,dif_l3])
# for k in dif_vent6:
#     print k[:3]