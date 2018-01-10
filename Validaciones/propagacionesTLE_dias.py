'''
Created on 17/07/2017

@author: mcvalenti
'''
import glob
from datetime import datetime
from TleAdmin.TLE import SetTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle
from visual.ploteos import grafica_diferenciasTotales

"""
Modulo que propaga y grafica las diferencias
de los TLE agrupadas por dia. (Osweiler bines).

* generar el crudo de TLEs para ICESAT Y LAGEOS
* correr uno por uno los escenarios.
* generar lista de TLEordenados, cantidad_tle
* llamar a la funcion difTLE (AjustarTLE)
"""

#===================================================
# Escenario ICESAT
#===================================================
# sat_id='27642'
# ini_epoca=datetime(2003,3,20)
# fin_epoca=datetime(2003,4,3)
# crudo='27642_escenario52.setTle'

#===================================================
# Escenario LAGEOS
#===================================================
sat_id='8820'
ini_epoca=datetime(2003,3,1)
fin_epoca=datetime(2003,3,16)
crudo='8820_escenario11.setTle'
#===================================================
# Escenario SAC-D #7 - Ventana 1
#===================================================
# sat_id='37673'
# ini_epoca=datetime(2013,4,1)
# fin_epoca=datetime(2013,4,16)
# crudo='37673_escenario71.setTle'

set_sat=SetTLE(sat_id,ini_epoca,fin_epoca,crudo)
set_sat.divide_setTLE()

# prepara los datos para generar las diferencias
lista_tle=glob.glob('../TleAdmin/tle/*') # extrae los tle de la carpeta
dic_tle=generadorDatos(lista_tle) # genera un diccionario con las fechas
tle_ordenados=ordenaTles(dic_tle) # ordena segun las fechas
cant_tle=len(lista_tle)
#======================================
# Genera las diferencias.
#======================================
bin, data, dataPri, coef1 = difTle(tle_ordenados, cant_tle) 
# [AjustarTLE/diferencias/difTotal_satID_fechaIni#]
# data: lista de listas, [dt_frac,dv,dn,dc]
#======================================
# Grafico
#======================================
path='../AjustarTLE/diferencias'
grafica_diferenciasTotales(sat_id,path,data[1],coef1)
