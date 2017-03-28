'''
Created on 27/03/2017

@author: mcvalenti
'''

import matplotlib.pyplot as plt
import numpy as np

def desviacion_standard_graf(sat_id,x,y,z):
    """
    Toma los valores de los bins para cada coordenada V,N,C.
    Grafica una sola figura con los tres ploteos de Bin vs Coordenada.
    ------------------------------------------------------------------
    input
        sat_id: NORAD ID del objeto (String)
        x,y,z: valores (Vectores)
    output
        sat_id_bin.pnt: nombre del archivo del grafico generado en
                        (visual/archivos)
    """   
    
    t=np.linspace(0, len(x), len(x))
    lx=len(x)
    ly=len(y)
    lz=len(z)
    
    # Two subplots, unpack the axes array immediately
    fig = plt.figure()
    plt.suptitle('Desviaciones Standard')
    ax1 = fig.add_subplot(311)
    ax1.grid()
    ax1.set_ylabel('Km')    
    ax2 = fig.add_subplot(312)
    ax2.grid()
    ax2.set_ylabel('Km')
    ax3 = fig.add_subplot(313)
    ax3.grid()
    ax3.set_ylabel('Km')
    ax3.set_xlabel('BIN')
    
    ax1.plot(t,x,label='Coord V')
    ax2.plot(t,y,label='Coord N')
    ax3.plot(t,z,label='Coord C')
    legend = ax1.legend(loc='upper center', shadow=True)
    legend = ax2.legend(loc='upper center', shadow=True)
    legend = ax3.legend(loc='upper center', shadow=True)
    
    plt.savefig('../visual/archivos/'+sat_id+'_bin.png')
    
def histograma_bin(cantidad):
    """
    Realiza un grafico de barras con la cantidad de
    registros por intervalo temporal
    ------------------------------------------------
    input
        cantidad: numero de registros (Vector)
    """
    N = len(cantidad)
    x = range(N)
    width = 1/2.5
    plt.bar(x, cantidad, width, color="blue")
#    plt.show()
    
# if __name__=='__main__':

    """
    grafico de barras
    """
#     cantidad = [3,17,15,16,15,13,11,10,9,8,6,5,4,3]
#     histograma_bin(cantidad)
#     
    """
    grafico de bins
    """
#     sat_id=str(8820)
#     x=[0.15531948383281455, 0.35208799139462987, 0.48735055684593348, 0.53655846595379852, 0.50416605421406502, 0.47271063165972399, 0.36993826186181894, 0.31618958882447445, 0.24121794450504946, 0.48202060158683524, 0.646876913769725, 0.41151881448685795, 0.098299360497055691, 0.069155690160713421]
#     y=[0.01261001256989118, 0.053985065818310002, 0.069754938211084944, 0.081556639046680895, 0.076935961292938781, 0.074010283401508489, 0.05387677772665516, 0.059940609952919999, 0.038014182287047255, 0.044055822822065757, 0.051215530306746485, 0.042827868937743832, 0.030871523454211208, 0.0088974321311783931]
#     z=[0.034044496501183651, 0.072488375082016568, 0.10191851628568856, 0.10054505875369606, 0.09733437177247832, 0.10847543102729051, 0.13753228181056895, 0.12950158521380925, 0.11980347298368454, 0.13369423771900754, 0.12911766888769602, 0.10197599440861053, 0.044421303898966986, 0.060285949366608423]
#     desviacion_standard_graf(sat_id,x,y,z)