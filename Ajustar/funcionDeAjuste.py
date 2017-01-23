'''
Created on 20/01/2017

Este modulo toma las tablas que contienen las diferencias 
entre los datos TLE y los datos CODS, para las coordenadas
u,v y w; hace un ajuste con la funcion Polynomial y luego
hace las graficas. 

@author: mcvalenti
'''
from os import system
import numpy as np
import numpy.polynomial as P
from datetime import datetime
from funcionesUtiles.funciones import toTimestamp

def funcionDeAjuste(arch1,arch2):
    """
    ---------------------------------------------------------------------------------
    Lee el archivo diferenciasUVW de la carpeta diferencias y genera 
    el archivo diferenciasAjustadas, que ademas de las diferencias contiene
    las columnas correspondientes al dato evaluado en la funcion de ajuste. 
    ---------------------------------------------------------------------------------
    inputs 
        diferenicasUVW:     archivo de texto plano con las diferencias ya calculadas.
        ajustesGraf:        texto plano en formato de gnuplot que se invoca para la 
                            realizacion de los graficos
    outputs
        diferenciasAjustadas: archivo de texto plano para la escritura de los valores
                              evaluados en la funcion de ajuste.
        ajustesUVW.eps: grafico con las diferencias y el ajuste en las 3 componentes.
        
    """
    
    datos=open('diferencias/'+arch1,'r')
    salida=open('diferencias/diferenciasAjustadas','w')
    x=np.arange(51)
    u=[]
    v=[]
    w=[]
    datos1=datos.readlines()
    for l in datos1:
        campos=l.split()
        dt=l[:19]
        dt=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
        dt_int=toTimestamp(dt)
        u.append(float(campos[2]))
        v.append(float(campos[3]))
        w.append(float(campos[4]))
    # Ajuste lineal, devuelve los coeficientes en orden creciente
    c,b,a = P.polynomial.polyfit(x, u, deg=2)
    print '---------Polinomio para U--------------'
    print(c,b,a)
    y2=c+b*x+a*x*x
    print '---------Polinomio para V--------------'
    cv,bv,av= P.polynomial.polyfit(x, v, deg=2)
    print(cv,bv,av)
    y3=cv+bv*x+av*x*x
    print '---------Polinomio para W--------------'
    cw,bw,aw= P.polynomial.polyfit(x, w, deg=2)
    print(cw,bw,aw)
    y4=cw+bw*x+aw*x*x
    for k in x:
        info1=str(k)+' '+str(u[k])+' '+str(v[k])+' '+str(w[k])+' '+str(y2[k])+' '+str(y3[k])+' '+str(y4[k])+'\n'
        salida.write(info1)
        
    """
    Grafico
    """   
    system('gnuplot diferencias/'+arch2)
    
    if __name__=='__main__':
        funcionDeAjuste('diferenciasUWV','ajustesGraf')
        print 'Fin'
        
        