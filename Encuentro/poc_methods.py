import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse,  Arrow,  Circle
from datetime import datetime
import psycopg2
import psycopg2.extras
from scipy.integrate import  nquad
from retrieveCDM import retrieveCDM
from object_v5 import TLEObject
from alert_v5 import Alert

def get_radius(obj1_id, obj2_id):
    """
    Collect object's radar cross sections (rcs) and computes object's
    radius
    """
    # Connect to an existing database
    conn = psycopg2.connect("dbname='detriti' user='guest' host='192.106.234.55' password='detritispaziali'")
    # Open a cursor to perform database operations
    cur1 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # retrieve the RCS
    cur1.execute("select rcs from tle where satid = "+str(obj1_id)+" ") 
    rcs1= cur1.fetchone()
    radius1=np.sqrt(rcs1[0]/np.pi)
    cur2.execute("select rcs from tle where satid = "+str(obj2_id)+" ") 
    rcs2= cur2.fetchone()
    radius2=np.sqrt(rcs2[0]/np.pi)
    return radius1, radius2

def f(y, z, maB_plane, rho_0_star, p_star, ra):
    """Defines the function f that is going to be integrated"""
    t_star=np.array([[0, 1, 0], [0, 0, 1]])  
    rho_star=np.dot(t_star, np.dot(maB_plane, [0, y, z]))
    diff=rho_star-rho_0_star
    p_star_inv=inv(p_star)
    s_star0=np.dot(p_star_inv, diff)
    s_star=np.dot(diff.transpose(), s_star0)
    return np.exp(-s_star)

def bounds_y(maB_plane, rho_0_star, p_star, rc):
    return [-rc, rc]

def bounds_z(y, maB_plane, rho_0_star, p_star, rc):
    return [-np.sqrt(rc*rc-y*y), np.sqrt(rc*rc-y*y)]

def PoC_akella(maB_plane, rho_0_star, p_star, rc):
    """ Computes the 2D integral """
    coeff=1.0/(2*np.pi*np.sqrt(np.linalg.det(p_star)))
    poc_integral,  err= nquad(f, [bounds_z, bounds_y], args=(maB_plane, rho_0_star, p_star, rc)) # double integrals 
    poc_ak = coeff*poc_integral
    return poc_ak
    
def PoCmax_Klinkrad(C_Bdiag, r_relative_Bplane, rc):
    vect_prod=np.dot(r_relative_Bplane.transpose(), np.dot(inv(C_Bdiag),r_relative_Bplane))
    coef1=np.exp(1)*np.sqrt(np.linalg.det(C_Bdiag))*vect_prod
    PoCmax=rc*rc/coef1
    return PoCmax
    
def f_k(x, y, C_Bdiag, rc):
    """Defines the function f that is going to be integrated"""
    rb=np.array([[x, y]])
    C_B_inv=inv(C_Bdiag)
    A_B=0.5*np.dot(rb, np.dot(C_B_inv, rb.transpose()))
    return np.exp(-A_B)

def k_bounds_y(C_Bdiag, rc):
    return [-rc, rc]

def k_bounds_z(x, C_Bdiag, rc):
    return [-np.sqrt(rc*rc-x*x), np.sqrt(rc*rc-x*x)]

def PoC_klinkrad(C_Bdiag, rc):
    """ Computes the 2D integral """
    # REVISAR DONDE ESTA CENTRADO R_B
    coeff=1.0/(2*np.pi*np.sqrt(np.linalg.det(C_Bdiag)))
    poc_integral,  err= nquad(f_k, [k_bounds_z, k_bounds_y], args=(C_Bdiag, rc)) # double integrals 
    poc_klinkrad= coeff*poc_integral
    return poc_klinkrad
    
def PoC_limit(rc,  miss_distance):
    erre=rc/miss_distance
    if erre < 0.8:
        PoC_limit=0.48394*erre
    else:
        PoC_limit=0.21329*np.exp(1.01511*erre)-0.09025
    return PoC_limit
    
def eigsorted(cov):
    vals, vecs = np.linalg.eigh(cov)
    #order = vals.argsort()[::-1] without order
    return vals, vecs#vals[order], vecs[:,order]
    
