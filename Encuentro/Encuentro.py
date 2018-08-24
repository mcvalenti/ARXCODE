'''
Created on 23/06/2017

@author: mcvalenti
'''
import numpy as np
from scipy.integrate import nquad
from numpy.linalg import inv
import sys
from Aplicacion.globals import tabla
from SistReferencia.sist_deCoordenadas import ricSis, ric_matrix
from datetime import datetime,timedelta
#from TleAdmin.TLE import Tle, SetTLE
from Estadistica.matrizOsweiler import calcula_matriz_Tles
from Estadistica.maCovar import EjecutaMaCovar

class Posicion:

    def __init__(self,r,v,epoca):   
        self.r=r
        self.v=v
        self.epoca=epoca
       
    def getCoordenadasGEOD(self):
        """
        Transforma coordenadas del sistem cartesiano (TEME)
        al sistema geodesico aprox.
        REVISAR!!! 
        ---------------
        outputs
            alpha, delta: angulos Geodesicos (float) [grados]
        """
        deg=np.divide(180,np.pi)
        r_mod=np.sqrt(self.r[0]*self.r[0]+self.r[1]*self.r[1]+self.r[2]*self.r[2])
        l=np.divide(self.r[0],r_mod)
        m=np.divide(self.r[1],r_mod)
        n=np.divide(self.r[2],r_mod)
        self.delta=np.arcsin(n)
        if m>0:
            self.alpha = np.arccos(np.divide(l,np.cos(self.delta)))
        else:
            self.alpha = 2*np.pi-np.arccos(np.divide(l,np.cos(self.delta)))
         
        return self.delta*deg, self.alpha*deg   

class Encuentro():
    
    def __init__(self,tle_sat,tle_deb,tca,hr):
        """
        Calcula las diferencias en posiciones y velocidades 
        para dos objetos en situacion de acercamiento, durante un 
        intervalo que se configura en el codigo (linea 94,95).
        Devuelve los parametros del encuentro:
        * minima distancia en modulo (RTN)
        * componentes de la minima distancia (R, T, N)
        * tiempo de maximo acercamiento
        * 2 archivos con las coordenadas de las trayectorias en el
          sistema geodesico.
        * 1 archivo con con las posiciones relativas del intervalo
          (RTN)
        METODOS para el caculo de la PoC.
        * Calcula la matriz de covarianzas combinadas.
        * Proyecta resultados al plano de encuentro.
        * Calcula la PoC.
        -----------------------------------------------------------
        outpus:
            3 archivos: (../Encuentro/archivos/)
                * coordenadas alfa y delta del sat.
                * coordenadas alfa y delta del deb.
                * Diferencias relativas en RTN para el intervalo breve.
            mod_minDist: Minima distancia en modulo en el sistema RTN. (float)
            tca_c: Instante del maximo acercamiento. (datetime)
            DistRic_min: coordenadas RTN relativas en el momento de min distancia (array)
        """
        
        self.tle_sat=tle_sat
        self.tle_deb=tle_deb
#         print 'Fecha del TLE del Satelite: ', self.tle_sat.epoca()
#         print 'Fecha del TLE del Desecho: ',self.tle_deb.epoca()
        self.tca=tca      
        self.hit_rad=hr 
        self.ma_sat_RTN_tca=None
        self.ma_deb_RTN_tca=None
        self.ndias_prev_sat=abs(int((self.tle_sat.epoca()-self.tca).total_seconds()/86400))
        self.ndias_prev_deb=abs(int((self.tle_deb.epoca()-self.tca).total_seconds()/86400))
