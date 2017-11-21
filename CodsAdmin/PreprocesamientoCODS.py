'''
Created on 16/03/2017

@author: mcvalenti
'''
import os, glob, gzip
import csv
import numpy as np
    

    
def unpack_gzFiles(dir): 
    """
    Unpacks all .gz files from dir.
    Saves them all at dir also
    """   
    lista_gz=glob.glob(dir+'/*.gz')
    print 'Total de Archivos gz = ', len(lista_gz) 
    
    for l in lista_gz:
        archivo=l.split('/')[-1]
        nombre=archivo.split('.')[0]
        f = gzip.open(l, 'r')
        content=f.read()
        salida_f=open(dir+'/'+nombre+'.'+'TXT','w')
        salida_f.write(content)
#     m=0
# #    print lista_gz[767]
#     for l in lista_gz:
#         print m
#         if m != 766:          
#             archivo=l.split('/')[-1]
#             nombre=archivo.split('.')[0]
#             f = gzip.open(l, 'r')
#             content=f.read()
#             salida_f=open('../CodsAdmin/TOD_O/'+nombre+'.'+'TXT','w')
#             salida_f.write(content)
#         m= m+1
# 
#     ### PREPROCESAMIENTO PARA FILTRAR LOS ARCHIVOS .D
#     lista_completa=glob.glob('../CodsAdmin/DatoMision/*')
#     for lt in lista_completa:
#         m=0
#         txt=0
#         archivo=lt.split('/')[-1]
#         nombre=archivo.split('.')[0]
#         tipo=nombre.split('_')[-1]
#         ext=archivo.split('.')[-1]
#         if ext == 'gz' and tipo == 'O':
#             m=m+1
#             lista_datos=glob.glob('../CodsAdmin/DatoMision/*.gz')
# #             for l in lista_datos:
# #                 f = gzip.open(l, 'r')
# #                 content=f.read()
# #                 salida_f=open('../CodsAdmin/DatoMision/'+nombre+'.'+'TXT','w')
# #                 salida_f.write(content)
# #                 f.close()
#         else:
#             os.remove(lt)
#             txt=txt+1
 
# 
#     print 'Total de ARchivos = ', len(lista_completa)

#     archivos=glob.glob('../CodsAdmin/TOD_O/*TXT')
#     largo = []
#     fila = []
#     linea_archivo = []
#     for arch in archivos:
#         a = open(arch, 'r')
#         nombre=arch.split('/')[-1]
#         fecha_nombre=nombre.split('_')[1]
#         anio=fecha_nombre[0:4]
#         mes=fecha_nombre[4:6]
#         dia=fecha_nombre[6:8]
#         fecha_str=anio+'/'+mes+'/'+dia
#         a_content= a.readlines()
#         largo.append(len(a_content))
#         linea_ini=a_content[1]
#         fecha_ini=linea_ini[:19]
#         linea_fin=a_content[-1]
#         fecha_fin=linea_fin[:19]
#         datos=[nombre,fecha_str,fecha_ini,fecha_fin,len(a_content)]
#         fila.append(datos)
#     with open('../CodsAdmin/registro_archivos.csv', "w") as f:
#         writer = csv.writer(f)
#         writer.writerows(fila)
# 
#     
#     print 'Cantidad TOTAL de archivos = ', len(archivos)
#     print 'Largo medio de los archivos = ', np.mean(largo)
#     print 'Archivo mayor, tamanio = ', np.max(largo)
#     print 'Archivo menor, tamanio = ', np.min(largo)
#     print 'FIN'

if __name__=="__main__":
    
    dir='../CodsAdmin/CUSS_CODS/DENSEPHEM_2012'
    unpack_gzFiles(dir)
    print 'FIN'