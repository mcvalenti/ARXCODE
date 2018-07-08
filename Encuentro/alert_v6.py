"""A Risk conjunction between two Space Objects"""
import sys
import numpy as np
from scipy.integrate import  nquad
import scipy.integrate as integrate
import scipy.linalg
from scipy.linalg import inv
from datetime import datetime,  timedelta
from object_v6 import TLEObject
from CDM import CDM

class Alert():
    """
    Everytime a conjunction risk is predicted, an Alert containing minimun
    distance and time of close approach  it could be generated with the
    'compute_approach' method.
    input:
        primary: SpaceObject instance
        secondary: SpaceObject instance
        tca: time of closest approach - datetime
    """
    def __init__(self, primary, secondary, tca):
        self.primary = primary
        self.secondary= secondary
        self.time_close_approach=tca
        self.r_pri_GCRF=None
        self.v_pri_GCRF=None
        self.r_sec_GCRF=None
        self.v_sec_GCRF=None
        self.r_relative_GCRF=None # at tca computed by default
        self.v_relative_GCRF=None # at tca computed by default
        self.combine_cov_matrix=None
        self.min_relative_distance_RTN=None
        self.miss_distance_computed=None
        self.tca_computed=None
        self.poc=None
        self.poc_max=None
    
    def _get_radius(self):
        radius1=8.0 # [m]
        radius2=1.0 # [m]        
        return radius1,  radius2
        
    def compute_relative_distance_in_RTN(self, prop_time=None):
        """
        Gets both, primary and secondary inercial positions and computes their
        relative distances in the satellite-based reference system RTN.
        """
        prop_time= prop_time if prop_time is not None else self.time_close_approach
        r_primary_GCRF,  v_primary_GCRF=self.primary.position_in_GCRF(prop_time)
        r_secondary_GCRF,  v_secondary_GCRF=self.secondary.position_in_GCRF(prop_time)
        r_RTN, v_RTN,  maT_eci2rtn=self.primary.position_in_RTN(prop_time)
        distance=np.array(r_secondary_GCRF)-np.array(r_primary_GCRF)
        relative_distance_RTN = np.dot(maT_eci2rtn.transpose(),distance)
        return relative_distance_RTN    
        
    def compute_relative_distance_in_ECI(self, epoch):
        """
        Takes both, primary and secondary inercial positions and computes their
        relative distance throught Skyfield library.
        note! Skyfield does not compute velocities in ECI
        """
        r_primary_ECI=self.primary.position_in_ECI(epoch)
        r_secondary_ECI=self.secondary.position_in_ECI(epoch)
        distance=r_secondary_ECI-r_primary_ECI
        return distance
        
    def compute_relative_distance_in_GCRF(self, prop_time=None):
        """
        Gets both, primary and secondary GCRF positions and computes their
        relative distances (at the tca computed and/or tca from the message by default)
        in the GCRF reference system.
        note! as Skyfield does not compute velocities in ECI, GCRF is done to
        differenciate this procedures that involves: SGP4 propagation (TEME) + Skyfield and
        NOVAS transformations.
        """
        prop_time= prop_time if prop_time is not None else self.time_close_approach
        #Relative Distance
        self.r_pri_GCRF=self.primary.position_in_GCRF(prop_time)[0]
        self.v_pri_GCRF=self.primary.position_in_GCRF(prop_time)[1]
        self.r_sec_GCRF=self.secondary.position_in_GCRF(prop_time)[0]
        self.v_sec_GCRF=self.secondary.position_in_GCRF(prop_time)[1]
        self.r_relative_GCRF=np.array(self.r_sec_GCRF)-np.array(self.r_pri_GCRF)
        self.v_relative_GCRF=np.array(self.v_sec_GCRF)-np.array(self.v_pri_GCRF)
        return  self.r_relative_GCRF
        
    def compute_relative_distance_in_TEME(self, prop_time=None):
        """
        Gets both, primary and secondary TEME positions and computes their
        relative distances (at the tca computed and/or tca from the message by default)
        in the TEME reference system.
        this procedures involves SGP4 propagation (TEME)
        """
        prop_time= prop_time if prop_time is not None else self.time_close_approach
        #Relative Distance
        self.r_pri_TEME=self.primary._position_in_TEME(prop_time)[0]
        self.v_pri_TEME=self.primary._position_in_TEME(prop_time)[1]
        self.r_sec_TEME=self.secondary._position_in_TEME(prop_time)[0]
        self.v_sec_TEME=self.secondary._position_in_TEME(prop_time)[1]
        self.r_relative_TEME=np.array(self.r_sec_TEME)-np.array(self.r_pri_TEME)
        self.v_relative_TEME=np.array(self.v_sec_TEME)-np.array(self.v_pri_TEME)
        return  self.r_relative_TEME
        
    def compute_approach(self, previous_offset=500000, post_offset=500000, step=1000):
        """
        Defines an interval around the datetime of interest, makes propagations
        and computes relative distances between objects. 
        Finally gets, miss distance, tca and RTN relative miss distances.                 
        Parameters:
            previous_offset  -- defines microseconds previous interval [microseconds]
            post_offset        -- defines microseconds post interval [microseconds]
            step                   -- step size of the propagation  [microseconds]
        """
        # Define a period for analysis.
        epoch_ini=self.time_close_approach-timedelta(microseconds=previous_offset)
        epoch_fin=self.time_close_approach+timedelta(microseconds=post_offset)
        dates=[]
        distances=[]
        distances_rtn=[]
        print 'Processing propagations, PLEASE WAIT! ...'
        self.miss_distance_computed=sys.float_info.max
        while epoch_ini < epoch_fin:
            # in GCRF
            relative_distance_GCRF=self.compute_relative_distance_in_GCRF(epoch_ini)
            distance=np.sqrt(np.dot(relative_distance_GCRF, relative_distance_GCRF))
            # in TEME
