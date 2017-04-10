

import numpy as np
from datetime import datetime
from math import pi
from sist_deTiempo import calcula_mjd, jd

#from newton import newton

def xv2eo(r,v):
    """
    ---------------------------------------------
    Trasformacion de vector de estado x,v
    a elementos orbitales.
    ---------------------------------------------
    inputs:
        x: posicion (vector) - [km]
        v: velocidad (vector) - [km/s]
    outputs:
        a: semieje mayor (float) - [km]
        e: excentricidad (float)
        i: inclinacion (float) - [rad]
        Omega: Longitud del Nodo (float) - [rad]
        w: Argumento del perigeo (float) - [rad]
        nu: Anomalia verdadera (float) - [rad]
    """
#    Rt=6378.0 #[km]
    GM=398600.4405 #[km3/s2]
    deg=180.0/np.pi 
#    rad=np.pi/180.0
    
    rmod=np.sqrt(np.dot(r,r))
    vmod=np.sqrt(np.dot(v,v))
    """
    i,Omega
    """
    h=np.cross(r,v)
    hmod=np.sqrt(np.dot(h,h))
    h=np.dot(1./hmod,h)
    i=np.arctan(np.sqrt(h[0]*h[0]+h[1]*h[1])/h[2])
    if i < 0.0:
        i=np.pi+i
        
    arg=-h[0]/h[1]
    Omega=np.arctan(arg)
    if np.sign(-h[1]) < 0.0:
        Omega=Omega+np.pi

    """
     a
    """
     
    a=1.0/((2.0/rmod)-vmod*vmod/GM)
    n=np.sqrt(GM/(a*a*a))
    
    """
     e
    """
    p=hmod*hmod/GM
    e=np.sqrt(1-(p/a))
    
    """
     M    
    """
    E=np.arctan((np.dot(r,v)/(a*a*n))/(1-rmod/a))
    if np.sign((1-rmod/a)) < 0.0:
        E=E+np.pi
    M=E-e*np.sin(E)

    """
     w, nu
    """

    u=np.arctan(r[2]/(-r[0]*h[1]+r[1]*h[0]))
    if np.sign((-r[0]*h[1]+r[1]*h[0])) < 0.0:
        u=u+np.pi
    nu=np.arctan((np.sin(E)*np.sqrt(1-e*e))/(np.cos(E)-e))
    if np.sign((np.cos(E)-e)) < 0.0:
        nu=nu+np.pi
    if u-nu < 0.0:
        w=2*np.pi+(u-nu)
    else:
        w=u-nu
    
    """
    Impresion de salida
    """
    print 'semieje mayor a= ',a
    print 'Excentricidad e= ',e
    print 'Inclinacion i= ',i*deg
    print 'Longitud del Nodo = ', Omega*deg
    print 'Argumento del Perigeo w= ',w*deg
    print 'Anomalia Media ',M*deg
    print 'Anomalia Verdadera',nu*deg
    return a,e,i,Omega,w,nu
    
def eo2xv(a,e,i,Omega,w,nu):
    """
    ----------------------------------------------------------------
    Transforma los elementos orbitales a sus coordenadas cartesianas
    inerciales (ECI: Earth Center Inertial)- No rotantes.
    ----------------------------------------------------------------
    inputs:
        a: semieje mayior (float) - [km]
        e: excentricidad (float)
        i: inclinacion (float) - [grados]
        Omega: longitud del Nodo (float) - [grados]
        w: argumento del perigeo (float) - [grados]
        nu: anomalia verdadera (float) - [grados]
    outputs:
        r_eq: posicion en el sistema inercial (ECI) (vector) - [km]
    """
    rad=np.pi/180.0 # grados a radianes
    
    i=i*rad
    Omega=Omega*rad
    w=w*rad
    nu=nu*rad
    r=a*(1.0-e*e)/(1.0+e*np.cos(nu))
    r_cos=[np.cos(nu),np.sin(nu),0.0]
    r1=np.dot(r,r_cos)
    Q=np.array([[-np.sin(Omega)*np.cos(i)*np.sin(w)+np.cos(Omega)*np.cos(w), -np.sin(Omega)*np.cos(i)*np.cos(w)-np.cos(Omega)*np.sin(w), np.sin(Omega)*np.sin(i)],
                 [np.cos(Omega)*np.cos(i)*np.sin(w)+np.sin(Omega)*np.cos(w),np.cos(Omega)*np.cos(i)*np.cos(w)-np.sin(Omega)*np.sin(w),np.cos(Omega)*np.sin(i)],
                  [np.sin(i)*np.sin(w),np.sin(i)*np.cos(w),np.cos(i)]])

    r_eq=np.dot(Q,r1)   
    return r_eq
    
