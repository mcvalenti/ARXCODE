
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
import numpy as np
#from newton import newton

def xv2eo(r,v):
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
    
def uvwSis(r,rp,dr):
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
        u: direccion radial - (Vector) - [km]
        v: direccion transversal - (Vector) - [km]
        w: direccion perpendicular al plano - (Vector) - [km]
    """
    
    ru=np.sqrt(np.dot(r,r))
    eu=np.dot(1.0/ru,r)
    rxrp_int=np.cross(r,rp)
    rxrp_mod=np.sqrt(np.dot(rxrp_int,rxrp_int))
    rxrp=np.cross(r,rp)
    ew=np.dot(1.0/rxrp_mod,rxrp)
    ev=np.cross(ew,eu)
    
    u=np.dot(eu,dr)
    v=np.dot(ev,dr)
    w=np.dot(ew,dr)
    
    return u,v,w
    
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

    