#            relative_distance_TEME=self.compute_relative_distance_in_TEME(epoch_ini)
#            distance=np.sqrt(np.dot(relative_distance_TEME, relative_distance_TEME))
            dates.append(epoch_ini)
            distances.append(distance)
            distances_rtn.append(relative_distance_GCRF)
            epoch_ini=epoch_ini + timedelta(microseconds=step)
        distances=np.array(distances)
        self.miss_distance_computed=distances.min()
        idx = np.argmin(distances)
        self.tca_computed=dates[idx]
        self.min_relative_distance_RTN=distances_rtn[idx]
        self.compute_relative_distance_in_GCRF(self.tca_computed)
        return dates, distances

    """ PoC methods """
    def PoC_limit(self):
        """ Alfano expression without considering error information"""
        radius_obj1,  radius_obj2=self._get_radius()
        r_c=radius_obj1/1000.0+radius_obj2/1000.0
        erre=r_c/self.miss_distance_computed
        if erre < 0.8:
            PoC_limit=0.48394*erre
        else:
            PoC_limit=0.21329*np.exp(1.01511*erre)-0.09025
        return  PoC_limit  
    
    def _project_Klinkrad_Bplane(self, C_GCRF,  r_relative_GCRF):
        "Returns covariance matrix and relative distance projected in B-plane"
        r_relative_module=np.sqrt(np.dot(self.r_relative_GCRF, self.r_relative_GCRF))
        Xb=np.dot(1.0/ r_relative_module, self.r_relative_GCRF)
        r_rel_x_v_rel=np.cross(self.r_relative_GCRF, self.v_relative_GCRF)
        r_rel_x_v_rel_mod=np.sqrt(np.dot(r_rel_x_v_rel,r_rel_x_v_rel))
        Yb=np.dot(1.0/r_rel_x_v_rel_mod, r_rel_x_v_rel)
        R_xy=np.array([Xb, Yb])
        C_B = np.dot(R_xy, (np.dot(C_GCRF, R_xy.transpose())))
        r_relative_B = np.dot(R_xy, r_relative_GCRF)
        return  C_B,  r_relative_B 
        
    def PoC_maxima(self,  C_GCRF,  r_relative_GCRF):
        """ Klinkrad expression based on the most adverse posible configuration """
        radius_obj1,  radius_obj2=self._get_radius()
        r_c=radius_obj1/1000.0+radius_obj2/1000.0
        C_B,  r_relative_B=self._project_Klinkrad_Bplane(C_GCRF,  r_relative_GCRF)
        vector_product=np.dot(r_relative_B.transpose(), np.dot(inv(C_B),r_relative_B))
        det=np.linalg.det(C_B)
        if det < 0:
            myError = ValueError('Covariance matrix determinant should be a positive')
            raise myError
        self.poc_max=r_c*r_c/(np.exp(1.0)*np.sqrt(det)*vector_product)
        return self.poc_max
        
    def PoC_one_dimensional(self,sigma_r=None):
        """ This method computes a One Dimentional integral 1D"""
        sigma_r= sigma_r if sigma_r is not None else np.sqrt(0.1*0.1+0.3*0.3+0.1*0.1)
        radius_obj1,  radius_obj2=self._get_radius()
        r_c=radius_obj1/1000.0+radius_obj2/1000.0
        coef=1.0/(np.sqrt(2*np.pi)* sigma_r)
        result = integrate.quad(lambda r:np.exp(-(r-self.miss_distance_computed)*(r-self.miss_distance_computed)/(2*sigma_r)) , -r_c,r_c)
        return coef*result[0] 
        
        
    def PoC_Akella(self, C1_GCRF, C2_GCRF):
        """
        * C matrix generation (b-plane)
        * T and T* generation
        *   P* generation
        """
        # Construyo R_B: transformation matrix to B-plane
        v_relative_module=np.sqrt(np.dot(self.v_relative_GCRF,self.v_relative_GCRF))
        i_ax=np.dot(1.0/v_relative_module, self.v_relative_GCRF)
        v1=self.primary.position_in_GCRF(self.tca_computed)[1]
        v2=self.secondary.position_in_GCRF(self.tca_computed)[1]
        v2xv1=np.cross(v2, v1)
        v2xv1_mod=np.sqrt(np.dot(v2xv1, v2xv1))
        j_ax=np.dot(1.0/v2xv1_mod, v2xv1)
        k_ax=np.cross(i_ax, j_ax)
        R_B=np.array([i_ax, j_ax, k_ax])
        #  t* and t
        t_star=np.array([[0,1,0],[0,0,1]])
        R_B0=np.concatenate((-R_B,R_B),axis=1)
        t=np.dot(t_star, R_B0)
        # p* covariances matrices
        z=(3, 3)
        z=np.zeros(z)
        p_star0=np.concatenate((C1_GCRF, z), axis=0)
        p_star1=np.concatenate((z, C2_GCRF), axis=0)
        p_star2=np.concatenate((p_star0,p_star1),axis=1)
        p_star=np.dot(t,np.dot(p_star2,t.transpose()))
        # PoC integral partial calculus
        rho_0=self.r_relative_GCRF
        #rho_0_star=np.dot(t_star, np.dot(R_B, rho_0.transpose()))
        # PoC 
        radius_obj1,  radius_obj2=self._get_radius()
        r_c=radius_obj1/1000.0+radius_obj2/1000.0
        coeff=1.0/(2*np.pi*np.sqrt(np.linalg.det(p_star)))
        poc_integral,  err= nquad(self.f, [self.bounds_z, self.bounds_y], args=(rho_0, R_B, p_star, r_c)) # double integrals 
        poc_ak = coeff*poc_integral
        return poc_ak
        
        
    def __diagonalize(self, matrix_U):
        """
        Diagonalize matrix_U.
        TODO! # Verify that off-diagonal elements are close to zero
        """
        (eig_vals, eig_vecs) = scipy.linalg.eig(matrix_U)
        eig_length = len(eig_vecs)
        assert(len(eig_vals) == eig_length)
        # Create the diagonalization matrix V
        matrix_V = np.matrix(eig_vecs) 
        # Multiply V^{-1} * U * V to diagonalize
        matrix_W = matrix_V.I * matrix_U * matrix_V
        return (matrix_W)        
        
        
