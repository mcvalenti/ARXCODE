"""
Calculo del dia juliano (J2000)
epoca juliana (J2000): 1ero de Enero de J2000 al mediodia.
jd(j2000)=2451545.0
"""
import numpy as np
from datetime import datetime

def j0(epoch):
    """
    Calcula la fecha juliana para 0hs de UT.
    ---------------------------------------------
    input
        epoch: fecha (datetime)
    output
        j0: fecha juliana a Ohs de UT (float)
    """
    y=epoch.year
    m=epoch.month
    d=epoch.day
    term1=7*(y+(m+9)/12)/4
    term2=275*m/9
    j0=367*y-term1+term2+d+1721013.5
    
    return j0
    
def jd(epoch):
    """
    Calcula la fecha juliana para la epoca.
    Utiliza la funcion anterior J0
    ---------------------------------------------
    input
        epoch: fecha (datetime)
    output
        jd: fecha juliana de la epoca (float)
    """
    h=epoch.hour
    minu=epoch.minute
    s=epoch.second+epoch.microsecond/1000000.0    
    j01=j0(epoch)
    ut=h+minu/60.0+s/3600.0
    jd=j01+ut/24.0
    
    return jd

def calcula_mjd(epoch):
    jd1=jd(epoch)
    mjd=jd1-240000.5   
    return mjd
    
def ts_greenwich(epoch):
    """
    -------------------------------------------------
    Calcula el Tiempo Sidereo en Greenwichj,
    para una fecha y hora. 
    -------------------------------------------------
    inputs
        epoca: fecha y hora - (datetime)
    outputs
        thetaG_xhs: Tiempo Sidereo para la epoca - (float)-[grados]
    """
    h1=epoch.hour
    minu1=epoch.minute
    s1=epoch.second+epoch.microsecond/1000000.0
    ut1=h1+minu1/60.0+s1/3600.0
    """
    Se calcula T0 [centurias julianas]
    """
    j02=j0(epoch)
    dt=(j02-2451545.0)/36525.0 
    """
    Tiempo sidereo en Greenwich a 0hs UT.
    """
    a=100.4606184
    b=36000.77004
    c=0.000387933
    d=-2.583*10**(-8)   
    thetaG_0hs=a+b*dt+c*dt*dt+d*dt**3 # [grados]
    if thetaG_0hs > 360.0:
       vueltas=np.modf(thetaG_0hs/360.0)[1]
       thetaG_0hs=thetaG_0hs-vueltas*360
    """
    Tiempo sidereo en Greenwich a una hora particular
    """
    thetaG_xhs=thetaG_0hs+360.98564724*(ut1/24.0)

    if thetaG_xhs > 360.0:
        vueltasx=np.modf(thetaG_xhs/360.0)[1]
        thetaG_xhs=thetaG_xhs-vueltasx*360
    
    return thetaG_xhs
    
    
def ts_local(epoch,lon):
    h1=epoch.hour
    minu1=epoch.minute
    s1=epoch.second+epoch.microsecond/1000000.0
    ut1=h1+minu1/60.0+s1/3600.0
    """
    Se calcula T0 [centurias julianas]
    """
    j02=j0(epoch)
    dt=(j02-2451545.0)/36525.0 
    """
    Tiempo sidereo en Greenwich a 0hs UT.
    """
    a=100.4606184
    b=36000.77004
    c=0.000387933
    d=-2.583*10**(-8)   
    thetaG_0hs=a+b*dt+c*dt*dt+d*dt**3 # [grados]
    if thetaG_0hs > 360.0:
       vueltas=np.modf(thetaG_0hs/360.0)[1]
       thetaG_0hs=thetaG_0hs-vueltas*360
    """
    Tiempo sidereo en Greenwich a una hora particular
    """
    thetaG_xhs=thetaG_0hs+360.98564724*(ut1/24.0)

    if thetaG_xhs > 360.0:
        vueltasx=np.modf(thetaG_xhs/360.0)[1]
        thetaG_xhs=thetaG_xhs-vueltasx*360
    
    if lon > 0.0:
        ts=thetaG_xhs+lon
    else:
        ts=thetaG_xhs-lon
    if ts > 360.0:
        vueltass=np.modf(ts/360.0)[1]
        ts=ts-vueltass*360
    return ts  
    