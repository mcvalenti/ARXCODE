'''
Created on 17/04/2017
@author: mcvalenti
'''

import glob
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates


"""
A partir de las diferencias entre los valores de los TLE
y los datos GPS, graficar las diferencias. 
"""

lista=glob.glob('../Estadistica/archivos/*')

fechas=[]
dv=[]
dn=[]
dc=[]

for lis in lista:
    f=open(lis,'r')
    contenido=f.readline()
    campo=contenido.split(' ')
    yy=int(campo[0][:4])
    mes=int(campo[0][4:6])
    dia=int(campo[0][6:8])
    fecha=datetime(yy,mes,dia)
    fechas.append(fecha.strftime('%Y-%m-%d'))
    dv.append(float(campo[1]))
    dn.append(float(campo[2]))
    dc.append(float(campo[3]))

dv_media=np.mean(dv)
dn_media=np.mean(dn)
dc_media=np.mean(dc)        

"""
GRAFICO
"""
# """
# Gestion de Fechas
# """
# date_fmt = '%Y-%m-%d'
# epoca=[datetime.strptime(str(i), date_fmt) for i in fechas]
# x = [mdates.date2num(i) for i in epoca]
# date_formatter = mdates.DateFormatter('%d-%m-%y')
# 
# plt.format_xdata = mdates.DateFormatter('%Y-%m-%d')
# plt.plot(fechas,dv,label='Coordenada V')
# plt.show()
# plt.close()


fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
ax1.grid(True)
ax2.grid(True)
ax3.grid(True)
ax1.plot( dv_media)
ax1.plot(dv,label='Coordenada V')
ax1.set_ylabel('Km')
ax2.plot(dn,label='Coordenada N')
ax2.plot(dn_media)#
ax2.set_ylabel('Km')
ax3.plot(dc,label='Coordenada C')
ax3.plot(dc_media)
ax3.set_ylabel('Km')
fig.suptitle('Diferencias CODS vs TLE+SGP4')
plt.xlabel('Epoca')
plt.savefig('../Estadistica/ajustes.png')
plt.show()
plt.close()