def gaussian_vectors(i,Om,ap):
    """
    --------------------------------------------------------
    Calcula los Vectores Gaussianos P,Q y W,
    para la transformacion entre el sistema perifocal y el
    sistema cartesiano inercial.
    --------------------------------------------------------
    inputs:
        i: inclinacion (float) - [rad]
        Om: longitud del nodo (float) - [rad]
        ap: argumento del perigeo (float) - [rad]
    outputs:
        P, Q y W: vectores gausianos (vect)
    """
    
    P=np.array([np.cos(ap)*np.cos(Om)-np.sin(ap)*np.cos(i)*np.sin(Om),
       np.cos(ap)*np.sin(Om)+np.sin(ap)*np.cos(i)*np.cos(Om),
        np.sin(ap)*np.sin(i)])
        
    Q=np.array([-np.sin(ap)*np.cos(Om)-np.cos(ap)*np.cos(i)*np.sin(Om),
       -np.sin(ap)*np.sin(Om)+np.cos(ap)*np.cos(i)*np.cos(Om),
        np.cos(Om)*np.sin(i)])
        
    W=np.array([np.sin(i)*np.sin(Om),
       -np.sin(i)*np.cos(Om),
        np.cos(i)])
        
    return P,Q,W
    
def vncSis(r,rp,dr):
    """
    -------------------------------------------------------------
    Transforma las coordenadas del sistema inercial cartesiano,
    al sistema de referecia de la nave. 
    -------------------------------------------------------------
    inputs
        r: posicion en el sistema cartesiano (Vector) - [km]
        rp: velocidad en el sistema cartesiano (Vector) -[km/s]
        dr: vector de diferencia en la posicion - (Vector) - [km]
    outputs
        v: direccion along track (velocidad) - (Vector) - [km]
        n: direccion normal/radial - (Vector) - [km]
        c: direccion perpendicular al plano - (Vector) - [km]
    """
    
    rv=np.sqrt(np.dot(rp,rp))
    ev=np.dot(1.0/rv,rp)
    rxrp_int=np.cross(r,rp)
    rxrp_mod=np.sqrt(np.dot(rxrp_int,rxrp_int))
    ec=np.dot(1.0/rxrp_mod,rxrp_int)
    en=np.cross(ev,ec)
    
    v=np.dot(ev,dr)
    n=np.dot(en,dr)
    c=np.dot(ec,dr)
    
    return v,n,c

def ricSis(r,rp,dr):
    """
    -------------------------------------------------------------
    Transforma las coordenadas del sistema inercial cartesiano,
    al sistema de referecia de la nave. 
    -------------------------------------------------------------
    inputs
        r: posicion en el sistema cartesiano (Vector) - [km]
        rp: velocidad en el sistema cartesiano (Vector) -[km/s]
        dr: vector de diferencia en la posicion - (Vector) - [km]
    outputs
        rr: direccion radial - (Vector) - [km]
        i: direccion in track (velocidad) - (Vector) - [km]
        c: direccion perpendicular al plano - (Vector) - [km]
    """
    
    r_mod=np.sqrt(np.dot(r,r))
    er=np.dot(1.0/r_mod,r)
    rxrp_int=np.cross(r,rp)
    rxrp_mod=np.sqrt(np.dot(rxrp_int,rxrp_int))
    ec=np.dot(1.0/rxrp_mod,rxrp_int)
    ei=np.cross(ec,er)
    
    rr=np.dot(er,dr)
    i=np.dot(ei,dr)
    c=np.dot(ec,dr)
    
    return rr,i,c
    
def lof_qsw(rt,vt):
    """
    ---------------------------------------------------
    Transforma las coordeandas al Local Orbital Frame
    vectores unitarios: q (radial), s (normal a q),
    w (normal al plano)
    ----------------------------------------------------
    inputs 
        r: posicion en el sistema cartesiano (Vector) - [km]
        v: velocidad en el sistema cartesiano (Vector) -[km/s]
    outputs
        q: direccion radial - (Vector) - [km]
        s: direccion transversal - (Vector) - [km]
        w: direccion perpendicular al plano - (Vector) - [km]      
    """    
    rq=np.sqrt(np.dot(rt,rt))
    q=np.dot(1.0/rq,rt)
    rxv_mod=np.sqrt(np.abs(np.dot(rt,vt)))
    rxv=np.cross(rt,vt)
    w=np.dot(1.0/rxv_mod,rxv)
    s=np.cross(w,q)    
    return q,s,w
    

    
