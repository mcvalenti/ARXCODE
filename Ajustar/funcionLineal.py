'''
Created on 20/01/2017

@author: mcvalenti
'''
import numpy as np
import numpy.polynomial as P
from datetime import datetime
import matplotlib.pyplot as plt
from funcionesUtiles.funciones import toTimestamp

datos=open('../Comparar/diferenciasUVW','r')
x=[]
u=[]
v=[]
datos1=datos.readlines()
for l in datos1:
    campos=l.split()
    dt=l[:19]
    dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
    dt_int=toTimestamp(dt)
    x.append(dt_int)
    u.append(float(campos[2]))
    v.append(float(campos[3]))
x=np.arange(51)
# Ajuste lineal, devuelve los coeficientes en orden creciente
c,b,a = P.polynomial.polyfit(x, u, deg=2)
print '---------Polinomio para U--------------'
print(c,b,a)
y2=c+b*x+a*x*x
plt.title('Ajuste de U')
plt.plot(x,u,marker='o')
plt.plot(x,y2)
plt.show()
plt.close()
print '---------Polinomio para V--------------'
cv,bv,av= P.polynomial.polyfit(x, v, deg=2)
print(c,b,a)
y3=cv+bv*x+av*x*x
plt.title('Ajuste de V')
plt.plot(x,v,marker='o')
plt.plot(x,y3)
plt.show()
plt.close()