#         print 'Delta Dias satelite: ',self.ndias_prev_sat
#         print 'Delta Dias Desecho: ',self.ndias_prev_deb
        """
        Genera Archivos
        """
        self.sat_id=self.tle_sat.catID()
        self.deb_id=self.tle_deb.catID()
        self.archivo_dif ='../Encuentro/archivos/'+str(self.sat_id)+'_'+str(self.deb_id)+'_rtn'
        salida1=open('../Encuentro/archivos/'+str(self.sat_id),'w+')
        salida2=open('../Encuentro/archivos/'+str(self.deb_id),'w+')
        salida3=open(self.archivo_dif,'w+')
        
        """
        Calcula las diferencias relativas entre los dos 
        objetos en el sistema RTN.
        """
#         self.epoca_ini=self.tca-timedelta(minutes=1) # 1 minutos antes de TCA
#         self.epoca_fin=self.tca+timedelta(minutes=1) # 1 minutos despues de TCA
        self.epoca_ini=self.tca-timedelta(seconds=1) # 1 segundos antes de TCA
        self.epoca_fin=self.tca+timedelta(seconds=1) # 1 segundos despues de TCA
        
        self.mod_minDist=sys.float_info.max
        epoca_ini_list=[]
        distancias_list=[]
        while self.epoca_ini < self.epoca_fin:
            r,v=self.tle_sat.propagaTLE(self.epoca_ini)
            r1,v1=self.tle_deb.propagaTLE(self.epoca_ini)
            
            r=np.array([float(r[0]),float(r[1]),float(r[2])])
            v=np.array([float(v[0]),float(v[1]),float(v[2])])
            r1=np.array([float(r1[0]),float(r1[1]),float(r1[2])])
            v1=np.array([float(v1[0]),float(v1[1]),float(v1[2])])
            
            #====================================
            # Posiciones en el ECI
            #====================================
            self.pos1=Posicion(r,v,self.epoca_ini)
            self.pos2=Posicion(r1,v1,self.epoca_ini)
            #====================================
            # Posiciones y vel relativas ECI
            #====================================
            DistVector=self.pos1.r-self.pos2.r
            VelVector=self.pos1.v-self.pos2.v
            mod_DistVector=np.sqrt(np.dot(DistVector,DistVector))
            #====================================
            # Posiciones y vel relativas RIC (RTN)
            #====================================           
            x_ric,y_ric,z_ric=ricSis(self.pos1.r,self.pos1.v,DistVector)            
            DistRic=np.array([x_ric,y_ric,z_ric])
            vx_ric,vy_ric,vz_ric=ricSis(self.pos2.r,self.pos2.v,VelVector)
            self.VelRic=np.array([vx_ric,vy_ric,vz_ric])
            mod_Dist1=np.sqrt(np.dot(DistRic,DistRic))
            
#            self.mod_Dist1=np.sqrt(np.dot(self.DistVector,self.DistVector))
            # Calculo de la distancia minima. 
            if mod_DistVector < self.mod_minDist:
                self.mod_minDist=mod_Dist1
                self.tca_c=self.epoca_ini
                self.DistRic_min=np.array([x_ric,y_ric,z_ric])
                self.vel_sat_tca=v
                self.vel_deb_tca=v1
                self.DistVector_min=DistVector
                self.VelVector_min=VelVector
                self.r_tca=r
                self.r1_tca=r1
                self.v_tca=v
                self.v1_tca=v1
