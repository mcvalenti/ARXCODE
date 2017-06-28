'''
Created on 25 jun. 2017

Modulo para validar las funciones de generacion de matrices
mediante el metodo de Osweiler.

@author: ceci
'''
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
# sat_id='27642'
# ini_epoca=datetime(2003,3,1)
# fin_epoca=datetime(2003,3,16)
# crudo='27642_escenario51.setTle'
#===========================================================================
# ESCENARIO ICESAT(sat 5) 27642- ventana #5 (14 Feb 2004 - 29 Feb 2004)
#===========================================================================
sat_id='27642'
ini_epoca=datetime(2004,2,14)
fin_epoca=datetime(2004,2,29)
crudo='27642_escenario55.setTle'
#===========================================================================
# ESCENARIO ICESAT(sat 5) 27642- ventana #6 (5 Marzo 2004 - 20 Marzo 2004)
#===========================================================================
# sat_id='27642'
# ini_epoca=datetime(2004,3,5)
# fin_epoca=datetime(2004,3,21)
# crudo='27642_escenario56.setTle'


set_deb=SetTLE(sat_id,ini_epoca,fin_epoca,crudo)
set_deb.divide_setTLE()

tle0=Tle.creadoxArchivo('../TleAdmin/tle/27642tle0')
epoca0=tle0.epoca()
tle26=Tle.creadoxArchivo('../TleAdmin/tle/27642tle26')

r,v= tle26.propagaTle(epoca0)
print r
# data=difPrimario()
# print '********************************'
# nombre_archivo_sat,var_r_sat,var_t_sat,var_n_sat=calcula_matriz_Tles(sat_id,ini_epoca,fin_epoca,crudo)
#maCovar_sat, ma_archivo_sat=EjecutaMaCovar(data[3])

# for k in maCovar_sat[:3]:
#     print k[:3]

# print '********************************'
# print 'Varianza en R =', var_r_sat
# print 'Varianza en T =', var_t_sat  
# print 'Varianza en N =', var_n_sat
# print '********************************' 