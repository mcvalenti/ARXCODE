'''
Created on 30/06/2017

Se transcriben los datos de la bibliografia
(Lei Chien ) a fin de validar que la formula
y los metodos que se utilizan para el calculo 
de la PoC son correctos.

@author: mcvalenti
'''

import numpy as np
from scipy.integrate import quad, dblquad
from SistReferencia.sist_deCoordenadas import ricSis

def proyecta_plano_de_encuentro(rsw_vect,sig_rsw_sat,sig_rsw_deb,phi):
    """
    Proyecta los valores del encuentro al plano de encuentro (x,y)
    -----------------------------------------------------------------
    inputs
        rsw_vect: vector con las posciones relativas en el sistema
                    (RSW) - [numpy array]
        sig_rsw_xxx: vector con las desviaciones estandar en el sistema
                    del satelite y el desecho respectivamente
                    (RSW) - [numpy array]
        phi: angulo entre los vectores de velocidad [grados]
    """
    mu_x=rsw_vect[0]
    mu_y=np.sqrt(rsw_vect[1]*rsw_vect[1]+rsw_vect[2]*rsw_vect[2])
    
    return mu_x,mu_y

if __name__=='__main__':
    """
    Evalua los valores del ejemplo de la bibliografia
    tanto para la formula de PoC explicita en RSW, 
    como para el calculo de la integral
    """

    #===============================================
    # GEOMETRIA DEL ENCUENTRO (Datos del Libro)
    #===============================================
    #Posiciones en el TCA (ECI)
    r_sat=np.array([1457.273246,1589.568484,6814.189959])
    v_sat=np.array([7.001731,2.439512,0.926209])
    r_deb=np.array([1457.532155,1588.932671,6814.316188])
    v_deb=np.array([3.578705,6.172896,2.200215])
    #-----------------------------------------------
    # posicion relativa del obj2 respecto a obj1
    # en el sistema de referencia RSW.
    #-----------------------------------------------
    dr=0.031731
    ds=0.436476
    dw=0.543785
    # angulo entre velocidades relativas phi [grados]
    phi=102.458
    phi_rad=phi*np.pi/180.0   
    #-----------------------------------------------
    # Estadistica
    #-----------------------------------------------
    # combinacion de errores
    sig_r_sat=0.0231207
    sig_r_deb=0.0363234
    sig_s_sat=0.2061885
    sig_s_deb=0.4102069
    sig_w_sat=0.0719775
    sig_w_deb=0.0341134
    sig_s_comb=0.4591115
    sig_w_comb=0.0796523    
    #-----------------------------------------------
    # PLANO DE ENCUENTRO
    #-----------------------------------------------
    # Posicion relativa de Obj2
    mu_x=dr
    mu_y=0.697294
    sig_x=0.0430576 # comp radial.
    sig_y=0.2941297 # comp horizontal

    sig2_xc=sig_r_sat*sig_r_sat+sig_r_deb*sig_r_deb 
    sig2_yc=sig_s_comb*sig_s_comb*np.cos(phi_rad/2.0)*np.cos(phi_rad/2.0)+sig_w_comb*sig_w_comb*np.sin(phi_rad/2.0)*np.sin(phi_rad/2.0)
    
    print'=========================================='
    print 'varianzas de bibliog = ', sig_x,sig_y
    print 'varianzas calculadas = ', round(np.sqrt(sig2_xc),7), round(np.sqrt(sig2_yc),7)
    
    ra=0.01
    #-----------------------------------------------
    # CAlculo de la PoC
    #-----------------------------------------------
    exp_c=np.exp(-ra*ra/(2*sig_x*sig_y))
    PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/(sig_x*sig_x))+(mu_y*mu_y/(sig_y*sig_y))))*(1-exp_c)
    PoC_int=dblquad(lambda y, x: (1.0/(2.0*np.pi*sig_x*sig_y))*np.exp((-1.0/2.0)*((x*x/(sig_x*sig_x))+(y*y/(sig_y*sig_y)))), mu_x-ra, mu_x+ra, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)
    Poc_bibl=0.0001807975
#     dif_poc=PoC-Poc_bibl
#     dif_porc=dif_poc*100.0/Poc_bibl
    print '=========================================='
    print 'PoC calculada en forma explicita    = ','%.7e' % round(PoC,11)
    print 'PoC calculada mediante una integral = ','%.7e' % round(PoC_int[0],11)
    print 'PoC calculada en la  bibliografia   = ', '%.7e' % round(Poc_bibl,11)
#     print 'Diferencia = ', dif_poc
#     print 'Porcentanje de error = ', dif_porc

    #===============================================
    # Posicion relativa calculada a partir de r,v
    #===============================================
    dif_r=r_sat-r_deb
    rr,i,c=ricSis(r_deb,v_deb, dif_r)
#     dif_r=r_deb-r_sat
#     rr,i,c=ricSis(r_sat,v_sat, dif_r)
    
    print'=========================================='
    print 'Posicion relativa bibliografia = ', dr,ds,dw
    print 'Posicion relativa calculada    = ', round(rr,7), round(i,7), round(c,7)