def rot_tierra(x,y,z,minu,ts):
    """
    x,y,z (ECI) -----> x,y,z (ECEF)
    """
    pos=[x,y,z]
    OmegaT=ts#+minu*60.0*15.04/3600.0 # velocidad angular de la tierra [seg]
    OmegaT_rad=OmegaT*np.pi/180.0

    ma_rot=np.array([[np.cos(OmegaT_rad), np.sin(OmegaT_rad), 0.0],
                       [-np.sin(OmegaT_rad), np.cos(OmegaT_rad), 0.0],
                       [0.0, 0.0, 1.0]])
                  
    r_prima=np.dot(ma_rot,pos)
    return r_prima 

def teme2tod(epoch,r_teme):
    """
    Transforma las coordenadas de r_teme, en el sistema
    TEME al sistema TOD.
    -----------------------------------------------------
    input
        epoch: epoca del vector de estado (datetime)
        r_teme: vector de estado en el sistema TEME (array)
    output
        r_tod: vector de estado en el sistema TOD (array)
    """
    
    arc2rad=np.pi/(180.0*3600.0)   
    jd1=jd(epoch)
    tt=(jd1-2451545.0)/36525.0 
#     mjd=calcula_mjd(epoch)
#     tt=(mjd-51544.5)/36525.0

    """
    Parametros [arcseconds / segundos de arco]
    """
    M_moon  = 134.96298139*3600.0+1717915922.6330*tt+31.31*tt*tt+0.064*tt*tt*tt
    M_sun   = 357.52772333*3600.0+129596581.2240*tt-0.577*tt*tt+0.012*tt*tt*tt
    mu_moon = 93.27191028*3600.0+1739527263.1370*tt-13.257*tt*tt-0.011*tt*tt*tt
    D_sun   = 297.85036306*3600.0+1602961601.3280*tt-6.891*tt*tt+0.019*tt*tt*tt
    O_moon  = 125.04452222*3600.0-6962890.5390*tt+7.455*tt*tt+0.0008*tt*tt*tt
    
    nutacion=open('../SistReferencia/prenut.dat','r')
    coef=nutacion.readlines()
    d_epsi1=0
    d_psi1=0
    
    for c in coef:
        an=c.split(',')
        a1=float(an[0])
        a2=float(an[1])
        a3=float(an[2])
        a4=float(an[3])
        a5=float(an[4])
        aphi=float(an[5])*arc2rad
        aphi_d=float(an[6])*arc2rad
        aepsi=float(an[7])*arc2rad
        aepsi_d=float(an[8])*arc2rad
        
        phi_i1=(a1*M_moon+a2*M_sun+a3*mu_moon+a4*D_sun+a5*O_moon)*arc2rad
        phi_i=phi_i1%(2*np.pi)
        
        d_epsi1=d_epsi1 + (aepsi+aepsi_d*tt)*np.cos(phi_i)
        d_epsi=d_epsi1%(2*np.pi)
        d_psi1=d_psi1 + (aphi+aphi_d*tt)*np.sin(phi_i)
        d_psi=d_psi1%(2*np.pi)
        
    d_epsi=d_epsi*(1.0/10000.0)
    d_psi=d_psi*(1.0/10000.0)
    
    epsi_media = (84381.448-46.815*tt-0.00059*tt*tt+0.001813*tt*tt*tt)*arc2rad # [rad]
    
    EQnox = (d_psi*np.cos(epsi_media+d_epsi)+0.00264*arc2rad*np.sin(O_moon*arc2rad)+0.000063*arc2rad*np.sin(2*O_moon*arc2rad))

    
    Q=np.matrix([[np.cos(-EQnox),np.sin(-EQnox),0],
                 [-np.sin(-EQnox),np.cos(-EQnox),0],
                 [0,0,1]])
    
    r_tod=np.dot(Q,r_teme)
    
    return r_tod    
    
if __name__=='__main__':
    epoca=datetime(2000,6,28,15,8,51,655)
#     jd=jd(epoca)
#     tt=(jd-2451545.0)/36525.0

    r_teme=[3961.0035498,6010.7511740,4619.3009301]
    r_todVal=[3961.4214985,6010.4752688,4619.301531]
    r_tod=teme2tod(epoca, r_teme)

    print epoca
    print r_tod
    print r_todVal-r_tod