#                print self.tca_c, self.mod_minDist
            self.epoca_ini=self.epoca_ini+timedelta(seconds=1)
            #self.epoca_ini=self.epoca_ini+timedelta(microseconds=1000)
            epoca_ini_list.append(self.epoca_ini)
            distancias_list.append(mod_Dist1)
            self.tca_min_data=[epoca_ini_list,distancias_list]
            #====================================
            # Distancias Minimas en RTN.
            #====================================
            print 'Vector miss distance en [RTN] : ', self.DistRic_min
            self.r_comp=self.DistRic_min[0]
            self.s_comp=self.DistRic_min[1]
            self.w_comp=self.DistRic_min[2]
            # Transformo a Coordenadas Geodesicas.
            delta1, alpha1=self.pos1.getCoordenadasGEOD()
            delta2, alpha2=self.pos2.getCoordenadasGEOD()
            # GUARDA EN ARCHIVO Posiciones en ALFA, DELTA (Seudo Geodesicas).
            salida1.write(str(alpha1)+' '+str(delta1)+' '+datetime.strftime(self.pos1.epoca,'%Y-%m-%d %H:%M:%S')+'\n')
            salida2.write(str(alpha2)+' '+str(delta2)+' '+datetime.strftime(self.pos2.epoca,'%Y-%m-%d %H:%M:%S')+'\n') 
            # GUARDA EN ARCHIVO Posiciones Relativas en RTN.
            salida3.write(datetime.strftime(self.pos1.epoca,'%Y-%m-%d %H:%M:%S')+' '+str(DistRic[0])+' '+str(DistRic[1])+' '+str(DistRic[2])+'\n')

        salida1.close()
        salida2.close()
        salida3.close()
    
    def _get_radius(self):
        radius1=8.0 # [m]
        radius2=1.0 # [m]        
        return radius1,  radius2    
    
    """Operaciones con Matrices"""
    
    def genera_maOSW_RTN(self,obj_id,epoch):
        """Ejecuta Osweiler para calcular la matriz de covarianza"""
        ini_set_deb=epoch-timedelta(days=15)
        archivo=obj_id+'_'+datetime.strftime(ini_set_deb,'%Y%m%d')+'.crudo'    
        nombre_archivo,var_r,var_t,var_n=calcula_matriz_Tles(obj_id,ini_set_deb,epoch,archivo)
        maCovar, ma_archivo=EjecutaMaCovar(nombre_archivo)
        return maCovar
    
    def suma_prop_errores(self,ma_sat_RTN,ma_deb_RTN):
        """Se calcula la cantidad de dias entre la epoca del TLE y el tca"""
        # propagacion de errores de la matriz de mision
        var_tab_r_sat=tabla[self.ndias_prev_sat][0]
        var_tab_t_sat=tabla[self.ndias_prev_sat][1]
        var_tab_c_sat=tabla[self.ndias_prev_sat][2]
        ma_sat_prop_tca=ma_sat_RTN
        ma_sat_prop_tca[0][0]=ma_sat_RTN[0][0]+var_tab_r_sat
        ma_sat_prop_tca[1][1]=ma_sat_RTN[1][1]+var_tab_t_sat
        ma_sat_prop_tca[2][2]=ma_sat_RTN[2][2]+var_tab_c_sat       
        # propagacion de errores de la matriz del desecho
        var_tab_r_deb=tabla[self.ndias_prev_deb][0]
        var_tab_t_deb=tabla[self.ndias_prev_deb][1]
        var_tab_c_deb=tabla[self.ndias_prev_deb][2]
        ma_deb_prop_tca=ma_deb_RTN
        ma_deb_prop_tca[0][0]=ma_deb_RTN[0][0]+var_tab_r_deb
        ma_deb_prop_tca[1][1]=ma_deb_RTN[1][1]+var_tab_t_deb
        ma_deb_prop_tca[2][2]=ma_deb_RTN[2][2]+var_tab_c_deb      
        return ma_sat_prop_tca, ma_deb_prop_tca
    
    def maT_rtn_eci(self,r,v,ma_RTN):
        """Transformacion al sistema inercial"""
        maT_teme2ric_sat=ric_matrix(r,v)
        R1_eci=maT_teme2ric_sat.transpose()
        a_x=[]
        a_y=[]
        a_z=[]
        for i in range(3):
            a_x.append(ma_RTN[0][i])
            a_y.append(ma_RTN[1][i])
            a_z.append(ma_RTN[2][i])
        ma_RTN=np.array([a_x,a_y,a_z])                   
        ma_eci=np.dot(R1_eci.transpose(),np.dot(ma_RTN,R1_eci))
        return ma_eci
        
    
    """Proyecciones al Plano"""
    
    def proyecta_alplano_encuentro(self,sat_maOSW_RTN,deb_maOSW_RTN):
        """Proyecta al plano de encuentro simplificado Lei-Chen"""
        #self.calculaMacombinada()
        #Calculo el angulo entre los vectores velocidad.
        cos_phi=np.dot(self.vel_sat_tca,self.vel_deb_tca)/(np.sqrt(np.dot(self.vel_sat_tca,self.vel_sat_tca))*np.sqrt(np.dot(self.vel_deb_tca,self.vel_deb_tca)))
        self.phi=np.arccos(cos_phi)
        sigma2_R=sat_maOSW_RTN[0][0]+deb_maOSW_RTN[0][0]
        sigma2_S=sat_maOSW_RTN[1][1]+deb_maOSW_RTN[1][1]
        sigma2_W=sat_maOSW_RTN[2][2]+deb_maOSW_RTN[2][2]
        mu_x=self.r_comp
        mu_y=np.sqrt(self.s_comp*self.s_comp+self.w_comp*self.w_comp)
        sigma2_x=sigma2_R
        sigma2_y=sigma2_S*np.cos(self.phi/2.0)*np.cos(self.phi/2.0)+sigma2_W*np.sin(self.phi/2.0)*np.sin(self.phi/2.0)        
        return mu_x,mu_y,sigma2_x,sigma2_y
    
    def _project_Klinkrad_Bplane(self,C1,C2):
        "Returns covariance matrix and relative distance projected in B-plane"
        ma_combinada_klinkrad=C1+C2
        r_relative_module=np.sqrt(np.dot(self.DistVector_min, self.DistVector_min))
        Xb=np.dot(1.0/ r_relative_module, self.DistVector_min)
        r_rel_x_v_rel=np.cross(self.DistVector_min, self.VelVector_min)
        r_rel_x_v_rel_mod=np.sqrt(np.dot(r_rel_x_v_rel,r_rel_x_v_rel))
        Yb=np.dot(1.0/r_rel_x_v_rel_mod, r_rel_x_v_rel)
        R_xy=np.array([Xb, Yb])
        C_B = np.dot(R_xy, (np.dot(ma_combinada_klinkrad, R_xy.transpose())))
        r_relative_B = np.dot(R_xy, self.DistVector_min.transpose())
        return  C_B,  r_relative_B 
    
    """ Integral tools """
    def f(self, y, z, rho_0, c, p_star, ra):
        """Defines the function f that is going to be integrated"""
        t_star=np.array([[0, 1, 0], [0, 0, 1]])    
        rho_0_star=np.dot(t_star, np.dot(c, rho_0))
        rho_star=np.dot(t_star, np.dot(c, [0, y, z]))
        diff=rho_star-rho_0_star
        p_star_inv=inv(p_star)
        s_star0=np.dot(p_star_inv, diff)
        s_star=np.dot(diff.transpose(), s_star0)
        return np.exp(-s_star)

    def bounds_y(self, rho_0, c, p_star, ra):
        return [-ra, ra]

    def bounds_z(self, y, rho_0, c, p_star, ra):
        return [-np.sqrt(ra*ra-y*y), np.sqrt(ra*ra-y*y)]
    
    """ Calculos de PoC """
    
    def calculaPoC_limite(self):
        """ PoC - Metodo de cota limite de Alfano """
        erre=self.hit_rad/self.mod_minDist
        if erre < 0.8:
            PoC_limit=0.48394*erre
        else:
            PoC_limit=0.21329*np.exp(1.01511*erre)-0.09025
        return PoC_limit
        
    def calculaPoC_circ(self):
        """PoC - Metodo simplificado de Lei-Chen"""
        #=======================================================================
        # Generacion y propagacion de las matrices de covarianza en RTN
        #=======================================================================
        # OSWEILER
