'''
Created on 19/06/2017

Utiliza la expresion explicita simplificada para el calculo
de la Probabilidad de Colision.
Requiere: 
*Las diferencias en el TCA, en R,S,W. 
*Los errores en el plano x,y (B-plane).
*El radio de riesgo ra.
P=exp[-1/2(mux2/sigmax2 + muy2/sigmay2)]*[1-exp[-(ra2/2*sigmax*sigmay)]]

@author: mcvalenti
'''
import os, glob
import numpy as np
from scipy.integrate import quad, dblquad
from datetime import datetime
from pruebas.claseTle import Tle, Encuentro
from TleAdmin.TleArchivos import divide_setTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles
from SistReferencia.sist_deCoordenadas import ricSis
from visual.trackencuentro import grafica_track

"""
PASOS.
----------------------------
1 - Ejecutar el encuentro para obtener las diferencias en R,S,W.
    Calcular muX, muY.
    Calcular el angulo phi entre los vectores velocidad.
2 - Ejecutar Osweiler para obtener los errores en R,S,W para ambos objetos.
    Sumarlos y obtener los sigmaR, sigmaS y sigmaW combinados.
    *Tiene que ejecutar Osweiler con CODS. 
3 - Calcular los sigmaX, sigmaY
4 - Reemplazar en PoC y calcular. 
"""

def proc_encuentroSimple(sat_id,deb_id,tca):
    """
    Propaga los objetos involucrados un intervalos [tca-90:tca+20]
    Calcula:
        Miss Distance
        TCA calculado
        Diferencias en RTN ---> Plotea.
        Genera archivo lat, long ---> Plotea.
      
    """
    # Importar los TLE de NORAD.

    usuario='macecilia'
    clave='MaCeciliaSpace17'
    tle_sat=Tle.creadoxParam(usuario, clave, sat_id, tca)
    tle_deb=Tle.creadoxParam(usuario, clave, deb_id, tca)
    
    """
    Propagacion hasta el Encuentro
    """
    r_sat,v_sat=tle_sat.propagaTLE(tca)
    r_deb,v_deb=tle_deb.propagaTLE(tca)
    
    encuentro1=Encuentro(tle_sat,tle_deb,tca)
    vector_rsw=encuentro1.DistRic_min

    print 'Minima Distancia = ', encuentro1.mod_minDist,encuentro1.tca_c
    grafica_track('../Encuentro/archivos/'+str(sat_id)+'U', '../Encuentro/archivos/'+str(deb_id)+'U')

    return r_sat,v_sat,r_deb,v_deb,vector_rsw

def metodoOSWtles(sat_id,crudo,tca):
    """
     Tanto para el Satelite como para el Desecho:
    
    * Importar Set de TLEs (importar_tle)
    * Implementar OSW con TLEs ---> extrar matriz.
    * 
    
    """
    files=glob.glob('../TleAdmin/tle/*')
    for filename in files:
        os.unlink(filename)
   
    
    divide_setTLE(sat_id, crudo)
    tles=glob.glob('../TleAdmin/tle/*')
    dic_tles=generadorDatos(tles)
    tle_ordenados=ordenaTles(dic_tles)
    
    
    tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[-1][0])
    r0,rp=tle_primario.propagaTLE(tca) # En TEME
    r0=np.array([r0[0],r0[1],r0[2]])
        
    nombre='difRSW_'+str(sat_id)+'_'+tca.strftime('%Y%m%d')+'.TLE'
    archivo_dif_rsw=open('../AjustarTLE/diferencias/'+nombre+'','w')
    # listas de diferencias (RSW)
    dr=[]
    ds=[]
    dw=[]
    drr=[]
    dss=[]
    dww=[]

    item=range(len(tle_ordenados)-2,-1,-1)       
    for j in item:
        tle1=Tle.creadoxArchivo('../TleAdmin/tle/'+tle_ordenados[j][0])
        fsec=tle1.epoca()
        pos,vel=tle1.propagaTLE(tca)
        pos=np.array([pos[0],pos[1],pos[2]])
        vel=np.array([vel[0],vel[1],vel[2]]) 
        # Calculo de Diferencias
        d_r=pos-r0
        d_v=vel-rp
        r,s,w=ricSis(r0, rp, d_r)
        rr,ss,ww=ricSis(r0,rp,d_v)
        '''
        Sistema RSW
        '''
        dr.append(r)
        ds.append(s)
        dw.append(w)
        drr.append(rr)
        dss.append(ss)
        dww.append(ww)
        
        infodifRST=fsec.strftime('%Y%m%d')+' '+str(r)+' '+str(s)+' '+str(w)+' '+str(rr)+' '+str(ss)+' '+str(ww)+'\n'
        archivo_dif_rsw.write(infodifRST)
    
    var_r=np.var(dr)
    var_s=np.var(ds)
    var_w=np.var(dw)
    
    return var_r,var_s,var_w

if __name__ == '__main__':
    
    """
    Codigo principal.
    Inicia el ciclo de procesamiento. 
    -----------------------------------------------------------
    inputs
        sat_id: id NORAD del Satelite (string)
        deb_id: id NORAD del Desecho (String)
        tca: tiempo de maximo acercamiento (datetime)
    """
    
    
    # Se crean los directorios necesarios.
   
    d1='../TleAdmin/tle'
    if not os.path.exists(d1):
        os.mkdir(d1)
    d2='../AjustarTLE/diferencias'
    if not os.path.exists(d2):
        os.mkdir(d2)
    d3='../main/matrices/'
    if not os.path.exists(d3):
        os.mkdir(d3)
    d4='../visual/archivos/TLE'
    if not os.path.exists(d4):
        os.mkdir(d4)
    d5='../visual/archivos/CODS'
    if not os.path.exists(d5):
        os.mkdir(d5)    
        

    
    # Genera las diferencias en R,S,W (idem R,T,N)

