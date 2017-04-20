'''
Created on 17/04/2017
@author: mcvalenti
'''

import glob
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.dates import date2num



"""
A partir de las diferencias entre los valores de los TLE
y los datos GPS, graficar. 
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
-----------------
Gestion de Fechas
"""

x = [datetime.strptime(d,'%Y-%m-%d').date() for d in fechas]
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
ax1.grid(True)
ax2.grid(True)
ax3.grid(True)
ax1.plot(x,dv,'o',label='V')
ax1.set_ylabel('Km')
ax1.legend(loc=1)
ax2.plot(x,dn,'o',label='N')
ax2.set_ylabel('Km')
ax2.legend(loc=4)
ax3.plot(x,dc,'o',label='C')
ax3.set_ylabel('Km')
ax3.legend(loc=4)
fig.suptitle('Diferencias CODS vs TLE+SGP4')
plt.xlabel('Epoca')
plt.savefig('../Estadistica/ajustes.png')
plt.show()
plt.close()