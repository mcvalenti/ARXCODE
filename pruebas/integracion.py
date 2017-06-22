'''
Created on 11/05/2017

@author: mcvalenti
'''
import numpy as np
from scipy.integrate import quad, dblquad

r_comp=0.031731
s_comp=0.436476
w_comp=0.543785

mu_x=r_comp
mu_y=np.sqrt(s_comp*s_comp+w_comp*w_comp)

sig_x=0.0430576
sig_y=0.2941297

ra=0.01

a=mu_x-ra
b=mu_x+ra
# la integral.
#f=(1.0/(2.0*np.pi*sig_x*sig_y))*np.exp((-1.0/2.0)*((x*x/sig2_x)+(y*y/sig2_y)))
#extremos
# y=np.sqrt(ra*ra-(y*y-mu_x)*(y*y-mu_x))+mu_y

area = dblquad(lambda y, x: (1.0/(2.0*np.pi*sig_x*sig_y))*np.exp((-1.0/2.0)*((x*x/(sig_x*sig_x))+(y*y/(sig_y*sig_y)))), a, b, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)
print area[0]
# a=np.array([2,3,4])
# print a
# b=a.T
# print b

# def f(x,y):
#     return x
# 
# int=nquad(f, [[2,4],[0,2]])
# 
# print int[0]
# N = 5
# def f(t, x):
#    return np.exp(-x*t) / t**N
# integrate.nquad(f, [[1, np.inf],[0, np.inf]])