#     TCA=datetime(2008,1,9,19,1,30,0)
#     sat_id='27386' #ENVISAT
#     deb_id='15482' #COSMOS
# -------------------------------------------
#   Escenario 2
# -------------------------------------------
#     TCA=datetime(2004,6,5,10,44,39,0)
#     sat_id='27386' # ENVISAT
#     deb_id='21798'  # AKM
# -------------------------------------------
#   Escenario 3
# -------------------------------------------
#     TCA=datetime(2004,6,9,17,46,29,0)
#     sat_id='27386' # ENVISAT
#     deb_id='5395'  # AKM
# -------------------------------------------
#   Escenario 4
# -------------------------------------------
    TCA=datetime(2004,9,2,19,14,11,0)
    sat_id='27386' #ENVISAT
    deb_id='12442' #COSMOS
# -------------------------------------------
#   Escenario 5
# -------------------------------------------
#     TCA=datetime(2004,9,29,23,56,3,0)
#     sat_id='23560' # ERS-2
#     deb_id='16681'  # COSMOS 1741
# -------------------------------------------
#   Escenario ALSAT I - (No hay datos para el debris)
# -------------------------------------------
#     TCA=datetime(2012,4,29,9,47,28,755)
#     sat_id='36798' # ALSAT
#     deb_id='37976'  # COSMOS 2251
# -------------------------------------------
#   Escenario SAC D - 20 DE JUNIO SOCRATES
# -------------------------------------------
#     TCA=datetime(2017,6,20,15,59,18,9)
#     sat_id='37673' # SAC-D
#     deb_id='14493'  # DELTA 1 DEB
# -------------------------------------------
#   Escenario TerraSAR - PEGASUS DEBRIS
# -------------------------------------------
    TCA=datetime(2010,8,7,13,19,35,0)
    sat_id='31698' # TerraSAR
    deb_id='24978'  # PEGASUS DEBRIS

    r_sat,v_sat,r_deb,v_deb,vec_rsw=proc_encuentroSimple(sat_id,deb_id,TCA)
    
    r_comp=vec_rsw[0]
    s_comp=vec_rsw[1]
    w_comp=vec_rsw[2]
    
    mu_x=r_comp
    mu_y=np.sqrt(s_comp*s_comp+w_comp*w_comp)
    
    #Calculo el angulo entre los vectores velocidad.
    cos_phi=np.dot(v_sat,v_deb)/(np.sqrt(np.dot(v_sat,v_sat))*np.sqrt(np.dot(v_deb,v_deb)))
    phi=np.arccos(cos_phi)
    
    # Genera las varianzas en R,S,W para ambos.
    # Metodo OSW. 
    
    # !!! HARDCODEO ARCHIVO CRUDO!!!
    
    # Ma. satelite.
#    crudo_sat='37673_20170605_20170621.tle'
#    crudo_sat='27386_20040523_20040607.tle'
#    crudo_sat='27386_20040526_20040610.tle' # Escenario 3
#    crudo_sat='27386_20071226_20080109.tle' #ENVI
#    crudo_sat='27386_20040819_20040903.tle' # Escenario 4
#    crudo_sat='23560_20040915_20040930.tle' # Escenario 5
#    crudo_sat='36798_20120415_20120430.tle' #Escenario ALSAT I
    crudo_sat='31698_20100725_20100808.tle' # TerraSAR
    
    var_rsat,var_ssat,var_wsat=metodoOSWtles(sat_id,crudo_sat,TCA)
    
    # Ma. Debris
#    crudo_deb= '14493_20170605_20170621.tle'
#    crudo_deb='21798_20040523_20040607.tle'
#    crudo_deb='5395_20040526_20040610.tle' # Escenario 3
#    crudo_deb='15482_20071226_20080109.tle' #COSMOS 
#    crudo_deb='12442_20040819_20040903.tle'  # Escenario 4
#    crudo_deb='16681_20040915_20040930.tle' #Escenario 5
#    crudo_deb='37976_20120415_20120430.tle' #Escenario ALSAT I
    crudo_deb='24978_20100725_20100808.tle' # Pegasus DEB.

    var_rdeb,var_sdeb,var_wdeb=metodoOSWtles(deb_id,crudo_deb,TCA)

    #Calculo los errores combinados proyectados.
    
    var_s=var_ssat+var_sdeb
    var_w=var_wsat+var_wdeb
    
    var_x=var_rsat+var_rdeb 
    var_y=var_s*np.cos(phi/2.0)*np.cos(phi/2.0)+var_w*np.sin(phi/2.0)*np.sin(phi/2.0)

    ra=0.005
    
#    PoC=np.exp((-1.0/2.0)*((mu_x*mu_x/var_x)+(mu_y*mu_y/var_y)))*(1-np.exp(-ra/(2*np.sqrt(var_x)*np.sqrt(var_y))))
    PoC=dblquad(lambda y, x: (1.0/(2.0*np.pi*np.sqrt(var_x)*np.sqrt(var_y)))*np.exp((-1.0/2.0)*((x*x/var_x)+(y*y/var_y))), mu_x-ra, mu_x+ra, lambda y: -np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y, lambda y: np.sqrt(ra*ra-(y-mu_x)*(y-mu_x))+mu_y)
    print '======================================'
    print 'PoC = ', PoC[0]
    print '======================================'