'''
Created on 30/03/2017

@author: mcvalenti
'''
import numpy as np
import numpy.polynomial as P
import matplotlib.pylab as plt


# # Cargamos los datos
# data = np.loadtxt("polar.dat")
# C_L, C_D = data
# # Descarto los datos que no me sirven
# stall_idx = np.argmax(C_L)
# y = C_D[:stall_idx + 1]
# x = C_L[:stall_idx + 1] ** 2
# # Ajuste lineal, devuelve los coeficientes en orden creciente
# C_D0, k = P.polynomial.polyfit(x, y, deg=1)
# print(C_D0, k)

x=np.linspace(-10, 10, 200)
y=[]
for i in x:
    y.append(i*i-2*i+1)

c, b, a = P.polynomial.polyfit(x, y, deg=2)
print c,b,a
plt.plot(x,y)
plt.show()