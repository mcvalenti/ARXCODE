'''
Created on 16/01/2017

@author: mcvalenti
'''

a='hola'

b=['perro gato','hola','conejo zorro','estrella planeta','hola perro','hola','hola']

m=0
for i in b:
    if i=='hola':
        m = m + 1
    palabras=i.split()
    print len(palabras)