#         sat_maOSW_RTN=self.genera_maOSW_RTN(self.tle_sat.catID(),self.tle_sat.epoca())
#         deb_maOSW_RTN=self.genera_maOSW_RTN(self.tle_deb.catID(), self.tle_deb.epoca())
        # Propagacion de errores.
#        self.ma_sat_RTN_tca, self.ma_deb_RTN_tca=self.suma_prop_errores(sat_maOSW_RTN, deb_maOSW_RTN)
        #------------------------------------------------------------------------
        # SOCRATES
        sat_maSOC_RTN=np.array([[0.1*0.1,0,0],[0,0.3*0.3,0],[0,0,0.1*0.1]])
        deb_maSOC_RTN=np.array([[0.1*0.1,0,0],[0,0.3*0.3,0],[0,0,0.1*0.1]])
        # Propagacion de errores.
        #self.ma_sat_RTN_tca, self.ma_deb_RTN_tca=self.suma_prop_errores(self.ma_sat_RTN_tca, self.ma_deb_RTN_tca)
        self.ma_sat_RTN_tca=sat_maSOC_RTN
        self.ma_deb_RTN_tca=deb_maSOC_RTN
        #--------------------------------------------------------------------------
        self.ma_sat_RTN_tca, self.ma_deb_RTN_tca=self.suma_prop_errores(self.ma_sat_RTN_tca, self.ma_deb_RTN_tca)
        mu_x,mu_y,var_x,var_y=self.proyecta_alplano_encuentro(self.ma_sat_RTN_tca, self.ma_deb_RTN_tca)
        pocVsra=open('../Validaciones/pocvsra.txt','w')
        ra=self.hit_rad
        PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/var_x)+(mu_y*mu_y/var_y)))*(1-np.exp(-ra*ra/(2.0*np.sqrt(var_x)*np.sqrt(var_y))))
        pocVsra.write(str(ra)+' '+str(PoC)+'\n')
