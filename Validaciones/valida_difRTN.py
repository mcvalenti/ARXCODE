'''
Created on 11/07/2017

@author: mcvalenti
'''
import sys
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import datestr2num
from TleAdmin.TLE import Tle
from SistReferencia.sist_deCoordenadas import ricSis
from Encuentro.Encuentro import Encuentro

"""
Para cada una de las situaciones ejemplo
calcula la Min Dist. y la PoC. 
Luego imprime las diferencias entre lo calculado
y publicado. 
"""
#==================================================
# Kilnkrad tabla (pag 236)
#==================================================
#ESCENARIO #4 
# sat_id='27386'
# deb_id='12442'
# TCA=datetime(2004,9,2,19,14,11,0)
# min_d=1.297
# dr='xxx'
# dt='xxx'
# dn='xxx'
# poc_p=0.0002186

# ESCENARIO #5
# sat_id='23560'
# deb_id='16681'
# TCA=datetime(2004,9,29,23,56,02,0)
# min_d=0.067
# dr='xxx'
# dt='xxx'
# dn='xxx'
# poc_p=0.0001546

#Flohrer Krag Klinkrad - (ENVI - COSMOS)
# sat_id='27386'
# deb_id='15482'
# TCA=datetime(2008,1,9,19,0,29,5)
# min_d=0.300
# dr=0.0103
# dt=0.1028
# dn=0.1566
# poc=0.00343

#==================================================
# Xu - Xiong - Method for calculating probability
# of collision between space objects.
#==================================================
# linea 1
# sat_id='25415'
# deb_id='31445'
# TCA=datetime(2013,3,18,14,44,34,0)
# min_d=0.115
# dr='xxx'
# dt='xxx'
# dn='xxx'
# poc_p=0.0000124

# linea 2
# sat_id='20737'
# deb_id='20738'
# TCA=datetime(2013,3,17,10,39,31,0)
# min_d=0.104
# dr='xxx'
# dt='xxx'
# dn='xxx'
# poc_p=0.0000017

# linea 3
# sat_id='27939'
# deb_id='31588'
# TCA=datetime(2013,3,16,13,46,21,0)
# min_d=0.098
# dr='xxx'
# dt='xxx'
# dn='xxx'
# poc_p=0.0000301

# linea 4
sat_id='11308'
deb_id='32315'
TCA=datetime(2013,3,15,03,02,16,0)
min_d=0.094
dr='xxx'
dt='xxx'
dn='xxx'
poc_p=0.000018

# linea 5
# sat_id='17583'
# deb_id='37442'
# TCA=datetime(2013,3,16,14,02,50,0)
# min_d=0.039
# dr='xxx'
# dt='xxx'
# dn='xxx'
# poc_p=0.0000939

#==================================================

# Escenario I - (EUMETSAT)
# sat_id='29499'
# deb_id='29096'
# TCA=datetime(2010,11,20,18,30,12,421*1000)
# min_d=0.187
# dr=0.0103
# dt=0.1028
# dn=0.1566
# poc=0.00343

# Escenario LAPORTE.
# sat_id='36036'
# deb_id='34907'
# TCA='2015-02-21T7:07'
# min_d=0.944
# dr=0.003
# dt=0.849
# dn=0.413
# poc=0.0014
#=========================
# MAILS
#=========================
# Escenario II - (MAIL 1 )
# sat_id='32789'
# deb_id='23657'
# TCA=datetime(2012,7,15,21,21,51,0)
# min_d=0.760
# dr=0.186
# dt=0.389
# dn=0.626

# Escenario III - (MAIL 2)
# sat_id='39417'
# deb_id='30189'
# TCA=datetime(2014,6,29,4,55,59,0)
# min_d=0.334
# dr=0.007
# dt=0.249
# dn=0.223

