'''
Created on 30/06/2017

Se transcriben los datos de la bibliografia
(Lei Chien ) a fin de validar que la formula
y los metodos que se utilizan para el calculo 
de la PoC son correctos.

@author: mcvalenti
'''

import numpy as np
from datetime import datetime
from scipy.integrate import dblquad
from CDM.cdmParser import CDM
from TleAdmin.TLE import Tle
from Encuentro.Encuentro import Encuentro
from SistReferencia.sist_deCoordenadas import ricSis

def calcula_Poc_manual(mu_x,mu_y,sig2_xc,sig2_yc):
    #-----------------------------------------------
    # CAlculo de la PoC
    #-----------------------------------------------
    ra=0.01
    exp_c=np.exp(-ra*ra/(2*np.sqrt(sig2_xc)*np.sqrt(sig2_yc)))
    PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/(sig2_xc))+(mu_y*mu_y/(sig2_yc))))*(1-exp_c)
    PoC_int=dblquad(lambda y, x: (1.0/(2*np.sqrt(sig2_xc)*np.sqrt(sig2_yc)))*np.exp((-1.0/2.0)*((x*x/(sig2_xc))+(y*y/(sig2_yc)))), mu_x-ra, mu_x+ra, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)

    return PoC, PoC_int


def proyecta_plano_de_encuentro(rsw_vect,cov_rsw,phi):
    """
    Proyecta los valores del encuentro al plano de encuentro (x,y)
    -----------------------------------------------------------------
    inputs
        rsw_vect: vector con las posciones relativas en el sistema
                    (RSW) - [numpy array]
        cov_rsw: ma. de Covarianza - [numpy array (matrix)]
        
        phi: angulo entre los vectores velocidad.
    """
    phi_rad=phi*np.pi/180.0  
    mu_x=rsw_vect[0]
    mu_y=np.sqrt(rsw_vect[1]*rsw_vect[1]+rsw_vect[2]*rsw_vect[2])
    
    sig2_xc=cov_rsw[0][0]
    sig2_yc=cov_rsw[1][1]*np.cos(phi_rad/2.0)*np.cos(phi_rad/2.0)+cov_rsw[2][2]*np.sin(phi_rad/2.0)*np.sin(phi_rad/2.0)
    
    return mu_x,mu_y,sig2_xc,sig2_yc

def valida_bibl():
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
    
#     print'=========================================='
#     print 'varianzas de bibliog = ', sig_x,sig_y
#     print 'varianzas calculadas = ', round(np.sqrt(sig2_xc),7), round(np.sqrt(sig2_yc),7)
    
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
    dif_r=r_deb-r_sat
    rr,i,c=ricSis(r_sat,v_sat, dif_r)
    dif_r1=r_sat-r_deb
    rr1,i1,c1=ricSis(r_deb,v_deb, dif_r1)
    
    print'=========================================='
    print 'Posicion relativa bibliografia = ', dr,ds,dw
    print 'Posicion relativa calculada  satelite  = ', round(rr,7), round(i,7), round(c,7)
    print 'Posicion relativa calculada  deb  = ', round(rr1,7), round(i1,7), round(c1,7)

def valida_cdm(cdm_archivo):
    """
    Extrae datos del CDM y calcula la PoC con el metodo
    de formula explicita de Lei Chen.
    """      
    cdm=CDM(cdm_archivo)
    #=================
    # Desgloce del CDM
    #=================
    sat_id=cdm.noradID_mision
    deb_id=cdm.noradID_deb
    TCA=cdm.TCA
    v_sat=cdm.v_sat
    v_deb=cdm.v_deb
    dr=float(cdm.dr)/1000.0
    ds=float(cdm.ds)/1000.0
    dw=float(cdm.dw)/1000.0
    var_r=float(cdm.cr_r)*0.000001
    var_s=float(cdm.ct_t)*0.000001
    var_w=float(cdm.cn_n)*0.000001
#    poc_cdm=float(cdm.POC)
    #===============================================
    #Calculo el angulo entre los vectores velocidad.
    #===============================================
    cos_phi=np.dot(v_sat,v_deb)/(np.sqrt(np.dot(v_sat,v_sat))*np.sqrt(np.dot(v_deb,v_deb)))
    phi=np.arccos(cos_phi)
    #===============================================
    #Calculo la Probabilidad de Colision.
    #===============================================
    rsw_vect=[dr,ds,dw]
    cov_rsw=np.array([[var_r,0,0],[0,var_s,0],[0,0,var_w]])
    mu_x,mu_y,sig2_xc,sig2_yc=proyecta_plano_de_encuentro(rsw_vect,cov_rsw,phi)
    PoC,PoC_int=calcula_Poc_manual(mu_x,mu_y,sig2_xc,sig2_yc)
#     print '=========================================='
#     print 'Proyeccion al Plano'
#     print mu_x,mu_y,sig2_xc,sig2_yc
    print '=========================================='
#    print 'PoC del CDM    = ','%.7e' % round(poc_cdm,11)
    print 'PoC calculada en forma explicita    = ','%.7e' % round(PoC,11)
    print 'PoC calculada mediante una integral = ','%.7e' % round(PoC_int[0],11)
    print '=========================================='
    #===============================================
    #Calculo del Encuentro.
    #===============================================
    tca_epoca=datetime.strptime(TCA,"%Y-%m-%dT%H:%M:%S.%f")
    tle_sat=Tle.creadoxParam(sat_id, tca_epoca)
    tle_deb=Tle.creadoxParam(deb_id, tca_epoca)
    n=0
    encuentro = Encuentro(tle_sat,tle_deb,tca_epoca,n)
    print '=========================================='
    print 'Min distancia Calculada = ', encuentro.mod_minDist
    print 'TCA calculado = ', encuentro.tca_c
    print 'Componentes RTN del CDM: ', dr, ds, dw
    print 'Componentes RTN calculadas: ', encuentro.r_comp, encuentro.s_comp, encuentro.w_comp
    
if __name__=='__main__':
    
#    valida_bibl() # CARGA LOS PARAMETROS DE LA BIBLIOGRAFIA Y CALCULA PoC.
#    cdm_archivo='cdmxmlBluebook.xml'
#    cdm_archivo='cdmTerraPegasus10.xml'
#    cdm_archivo='25922_conj_23270_JAN_2013010_1603.xml'
    cdm_archivo='24903_conj_33759_JAN_2013010_1322.xml'
    valida_cdm(cdm_archivo) # CARGA vel, dif RTN, varianzas RTN y calcula PoC

    
    