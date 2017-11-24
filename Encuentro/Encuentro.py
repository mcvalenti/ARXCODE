'''
Created on 23/06/2017

@author: mcvalenti
'''
import numpy as np
from scipy.integrate import dblquad
import sys
from Aplicacion.globals import tabla
from SistReferencia.sist_deCoordenadas import ricSis
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
    
    def __init__(self,tle_sat,tle_deb,tca,n):
        """
        Calcula las diferencias en posiciones y velocidades 
        para dos objetos en situacion de acercamiento, durante un 
        intervalo que inicia 5 minutos antes y termina 5 minutos
        despues del TCA.
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
        self.tca=tca  
        self.ndias_prev=n      
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
#        self.epoca_ini=self.tca-timedelta(minutes=5) # 5 minutos antes de TCA
#        self.epoca_fin=self.tca+timedelta(minutes=5) # 5 minutos despues de TCA
        self.epoca_ini=self.tca-timedelta(seconds=3) # 3 segundos antes de TCA
        self.epoca_fin=self.tca+timedelta(seconds=3) # 3 segundos despues de TCA
        
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
            if mod_Dist1 < self.mod_minDist:
                self.mod_minDist=mod_Dist1
                self.tca_c=self.epoca_ini
                self.DistRic_min=np.array([x_ric,y_ric,z_ric])
                self.vel_sat_tca=v
                self.vel_deb_tca=v1
#                print self.tca_c, self.mod_minDist
#            self.epoca_ini=self.epoca_ini+timedelta(seconds=1)
            self.epoca_ini=self.epoca_ini+timedelta(microseconds=100000)
            epoca_ini_list.append(self.epoca_ini)
            distancias_list.append(mod_Dist1)
            self.tca_min_data=[epoca_ini_list,distancias_list]
            #====================================
            # Distancias Minimas en RTN.
            #====================================
            self.r_comp=self.DistRic_min[0]
            self.s_comp=self.DistRic_min[1]
            self.w_comp=self.DistRic_min[2]
    
            #Calculo el angulo entre los vectores velocidad.
            cos_phi=np.dot(self.vel_sat_tca,self.vel_deb_tca)/(np.sqrt(np.dot(self.vel_sat_tca,self.vel_sat_tca))*np.sqrt(np.dot(self.vel_deb_tca,self.vel_deb_tca)))
            self.phi=np.arccos(cos_phi)
            # Transformo a Coordenadas Geodesicas.
            delta1, alpha1=self.pos1.getCoordenadasGEOD()
            delta2, alpha2=self.pos2.getCoordenadasGEOD()
            # GUARDA EN ARCHIVO Posiciones en ALFA, DELTA (Seudo Geodesicas).
            salida1.write(str(alpha1)+' '+str(delta1)+' '+datetime.strftime(self.pos1.epoca,'%Y-%m-%d %H:%M:%S')+'\n')
            salida2.write(str(alpha2)+' '+str(delta2)+' '+datetime.strftime(self.pos2.epoca,'%Y-%m-%d %H:%M:%S')+'\n') 
            # GUARDA EN ARCHIVO Posiciones Relativas en RTN.
            salida3.write(datetime.strftime(self.pos1.epoca,'%Y-%m-%d %H:%M:%S')+' '+str(DistRic[0])+' '+str(DistRic[1])+' '+str(DistRic[2])+'\n')

        print 'Fin del procesamiento de Encuentro'
        salida1.close()
        salida2.close()
        salida3.close()
        
    def calculaMacombinada(self):
        """
        1 - Calculo la matriz del desecho x OSW.
        2 - Calculo la matriz de la mision x OSW (con TLEs).
        3 - Corrijo ambas matrices por tabla de Marce al TCA - n dias adelante.
        4 - Calculo la matriz combinada, suma de las matrices anteriores.
        --------------------------------------------------------------        
        """
        deb_id=self.tle_deb.catID()
        ini_set_sat=self.tle_sat.epoca()-timedelta(days=15)
        fin_set_sat=self.tle_sat.epoca()
        sat_id=self.tle_sat.catID()
        ini_set_deb=self.tle_deb.epoca()-timedelta(days=15)
        fin_set_deb=self.tle_deb.epoca()
        
        #=============================================================
        # 1 - MATRIZ DEL DESECHO 
        #=============================================================
        archivo=deb_id+'_'+datetime.strftime(ini_set_deb,'%Y%m%d')+'.crudo'    
        nombre_archivo,var_r,var_t,var_n=calcula_matriz_Tles(deb_id,ini_set_deb,fin_set_deb,archivo)
        maCovar_deb, ma_archivo=EjecutaMaCovar(nombre_archivo)
         
        print '*******************************************************'
        print '-----------------Varianzas DESECHO---------------------'
        print '*******************************************************'
        print 'Var en R = ', var_r 
        print 'Var en T = ', var_t
        print 'Var en N = ', var_n
        print '*******************************************************'
        print '-----------------Ma. Desecho---------------------------'
        print '*******************************************************'
        for k in maCovar_deb[:3]:
            print k[:3]
        #=============================================================    
        # 2 - MATRIZ DE LA MISION 
        #=============================================================
        ini_set_sat=self.tle_sat.epoca()-timedelta(days=15)
        fin_set_sat=self.tle_sat.epoca()
        archivo_sat=sat_id+'_'+datetime.strftime(ini_set_sat,'%Y%m%d')+'.crudo'    
        nombre_archivo_sat,var_r_sat,var_t_sat,var_n_sat=calcula_matriz_Tles(sat_id,ini_set_sat,fin_set_sat,archivo_sat)
        maCovar_sat, ma_archivo_sat=EjecutaMaCovar(nombre_archivo_sat)
        
        print '*******************************************************'
        print '-----------------Varianzas MISION----------------------'
        print '*******************************************************'
        print 'Var en R = ', var_r_sat
        print 'Var en T = ', var_t_sat
        print 'Var en N = ', var_n_sat
        print '*******************************************************'
        print '-----------------Ma. MISION----------------------------'
        print '*******************************************************'
 #       for k in maCovar_sat[:3]:
 #           print k[:3]
        #=============================================================
        # 3 -Corrijo ambas matrices por tabla de Marce al TCA -
        # n dias adelante.
        #=============================================================
#         var_tab_r=tabla[self.ndias_prev][0]
#         var_tab_t=tabla[self.ndias_prev][1]
#         var_tab_c=tabla[self.ndias_prev][2]
#         
#         maCovar_deb[0][0]=maCovar_deb[0][0]+var_tab_r
#         maCovar_deb[1][1]=maCovar_deb[1][1]+var_tab_t
#         maCovar_deb[2][2]=maCovar_deb[2][2]+var_tab_c
# 
#         maCovar_sat[0][0]=maCovar_sat[0][0]-var_tab_r
#         maCovar_sat[1][1]=maCovar_sat[1][1]-var_tab_t
#         maCovar_sat[2][2]=maCovar_sat[2][2]-var_tab_c 
        #=============================================================
        # 4 - Calculo la matriz combinada, suma de las matrices
        # anteriores. En el sistema RTN.
        #=============================================================    
        self.matriz_combinada=maCovar_sat+maCovar_deb

        return self.matriz_combinada, maCovar_sat, maCovar_deb
    
    def proyecta_alplano_encuentro(self):
    #============================================
    # Calcula los errores combinados proyectados.
    #============================================
        self.calculaMacombinada()
        mu_x=self.r_comp
        mu_y=np.sqrt(self.s_comp*self.s_comp+self.w_comp*self.w_comp)
        var_x=self.matriz_combinada[0][0]
        var_y=self.matriz_combinada[1][1]*np.cos(self.phi/2.0)*np.cos(self.phi/2.0)+self.matriz_combinada[2][2]*np.sin(self.phi/2.0)*np.sin(self.phi/2.0)
        
        return mu_x,mu_y,var_x,var_y
    
    def calculaPoC_circ(self):
        mu_x,mu_y,var_x,var_y=self.proyecta_alplano_encuentro()
        pocVsra=open('../Validaciones/pocvsra.txt','w')
        ra=0.01
        PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/var_x)+(mu_y*mu_y/var_y)))*(1-np.exp(-ra*ra/(2.0*np.sqrt(var_x)*np.sqrt(var_y))))
        PoC_int=PoC_int=dblquad(lambda y, x: (1.0/(2.0*np.pi*np.sqrt(var_x)*np.sqrt(var_y)))*np.exp((-1.0/2.0)*((x*x/(var_x))+(y*y/(var_y)))), mu_x-ra, mu_x+ra, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)
        pocVsra.write(str(ra)+' '+str(PoC)+'\n')
#         ra=0.001
#         while ra<0.03:
#             PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/var_x)+(mu_y*mu_y/var_y)))*(1-np.exp(-ra*ra/(2.0*np.sqrt(var_x)*np.sqrt(var_y))))
#             PoC_int=PoC_int=dblquad(lambda y, x: (1.0/(2.0*np.pi*np.sqrt(var_x)*np.sqrt(var_y)))*np.exp((-1.0/2.0)*((x*x/(var_x))+(y*y/(var_y)))), mu_x-ra, mu_x+ra, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)
#             pocVsra.write(str(ra)+' '+str(PoC)+'\n')
#             ra=ra+0.0003            
        return PoC, PoC_int[0]
    
    def calculaPoC_gral(self):
        pass