# Escenario IV - (MAIL 3)
# sat_id='24278'
# deb_id='10470'
# TCA=datetime(2012,11,23,23,38,42,0)
# min_d=0.984
# dr=0.174
# dt=0.690
# dn=0.680

# Escenario V - (MAIL 4)
# sat_id='32789'
# deb_id='24097'
# TCA=datetime(2013,3,31,3,25,45,0)
# min_d=0.783
# dr=0.096
# dt=0.006
# dn=0.783

# Escenario VI - (MAIL 5) - No existen los datos en NORAD
# sat_id='38081'
# deb_id='19336'
# TCA=datetime(2013,5,2,17,12,2,0)
# min_d=0.170
# dr=0.138
# dt=0.030
# dn=0.096

#=========================
# CDM
#=========================
# MENSAJE # 1                    
# sat_id='24793'
# deb_id='27646'
# TCA=datetime(2013,01,10,9,59,57,0)
# min_d=0.17
# dr=-0.1638  
# dt=-0.0222
# dn=-0.0404 

# MENSAJE # 2                                        
# sat_id='25273'
# deb_id='31279'
# TCA=datetime(2013,01,12,0,20,51,0)
# min_d=0.175 
# dr=0.1701
# dt=0.0122
# dn=0.0424

# MENSAJE # 5
# sat_id='28810'
# deb_id='33315'
# TCA=datetime(2012,11,22,13,3,44,823)
# min_d=0.976
# dr=0.0661 
# dt=-0.2413 
# dn=-0.9443

# MENSAJE # 6                                                          
# sat_id='38755'
# deb_id='34115'
# TCA=datetime(2012,12,26,5,0,41,0)
# min_d= 0.617  
# dr=-0.0825 
# dt=-0.0509
# dn=0.6094   

# MENSAJE # 7                                                          
# sat_id='24903'
# deb_id='33759'
# TCA=datetime(2013,01,10,13,22,45)
# min_d= 0.18
# dr=0.0359
# dt=-0.1488
# dn=0.0957

# MENSAJE # 8                                        
# sat_id='27372'
# deb_id='31413'
# TCA=datetime(2013,01,11,5,30,55,0)
# min_d= 0.15
# dr=-0.1191 
# dt=0.0003  
# dn=0.092
   
   
#tca_epoca=datetime.strptime(TCA,"%Y-%m-%dT%H:%M")
tle_sat=Tle.creadoxParam(sat_id, TCA)
tle_deb=Tle.creadoxParam(deb_id, TCA)

n=3
encuentro=Encuentro(tle_sat,tle_deb,TCA,n)

rtn_dist=encuentro.DistRic_min
set_data=encuentro.tca_min_data
poc, poc_int=encuentro.calculaPoC_circ()

# #==============================
# # PLOTEO
# #==============================
# """
# Gestion de Fechas
# """

# dt=[]
# fecha0=set_data[0][0]
# for fecha in set_data[0]:
#     dt.append((fecha-fecha0).total_seconds())
# plt.ylim(-3,3)
# plt.title('Acercamiento ENVI vs COSMOS 2008/01/09 - 19:00:29')
# plt.ylabel('Km')
# plt.xlabel('Segundos')
# plt.grid()
# plt.plot(dt, set_data[1], 'r-', label='Minima Distancia')
# plt.show()


print '**************************************************'
print 'Calculado'
print '**************************************************'
print 'TCA calculado = ', encuentro.tca_c
print 'Minima distancia total = ', round(encuentro.mod_minDist,6)
print 'Minima Distancia RTN = ', round(rtn_dist[0],6), round(rtn_dist[1],6), round(rtn_dist[2],6)
print 'PoC calculada =', round(poc,6), round(poc_int,6)
print '**************************************************'
print 'Publicado'
print '**************************************************'
print 'TCA publicado = ',TCA
print 'Minima distancia total = ',min_d
print 'Minima Distancia RTN = ',dr,dt,dn
print 'PoC publicada =', poc_p
