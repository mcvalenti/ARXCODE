'''
Created on 09/05/2017

@author: mcvalenti
'''
"""
Created on Mon Jan 11 10:26:46 2016

Transformacion de Coordenadas:
    x,y,z ---> alpha, delta

@author: mcvalenti
"""

import numpy as np
from rot_tierra import rot_tierra

in1=open('desarrollo/envi.sal')
in2=open('desarrollo/cosmos.sal')
out1=open('alfdelenvi.txt','w+')
out2=open('alfadelcosmos.txt','w+')
pi=np.pi
deg=np.divide(180,pi)
#in2=open('cosmos.sal','w+')
 
lineas1=in1.readlines()
lineas2=in2.readlines()
 
for l1 in lineas1:
    datos=l1.split(' ')
    x=float(datos[3])
    y=float(datos[4])
    z=float(datos[5])
#    print x,y,z
    r_prima=rot_tierra(x,y,z)
    print 'r_prima'+str(r_prima)
#    x=r_prima[0]
#    y=r_prima[1]
#    z=r_prima[2]
#    print x,y,z
    r=np.sqrt(x*x+y*y+z*z)
    l=np.divide(x,r)
    m=np.divide(y,r)
    n=np.divide(z,r)
    delta=np.arcsin(n)
    if m>0:
        alpha = np.arccos(np.divide(l,np.cos(delta)))
    else:
        alpha = 2*pi-np.arccos(np.divide(l,np.cos(delta)))
#    print alpha*deg
    fila=str(alpha*deg)+' '+str(delta*deg)+'\n'
    out1.write(fila)
     
for l2 in lineas2:
    datos=l2.split(' ')
    x2=float(datos[3])
    y2=float(datos[4])
    z2=float(datos[5])
    r2=np.sqrt(x2*x2+y2*y2+z2*z2)
    ll=np.divide(x2,r2)
    mm=np.divide(y2,r2)
    nn=np.divide(z2,r2)
    delta2=np.arcsin(nn)
    if mm>0:
        alpha2 = np.arccos(np.divide(ll,np.cos(delta2)))
    else:
        alpha2 = 2*pi-np.arccos(np.divide(ll,np.cos(delta2)))
#    print alpha*deg
    fila2=str(alpha2*deg)+' '+str(delta2*deg)+'\n'
    out2.write(fila2)
    
def cart2geod(x,y,z):
    """
    Transforma coordenadas del sistem cartesiano (TEME)
    al sistema geodesico aprox. 
    """
    r=np.sqrt(x*x+y*y+z*z)
    l=np.divide(x,r)
    m=np.divide(y,r)
    n=np.divide(z,r)
    delta=np.arcsin(n)
    if m>0:
        alpha = np.arccos(np.divide(l,np.cos(delta)))
    else:
        alpha = 2*np.pi-np.arccos(np.divide(l,np.cos(delta)))
#    print alpha*deg
    fila=str(alpha*np.divide(180,np.pi))+' '+str(delta*np.divide(180,np.pi))+'\n'
    
    return fila
    