#         ra=0.001
#         while ra<0.03:
#             PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/var_x)+(mu_y*mu_y/var_y)))*(1-np.exp(-ra*ra/(2.0*np.sqrt(var_x)*np.sqrt(var_y))))
#             PoC_int=PoC_int=dblquad(lambda y, x: (1.0/(2.0*np.pi*np.sqrt(var_x)*np.sqrt(var_y)))*np.exp((-1.0/2.0)*((x*x/(var_x))+(y*y/(var_y)))), mu_x-ra, mu_x+ra, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)
#             pocVsra.write(str(ra)+' '+str(PoC)+'\n')
#             ra=ra+0.0003  
        print 'POC explicita de CHAN =%e ' % PoC 
        return PoC
                
    def calculaPoC_akella(self):    
        """ PoC - Metodo de cota limite de Alfano """
        #=======================================================================
        # MATRICES DE COVARIANZA
        # Generacion, propagacion y transformacion al ECI
        #=======================================================================
        # OSWEILER
#        sat_maOSW_RTN=self.genera_maOSW_RTN(self.tle_sat.catID(),self.tle_sat.epoca())
#        deb_maOSW_RTN=self.genera_maOSW_RTN(self.tle_deb.catID(), self.tle_deb.epoca())
#         # Propagacion de errores.
#        self.ma_sat_RTN_tca, self.ma_deb_RTN_tca=self.suma_prop_errores(sat_maOSW_RTN, deb_maOSW_RTN)
        #------------------------------------------------------------------------
        # SOCRATES
        sat_maSOC_RTN=np.array([[0.1*0.1,0,0],[0,0.3*0.3,0],[0,0,0.1*0.1]])
        deb_maSOC_RTN=np.array([[0.1*0.1,0,0],[0,0.3*0.3,0],[0,0,0.1*0.1]])
