'''
Created on 14 jul. 2018
@author: ceci
'''
import csv
from datetime import datetime, timedelta
from TleAdmin.TLE import Tle
from Encuentro.Encuentro import Encuentro


hr=0.009 # radio combinado [km]
filename='valAkella.csv'
with open(filename, 'w') as csvfile:
    fieldnames = ['Event ID', 'data Miss Dist.', 'computed Miss Dist.',
                  'data poc','computed poc','sigma2_1','sigma2_2','sigma2_3' ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    with open('tabladatos.csv') as File:  
        reader = csv.reader(File)
        cdm_list=list(reader)
        for row in cdm_list[4:6]:
            obj1_id=row[0]
            obj2_id=row[1]
            tca=datetime.strptime(row[2], '%d/%m/%Y %H:%M:%S')
            miss_distance=row[3]
            poc=row[4]
            
            # Instanciacion de los TLE
            tle_sat=Tle.creadoxParam(obj1_id, tca)
            tle_deb=Tle.creadoxParam(obj2_id, tca)
            
            # Corroborar que el TLE es anterior en fecha y hora al tca
            if tle_sat.epoca() >= tca:
                tca_sust=tca-timedelta(days=1)
                tle_sat=Tle.creadoxParam(obj1_id,tca_sust)
                
            if tle_deb.epoca() >= tca:
                tca_sust=tca-timedelta(days=1)
                tle_deb=Tle.creadoxParam(obj2_id,tca_sust)
                
            encuentro1=Encuentro(tle_sat,tle_deb,tca,hr)
            
            # Procesamiento Lei-Chen
            #poc_lei=encuentro1.calculaPoC_circ()
            poc_ak=encuentro1.calculaPoC_akella()
            tca_string=row[2].split()[0]
            event_id=str(obj1_id)+'_'+str(obj2_id)+'_'+tca_string
            ma_sat_RTN_tca=encuentro1.ma_sat_eci #encuentro1.ma_sat_RTN_tca
            ma_deb_RTN_tca=encuentro1.ma_deb_eci #encuentro1.ma_deb_RTN_tca
            sigma2_1=ma_sat_RTN_tca[0][0]+ma_deb_RTN_tca[0][0]
            sigma2_2=ma_sat_RTN_tca[1][1]+ma_deb_RTN_tca[1][1]
            sigma2_3=ma_sat_RTN_tca[2][2]+ma_deb_RTN_tca[2][2]
            writer.writerow({'Event ID':event_id, 'data Miss Dist.':row[3], 'computed Miss Dist.':encuentro1.mod_minDist,
                             'data poc':row[4],'computed poc':poc_ak,
                             'sigma2_1':sigma2_1,'sigma2_2':sigma2_2,'sigma2_3':sigma2_3})
