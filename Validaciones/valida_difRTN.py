'''
Created on 11/07/2017

@author: mcvalenti
'''
from datetime import datetime
from TleAdmin.TLE import Tle
from Encuentro.Encuentro import Encuentro

"""
Dados dos objetos cuyos identificadores se conocen
y un TCA entre ellos.
Se calculan las posiciones relativas en las componentes
RTN, para verificar la transformacion.
"""

# Escenario I - (EUMETSAT)
# sat_id='29499'
# deb_id='29096'
# TCA=datetime(2010,11,20,18,30,12,421*1000)
# min_d=0.187
# dr=0.0103
# dt=0.1028
# dn=0.1566
# poc=0.00343

# Escenario II - (MAIL 1 )
# sat_id='32789'
# deb_id='23657'
# TCA=datetime(2012,7,15,21,21,0,0)
# min_d=0.760
# dr=0.186
# dt=0.389
# dn=0.626

# Escenario III - (MAIL 2)
# sat_id='39417'
# deb_id='30189'
# TCA=datetime(2014,6,29,4,55,0,0)
# min_d=0.334
# dr=0.007
# dt=0.249
# dn=0.223

#==========================
# Valida Mails
#==========================

tabla_mails=open('../CDM/mails/tabla_mails','r')
contenido=tabla_mails.readlines()
n=3
mail=contenido[n]
linea_data=mail.split()
sat_id=linea_data[0]
deb_id=linea_data[1]
TCA=linea_data[2]
dr=linea_data[3]
dt=linea_data[4]
dn=linea_data[5]
min_dist=linea_data[6]
var_r_sat=linea_data[7]
var_t_sat=linea_data[8]
var_n_sat=linea_data[9]
var_r_deb=linea_data[10]
var_t_deb=linea_data[11]
var_n_deb=linea_data[12]

tca_epoca=datetime.strptime(TCA,"%Y-%m-%dT%H:%M")
tle_sat=Tle.creadoxParam(sat_id, tca_epoca)
tle_deb=Tle.creadoxParam(deb_id, tca_epoca)

n=0
encuentro=Encuentro(tle_sat,tle_deb,tca_epoca,n)
print 'TCA calculado = ', encuentro.tca_c
print 'Minima distancia total = ', encuentro.mod_minDist
print 'Minima Distancia RTN = ', encuentro.DistRic_min




