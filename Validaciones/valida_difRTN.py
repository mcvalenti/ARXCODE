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
Dados dos objetos cuyos identificadores se conocen
y un TCA entre ellos.
Se calculan las posiciones relativas en las componentes
RTN.
"""
#Flohrer Krag Klinkrad - (ENVI - COSMOS)
# sat_id='27386'
# deb_id='15482'
# TCA=datetime(2008,1,9,19,0,29,5)
# min_d=0.300
# dr=0.0103
# dt=0.1028
# dn=0.1566
# poc=0.00343

# Escenario I - (EUMETSAT)
# sat_id='29499'
# deb_id='29096'
# tca_epoca=datetime(2010,11,20,18,30,12,421*1000)
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

# Escenario IV - (MAIL 3)
# sat_id='24278'
# deb_id='10470'
# TCA=datetime(2012,11,23,23,38,0,0)
# min_d=0.984
# dr=0.174
# dt=0.690
# dn=0.680

# Escenario V - (MAIL 4)
# sat_id='32789'
# deb_id='24097'
# TCA=datetime(2013,3,31,3,24,0,0)
# min_d=0.783
# dr=0.096
# dt=0.006
# dn=0.783

# Escenario VI - (MAIL 5) - No existen los datos en NORAD
# sat_id='38081'
# deb_id='19363'
# TCA=datetime(2013,5,5,17,12,0,0)
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
sat_id='25273'
deb_id='31279'
TCA=datetime(2013,01,12,0,20,51,0)
min_d=0.175 
dr=0.1701
dt=0.0122
dn=0.0424
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


  
#tca_epoca=datetime.strptime(TCA,"%Y-%m-%dT%H:%M")
tle_sat=Tle.creadoxParam(sat_id, TCA)
tle_deb=Tle.creadoxParam(deb_id, TCA)

n=2
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
# -------------------------------
# Prueba de ajuste de posiciones
# -------------------------------
# mod_minDist=sys.float_info.max
# ajuste=np.array([0.055976182388,0.0469271749738,0.0274533794103])
# TCA_ini=TCA-timedelta(seconds=3)
# TCA_fin=TCA+timedelta(seconds=3)
# fecha0_calculado=[]
# dist_calcualda=[]
# while TCA_ini <= TCA_fin:
#     r_sat,v_sat=tle_sat.propagaTLE(TCA_ini)
#     r_deb,v_deb=tle_deb.propagaTLE(TCA_ini)
#     r=np.array([float(r_sat[0]),float(r_sat[1]),float(r_sat[2])])
#     v=np.array([float(v_sat[0]),float(v_sat[1]),float(v_sat[2])])
#     r1=np.array([float(r_deb[0]),float(r_deb[1]),float(r_deb[2])])
#     v1=np.array([float(v_deb[0]),float(v_deb[1]),float(v_deb[2])])
#     # Diferencias
#     dist_pos=r1-r
#     dist_vel=v1-v
#     x_ric,y_ric,z_ric=ricSis(r,v,dist_pos)  # centro en satelite          
#     DistRic=np.array([x_ric,y_ric,z_ric])
#     mod_Dist1=np.sqrt(np.dot(DistRic,DistRic))
#     if mod_Dist1 < mod_minDist:
#         mod_minDist=mod_Dist1
#         TCA_min=TCA_ini
#     TCA_ini=TCA_ini+timedelta(microseconds=100000)
#     fecha0_calculado.append(TCA_ini)
#     dist_calcualda.append(mod_Dist1)
# #    print TCA_ini, mod_Dist1
# print '**************************************************'
# print 'Calculado'
# print '**************************************************'
# print 'El TCA calculadO es = ', TCA_min
# print 'La minima distancia calculada es = ', mod_minDist
# fecha0=fecha0_calculado[0]
# dt=[]
# for fecha in fecha0_calculado:
#     dt.append((fecha-fecha0).total_seconds())
# plt.ylim(-3,3)
# plt.title('Acercamiento ENVI vs COSMOS 2008/01/09 - 19:00:29')
# plt.ylabel('Km')
# plt.xlabel('Segundos')
# plt.grid()
# plt.plot(dt, dist_calcualda, 'r-', label='Minima Distancia')
# plt.legend(loc=3)
# plt.show()
#==========================
# Valida Mails
#==========================
# 
# tabla_mails=open('../CDM/mails/tabla_mails','r')
# contenido=tabla_mails.readlines()
# n=0
# mail=contenido[n]
# linea_data=mail.split()
# sat_id=linea_data[0]
# deb_id=linea_data[1]
# TCA=linea_data[2]
# dr=linea_data[3]
# dt=linea_data[4]
# dn=linea_data[5]
# min_dist=linea_data[6]
# var_r_sat=linea_data[7]
# var_t_sat=linea_data[8]
# var_n_sat=linea_data[9]
# var_r_deb=linea_data[10]
# var_t_deb=linea_data[11]
# var_n_deb=linea_data[12]