if __name__=="__main__":
    #==================================
    # CDM input
    #==================================
    #file_name='CSK3T_CA_2018-01-05.txt'
    #file_name='CSK3T_CA_2018-03-03.txt'
    #file_name='DSAT_CDM_2018-01-19.txt'
    #file_name='DSAT_CDM_2018-01-20.txt'
    #file_name='DSAT_CDM_2018-01-21.txt'
    #file_name='DSAT_CDM1_2018-04-06.txt' # with PoC
    #file_name='CSK3T_CA_2018-03-03.txt'   # with PoC
    file_name='DSAT_CDM2_2018-04-06.txt' # with PoC
    # define a CDM class
    myCDM = CDM('CDM/'+file_name)
    sat_id= int(myCDM.O1_OBJECT_DESIGNATOR)
    deb_id= int(myCDM.O2_OBJECT_DESIGNATOR)            
    tca=datetime.strptime(myCDM.TCA.strip(),'%Y-%m-%dT%H:%M:%S.%f')
    msg_miss_distance=myCDM.MISS_DISTANCE/1000.0
    poc=myCDM.COLLISION_PROBABILITY
    print '================ CDM DATA =================='
    print 'Relative Distance Module in CDM: ', 
    print 'Miss Distance: ',  myCDM.MISS_DISTANCE
    print 'TCA: ', tca
    print 'Relative Distance in RTN: ', myCDM.RELATIVE_POSITION_R, myCDM.RELATIVE_POSITION_T, myCDM.RELATIVE_POSITION_N
    print 'PoC = %e ' %poc
    print '=================================='
    filename_date=file_name.split('_')[2].split('.')[0]
    cdm_date=datetime.strptime(filename_date, '%Y-%m-%d')
    primary=TLEObject(obj_id=str(sat_id),epoch=cdm_date)
    secondary=TLEObject(obj_id=str(deb_id), epoch=cdm_date)
    #==================================
    # ALERT
    #==================================
    alert1=Alert(primary,secondary, tca)
    dates, distances= alert1. compute_approach()
    print '================ Computed DATA =================='
    print 'Computed TCA: ', alert1.tca_computed
    print  'Computed miss distance [m]: ',  alert1.miss_distance_computed*1000.0
    print 'Computed Relative Distance in RTN: ', alert1.min_relative_distance_RTN
    #==================================
    # PoC
    #==================================
    """ PoC limit"""
    PoC_limit=alert1.PoC_limit()
    print 'PoC Limit method =%e' % PoC_limit
    """ Klinkrad """
    r_relative_GCRF=alert1.r_relative_GCRF
    # transformar la matriz de covarianza al sistema GCRF
    r_pri_RTN, v_pri_RTN,  R_1 =primary.position_in_RTN( prop_time=alert1.tca_computed)
    r_sec_RTN, v_sec_RTN,  R_2 =secondary.position_in_RTN( prop_time=alert1.tca_computed)
    R_1=R_1.transpose() # to get GCRF
    R_2=R_2.transpose()
    C_RTN=np.array([[0.1*0.1, 0, 0], [0, 0.3*0.3, 0], [0, 0, 0.1*0.1]]) # [km2] Socrates values
    C1_GCRF=np.dot(R_1, np.dot(C_RTN,R_1.transpose()))
    C2_GCRF=np.dot(R_2, np.dot(C_RTN,R_2.transpose()))
    C_GCRF=C1_GCRF+C2_GCRF
    # PoC
    PoC_max=alert1.PoC_maxima(C_GCRF,  r_relative_GCRF)
    print 'PoC maxima (Klinkrad) =%e' % PoC_max
    """ PoC 1D integral """
    PoC_1D=alert1.PoC_one_dimensional()
    print 'PoC 1 Dimension =%e' % PoC_1D
    """ PoC Akella"""
    PoC_Akella=alert1.PoC_Akella(C1_GCRF, C2_GCRF)
    print 'PoC Akella =%e' % PoC_Akella
        
    print '==== Done! ========='
    #==================================
    #Plot
    #==================================
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.grid(True)
    fig.autofmt_xdate()
    plt.plot(dates,distances)
    plt.title('Conjunction: '+str(sat_id)+' and '+str(deb_id)+' at: '+datetime.strftime(tca, '%Y-%m-%dT%H:%M:%S.%f'), loc='left')
    plt.axhline(y=alert1.miss_distance_computed, color='blue', linestyle='--')
    plt.axvline(x=alert1.tca_computed, color='blue', linestyle='--')
    plt.axhline(y=msg_miss_distance, color='r', linestyle='--')
    plt.axvline(x=tca, color='r', linestyle='--')
    plt.ylabel('Distances [Km]')
    plt.xlabel('Time')
    plt.savefig(str(sat_id)+'_&_'+str(deb_id)+'.png')
    plt.show()



    
    
