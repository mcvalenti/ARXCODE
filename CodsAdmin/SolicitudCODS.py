'''
Created on 13/03/2017
"""
indentificar el nombre del archivo deseado a partir de la fecha.
conexion al servidor CODS y descarga del dato .gz
Descompresion del archivo .gz
generacion del crudo total para los pasos siguientes.
"""
@author: mcvalenti
'''
import gzip, re
import os, sys, glob
from datetime import datetime
#import pysftp

directorio = '../CodsAdmin/DatoMision/'

if not os.listdir(directorio):
    sys.exit(directorio+' '+'No contiene archivos')
else:
    lista=glob.glob(directorio+'*')
    nombreArchivo=lista[0].split('_')
    fechaArchivo=nombreArchivo[1]
    year=int(fechaArchivo[:4])
    mes=int(fechaArchivo[4:6])
    dia=int(fechaArchivo[6:8])
    fechaArchivo1=datetime(year,mes,dia)
    
   
# f = gzip.open('../CodsAdmin/DatoMision/CODS_20131025_181316_SACD_ORBEPHEM_TOD_XYZ_D.TXT.gz', 'rb')
# file_content = f.readlines()
# for linea in file_content:
#     encontra_header=re.search(r'*HEADER', linea)
# 
# f.close()

#path = './CodsAdmin/DatoMision/'#hard-coded
# localpath = sys.argv[1]
 
#host = "cods.conae.gov.ar"                    #hard-coded
# password = "mcvalenti"                #hard-coded
# username = "9Fd3-&(N"                #hard-coded
# 
# with pysftp.Connection(host, username=username, password=password) as sftp:
#     sftp.isdir('ORBEPHEM_TOD_XYZ')
#     sftp.get_d('ORBEPHEM_TOD_XYZ', path, preserve_mtime=True)

print 'Upload done.'