'''
Created on 08/05/2017

@author: mcvalenti
'''
import sys, os, glob
import numpy as np
from datetime import datetime, timedelta
from TleAdmin.get_tle import importar_tle
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import Tle
from SistReferencia.sist_deCoordenadas import vncSis
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
"""
Calcula la probabilidad de Colision PoC.
Luego de realizar los siguientes pasos:
--------------------------------------
# Calcular la miss distance.
# Genera el B-plane a partir de r(tca) y v(tca).
# Arma la matriz del B-plan
# Proyecta la matriz de convarianza al B-plane - [Cb]
# Calcula los autovalores y autovectores.
# Identifica el semieje mayor y menor entre los autovalores.
# Idetifica el autovector asociado al semieje mayor.
# Construye xb (chico)
# Resuelve la integral de la PoC.
"""

def tuplaFloat(tupla):
    """
    transforma las tuplas a sus componentes en flotante
    """
    x=float(tupla[0])
    y=float(tupla[1])
    z=float(tupla[2])
    
    return x,y,z

def missDistance(sat_id,arch_tle, deb_id,arch_tle1,TCA):
    """
    Busca los tles de los objetos para una fecha con 3 dias anteriores
    al TCA. 
    Propaga las posiciones hasta el TCA y calcula la distancia entre ellos. 
    Identifica el momento de maximo acercamiento y lo compara con TCA.
    ------------------------------------------------------------------
    inputs
        sat_id: codigo NORAD del satelite (string)
        arch_tle: archivo TLE del satelite (string)
        deb_id: codigo NORAD del desecho (string)
        arch_tle1: archivo TLE del desecho (string)
        TCA: epoca del maximo acercamiento (datetime)
    outputs
        dr,dv: distancia relativa al momento del maximo acercaciento. (array)
        TCA_calc: epoca del maximo acercamiento calculada (datetime)        
    """

    tle_envi=Tle('../TleAdmin/tle/'+arch_tle)
    tle_cosmos=Tle('../TleAdmin/tle/'+arch_tle1)
    
    #========================
    #Calculo de Diferencias
    #========================
    
    for k in range(8):          
        r,v=tle_envi.propagaTLE(TCA)
#        print 'Envi posicion: ',r,v
        xf,yf,zf=tuplaFloat(r)
        xv,yv,zv=tuplaFloat(v)
        r=np.array([xf,yf,zf])
        ve=np.array([xv,yv,zv])

        r1,v1=tle_cosmos.propagaTLE(TCA)
#        print 'Cosmos posicion: ',r1,v1
        xf1,yf1,zf1=tuplaFloat(r1)
        xv1,yv1,zv1=tuplaFloat(v1)
        r1=np.array([xf1,yf1,zf1])
        v1=np.array([xv1,yv1,zv1])

        dif_r=r-r1
        dif_v=ve-v1
        #---------Sistema V,N,C.
        v,n,c=vncSis(r, ve, dif_r)
        vv,nn,cc=vncSis(r, ve, dif_v)
        rvnc=np.array([v,n,c])
        vvnc=np.array([vv,nn,cc])
        mod_dif=np.sqrt(np.dot(rvnc,rvnc))
        print TCA, mod_dif
        
        TCA=TCA+timedelta(seconds=1)
    
    return rvnc,vvnc

def generaBplane(dr,dv):
    """
    Genera la matriz de Transformacion Rxb,yb
    -----------------------------------------
    inputs
        dr,dv: vectores relativos de posicion y
               velocidad en TCA. (arrays)
    output
        Rb: Matriz de transformacion al B-plane. 
    """
    dr_mod=np.sqrt(np.dot(dr,dr))    
    rxv=np.cross(dr,dv)
    mod_rxv=np.sqrt(np.dot(rxv,rxv))
    #--------------------------------
    xm_b=np.dot(1.0/dr_mod,dr)
    ym_b=np.dot(1.0/mod_rxv,rxv)
    Rb=np.array([[xm_b[0],xm_b[1],xm_b[2]],[ym_b[0],ym_b[1],ym_b[2]]])
    return Rb