if __name__=='__main__':
    
    # CDM 
    #cdm_id='27386_10728_2018-06-01 09:44:54.508000_0.0002627'
    #cdm_id='27386_10728_2018-06-01 09:44:54.510000_0.01093'
    cdm_id='27386_27450_2018-06-26 01:00:44.997000_0.0001773'
    cdm = retrieveCDM(cdm_id)
    obj1_id=cdm[1]
    obj2_id=cdm[2]
    miss_distance=cdm[6] # [km]
    msg_epoch=cdm[3]
    tca=cdm[5]
    poc=cdm[14]
    # Collision Radius
    radius1, radius2=get_radius(obj1_id, obj2_id)
    rc=radius1/1000.0+radius2/1000.0
    
    # Instantiate a TLEObject
    primary=TLEObject(obj_id=obj1_id, epoch=msg_epoch)
    secondary=TLEObject(obj_id=obj2_id, epoch=msg_epoch)
    # Instantiate Alert
    alert=Alert(primary, secondary, tca)
    dates, distances= alert. compute_approach()
    # Covariance matrix in GCRF
    r_RTN, v_RTN,  maT_eci2rtn =secondary.position_in_RTN( prop_time=alert.tca_computed)
    maT_rtn2eci=maT_eci2rtn.transpose()
    socrates_covar_matrix=np.array([[0.1*0.1, 0, 0], [0, 0.3*0.3, 0], [0, 0, 0.1*0.1]]) # [km2]
    socrates_covma_GCRF=np.dot(maT_rtn2eci.transpose(), np.dot(socrates_covar_matrix,maT_rtn2eci))
    
    #========================
    # PoC limit (Alfano)
    #========================
    miss_distance=np.sqrt(np.dot(alert.r_relative_GCRF, alert.r_relative_GCRF))
    poc_limit=PoC_limit(rc,  miss_distance)
    print 'PoC limit = ',  poc_limit
    
    #========================
    # Akella B-plane
    #========================
    # i = vr, j = v_sec x v_pri, k = i x j
    vr_mod=np.sqrt(np.dot(alert.v_relative_GCRF, alert.v_relative_GCRF))
    i_ver=np.dot(1.0/vr_mod, alert.v_relative_GCRF)
    v_secxv_pri=np.cross(alert.v_sec_GCRF, alert.v_pri_GCRF)
    v_secxv_pri_mod=np.sqrt(np.dot(v_secxv_pri, v_secxv_pri))
    j_ver=np.dot(1.0/v_secxv_pri_mod, v_secxv_pri)
    k_ver=np.cross(i_ver, j_ver)
    maB_plane=np.array([i_ver, j_ver, k_ver]) # B-plane matrix transformation
    ma_conc=np.concatenate((-maB_plane,maB_plane),axis=1)
    t_star=np.array([[0, 1, 0], [0, 0, 1]])    
    t=np.dot(t_star, ma_conc)
    # Combined covariance matrix p* in B-plane
    z=(3, 3)
    z=np.zeros(z)
    p_star0=np.concatenate((socrates_covma_GCRF, z), axis=0)
    p_star1=np.concatenate((z, socrates_covma_GCRF), axis=0)
    p_star2=np.concatenate((p_star0,p_star1),axis=1)
    p_star=np.dot(t,np.dot(p_star2,t.transpose()))
    rho_0_star=np.dot(t_star, np.dot(maB_plane, alert.r_relative_GCRF.transpose()))
    # Akella PoC
    poc_ak=PoC_akella(maB_plane, rho_0_star, p_star, rc)
    print 'PoC CDM = %e' %poc
    print 'PoC Akella = %e' % poc_ak
    
    #========================
    # Klinkrad B-plane
    #========================
    r_relative_mod=np.sqrt(np.dot(alert.r_relative_GCRF, alert.r_relative_GCRF))
    Xb=np.dot(1.0/r_relative_mod, alert.r_relative_GCRF)
    rxv=np.cross(alert.r_relative_GCRF, alert.v_relative_GCRF)
    rxv_mod=np.dot(rxv, rxv)
    Yb=np.dot(1.0/rxv_mod,  rxv)
    maB_planeXY=np.array([Xb,Yb])
    r_relative_Bplane=np.dot(maB_planeXY, alert.r_relative_GCRF.transpose())
    C_B=np.dot(maB_planeXY, np.dot(socrates_covma_GCRF, maB_planeXY.transpose()))
    vals,  vects=eigsorted(C_B)
    C_Bdiag=np.array([[vals[0], 0], [0, vals[1]]])
    # PoC max Klinkrad
    PoCmax=PoCmax_Klinkrad(C_Bdiag, r_relative_Bplane, rc)
    print 'PoCmax (Klinkrad) = ',  PoCmax
    poc_klinkrad=PoC_klinkrad(C_Bdiag, rc)
    print 'PoC (Klinkrad) = ',  poc_klinkrad
    # Ellipse
    a=np.sqrt(np.max([vals[0], vals[1]]))
    b=np.sqrt(np.min([vals[0], vals[1]]))
    theta_arg=(C_B[0][0]*C_B[0][0]-C_B[1][1]*C_B[1][1])
    theta=np.arctan2(2*C_B[0][1], theta_arg)/2.0

    """
    Graphic Representation of the situation into the B-Plane
    """
    # plot parameters
    # eigenvalues, eigenvectors and angle
#    vals, vecs = eigsorted(p_star)
#    theta = np.degrees(np.arctan2(*vecs[:,0][::-1]))
#    sigma1=np.sqrt(abs(vals[1]))*1000.0
#    sigma2=np.sqrt(abs(vals[0]))*1000.0
    # add an ellipse
    ells = Ellipse((0,0),a*1000.0,b*1000.0,  theta,  fill=0)
    # add an arrow
    arrow = Arrow(0, 0, r_relative_Bplane[0]*1000.0,r_relative_Bplane[1]*1000.0,width=0.001, color='black')
    # add an circle
    circle =Circle([r_relative_Bplane[0]*1000.0,r_relative_Bplane[1]*1000.0], rc*1000.0,fc='gray', color='black') #ec="none"
    rho_0_mod=np.sqrt(np.dot(r_relative_Bplane,r_relative_Bplane))
    fig = plt.figure(0)
    ax = fig.add_subplot(111, aspect='equal')
    ax.add_artist(ells)
    ax.add_artist(circle)
    ax.add_artist(arrow)
    ells.set_clip_box(ax.bbox)
    ax.grid()
#    ax.set_xlim([- rho_0_mod*1000.0+rc, rho_0_mod*1000.0+rc])
#    ax.set_ylim([- rho_0_mod*1000.0+rc,rho_0_mod*1000.0+rc])
    ax.set_xlim(-np.max([a*1000.0,  rho_0_mod*1000.0]),np.max([a*1000.0,rho_0_mod*1000.0]))
    ax.set_ylim(-np.max([a*1000.0,rho_0_mod*1000.0]),np.max([a*1000.0, rho_0_mod*1000.0]))
    plt.title(str(obj1_id)+' and '+str(obj2_id)+' at: '+datetime.strftime(tca, '%Y-%m-%dT%H:%M:%S')+'- PoC = '+str(np.round(poc, 4)), loc='left')
    plt.show()