#         # Propagacion de errores.
        self.ma_sat_RTN_tca, self.ma_deb_RTN_tca=self.suma_prop_errores(sat_maSOC_RTN, deb_maSOC_RTN)
        #------------------------------------------------------------------------
        # Transformacion de las matrices ya propagadas al sistema ECI
        self.ma_sat_eci=self.maT_rtn_eci(self.r_tca,self.v_tca,self.ma_sat_RTN_tca)
        self.ma_deb_eci=self.maT_rtn_eci(self.r1_tca,self.v_tca,self.ma_deb_RTN_tca)
        # Construyo R_B: transformation matrix to B-plane
        v_relative_module=np.sqrt(np.dot(self.VelVector_min,self.VelVector_min))
        i_ax=np.dot(1.0/v_relative_module, self.VelVector_min)
        v1_ak=self.v_tca
        v2_ak=self.v1_tca
        v2xv1=np.cross(v2_ak, v1_ak)
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
        p_star0=np.concatenate((self.ma_sat_eci, z), axis=0)
        p_star1=np.concatenate((z, self.ma_deb_eci), axis=0)
        p_star2=np.concatenate((p_star0,p_star1),axis=1)
        p_star=np.dot(t,np.dot(p_star2,t.transpose()))
        # PoC integral partial calculus
        rho_0=self.DistVector_min
        #rho_0_star=np.dot(t_star, np.dot(R_B, rho_0.transpose()))
        # PoC 
        radius_obj1,  radius_obj2=self._get_radius()
        r_c= self.hit_rad #radius_obj1/1000.0+radius_obj2/1000.0
        coeff=1.0/(2*np.pi*np.sqrt(np.linalg.det(p_star)))
        poc_integral,  err= nquad(self.f, [self.bounds_z, self.bounds_y], args=(rho_0, R_B, p_star, r_c)) # double integrals 
        poc_ak = coeff*poc_integral
        print 'PoC Akella =%e ' %  poc_ak
        return poc_ak

#     def calculaPoC_klinkrad(self):
#         """ Klinkrad expression based on the most adverse possible configuration """
#         radius_obj1,  radius_obj2=self._get_radius()
#         r_c=radius_obj1/1000.0+radius_obj2/1000.0
#         #=======================================================================
#         # Generacion, propagacion y transformaciones de la matriz de covarianzas
#         #=======================================================================
#         # OSWEILER
#         sat_maOSW_RTN=self.genera_maOSW_RTN(self.tle_sat.catID(),self.tle_sat.epoca())
#         deb_maOSW_RTN=self.genera_maOSW_RTN(self.tle_deb.catID(), self.tle_deb.epoca())
#         self.ma_sat_RTN_tca, self.ma_deb_RTN_tca=self.suma_prop_errores(sat_maOSW_RTN, deb_maOSW_RTN)
#         ma_sat_eci=maT_rtn2eci(self.r_tca,self.v_tca,self.ma_sat_RTN_tca)
#         ma_deb_eci=maT_rtn2eci(self.r1_tca,self.v_tca,self.ma_deb_RTN_tca)
#         # Proyeccion al plano
#         C_B,  r_relative_B=self._project_Klinkrad_Bplane(ma_sat_eci,ma_deb_eci)
#         vector_product=np.dot(r_relative_B.transpose(), np.dot(inv(C_B),r_relative_B))
#         det=np.linalg.det(C_B)
#         if det < 0:
#             myError = ValueError('Covariance matrix determinant should be a positive')
#             raise myError
#         poc_max=r_c*r_c/(np.exp(1.0)*np.sqrt(det)*vector_product)
#         print 'PoC max KLINKRAD =%e ' %  poc_max         
#         #================
#         # POC 1D
#         #================
#         #sigma_r=np.sqrt(0.1*0.1+0.3*0.3+0.1*0.1)
#         C, C1_eci, C2_eci=self.calculaMacombinada()
#         sigma_r=np.sqrt(C[0][0]+C[1][1]+C[2][2])
#         coef=1.0/(np.sqrt(2*np.pi)* sigma_r)
#         result = integrate.quad(lambda r:np.exp(-(r-self.mod_minDist)*(r-self.mod_minDist)/(2*sigma_r)) , -ra,ra)
#         print 'PoC 1D = ', coef*result[0]    
        
    