def calculaElipses_param(C_b, xm_b):
    """
    Calcula los semiejes de la elipse y la orientacion
    --------------------------------------------------
    inputs
        C_b:Matriz de covarianza combinada, proyectada en
            el B-plane. 
    outputs
        xb: vector unitario en la direccion del semieje mayor.
        phi_b: angulo con la direccion del semieje mayor. 
    """
    auto_val, auto_vect=np.linalg.eig(C_b)
    i=np.argmax(auto_val)
    j=np.argmin(auto_val)
    a=auto_val[i]
    b=auto_val[j]
    e_a=auto_vect[i]
    e_b=auto_vect[j]
    ea_mod=np.sqrt(np.dot(e_a,e_a))
    xb=np.dot(1.0/ea_mod,e_a)
    phi_b=np.arccos(xb,xm_b)
        
    return a,b,xb,phi_b

def calculaPoC():
    """
    Calcula la Poc en dos dimensiones.
    -------------------------------------------------------
    inputs
        dr,Cb,xb,Rc
    outputs
        PoC
    """
    pass



if __name__=='__main__':
    
    """
    Propagacion los datos tle de los objetos
    ENVISAT - NORAD ID: 27386
    COSMOS  - NORAD ID: 15482
    A partir de las 18 hs hasta las 20 hs.
    Del dia 09/01/2008 
    """
    
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
    
    
    TCA=datetime(2008,1,9,19,0,27,0)
    sat_id='27386' #ENVISAT
    deb_id='15482' #COSMOS
#     sat_id='23560' #ENVISAT
#     deb_id='16011' #COSMOS
    #-------Request a NORAD.
    f_ini=TCA-timedelta(days=18)
    f_fin=TCA-timedelta(days=3)
    usuario='macecilia'
    clave='MaCeciliaSpace17'
    
    #--------------------MISION-----------------------------    
    importar_tle(usuario,clave, sat_id,f_ini,f_fin,str(sat_id))
    ark=open('../TleAdmin/crudosTLE/'+str(sat_id))
    contenido=ark.readlines()
    if len(contenido) > 0:
        files=glob.glob('../TleAdmin/tle/*')
        for filename in files:
            os.unlink(filename)
        setTLE(sat_id,str(sat_id))
        tles=glob.glob('../TleAdmin/tle/*')
        tle_dic=generadorDatos(tles)
        tles_ord=ordenaTles(tle_dic)
        arch_tle=tles_ord[-1][0]
    else:
        print 'El programa ha detenido su ejecucion.'
        sys.exit()
    #----------DESECHO----------------------------------------    
    importar_tle(usuario,clave, deb_id,f_ini,f_fin,str(deb_id))
    ark1=open('../TleAdmin/crudosTLE/'+str(deb_id))
    contenido1=ark1.readlines()
    if len(contenido) > 0:
        setTLE(deb_id,str(deb_id))
        tles1=glob.glob('../TleAdmin/tle/'+str(deb_id)+'*')
        tle_dic1=generadorDatos(tles1)
        tles_ord1=ordenaTles(tle_dic1)
        arch_tle1=tles_ord1[-1][0]
    else:
        print 'El programa ha detenido su ejecucion.'
        sys.exit()
         
         
    rvnc,vvnc=missDistance(sat_id,arch_tle, deb_id,arch_tle1,TCA)

# 10 de Mayo.

    R_b=generaBplane(rvnc,vvnc)
    
    #====================
    #Matriz de Covarianza
    #====================

    Cd=np.array([[4.1345498441906514,-0.031437388833697122,0.078011634263035007],
                 [-0.031437388833697122,0.0025693554190851101,-0.014250096142904997],
                 [0.078011634263035007,-0.014250096142904997,0.096786625771746529]])
    
    Cm=np.array([[4.8247926515782202,0.05994752830943241,0.049526867540809635],
                 [0.05994752830943241,0.019150349628774828,0.012470649611436152],
                 [0.049526867540809635,0.012470649611436152,0.012649606483621921]])

    
    C=Cd+Cm
    
    C_b=np.dot(C,np.transpose(R_b))
    C_b=np.dot(R_b,C_b)
    print C_b
    
    w,v=np.linalg.eig(C_b)
    print w,v
    