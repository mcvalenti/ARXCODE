'''
Created on 14/02/2017

@author: mcvalenti
'''
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Comparar.TleVsCods import generaTEME

class ProcCODS(QWidget):
    
    def __init__(self):
        super(ProcCODS, self).__init__()
        self.resize(600, 600)
        self.setWindowTitle('PROCESAMIENTO de DATOS CODS')
       
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.white)
        self.setPalette(self.palette)
        
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        
        self.archivoTLE='' 
    
        """
        Etiquetas
        """
        self.carga_datos     = QLabel('CARGAR LOS ARCHIVOS')
        self.TLE_label       = QLabel('Datos Crudos TLE')
        self.CODS_label      = QLabel('Datos Crudos CODS')
        """
        Campos de Edicion
        """
        self.TLE_edit       = QLineEdit()
        self.CODS_edit      = QLineEdit()
        """
        Botones
        """
        self.boton_tle_cargado  = QPushButton('CARGADO')
        self.boton_cods_cargado = QPushButton('CARGADO')
        self.boton_salir        = QPushButton('Salir')
                
        """
        GRILLA
        """
        self.grid.addWidget(self.TLE_label,1,0)
        self.grid.addWidget(self.TLE_edit,1,1)
        self.grid.addWidget(self.boton_tle_cargado,1,2)
        self.grid.addWidget(self.CODS_label,2,0)
        self.grid.addWidget(self.CODS_edit,2,1)
        self.grid.addWidget(self.boton_cods_cargado,2,2)
        self.grid.addWidget(self.boton_salir,5,2)
        self.setLayout(self.grid)
        self.show()
        
        """
        Acciones
        """
        self.boton_salir.clicked.connect(self.salir)
        self.boton_tle_cargado.clicked.connect(self.TLEteme)
        
    def TLE2sv(self):
        pass
#         tles = glob.glob('../TleAdmin/tle/*')
#         generaTEME(tles)
        
    def TLEteme(self):
        self.archivoTLE=self.TLE_edit.text()
        
    def salir(self):
        self.close()
    
if __name__=='__main__':
    #IniciaApp():
    QApplication.setStyle("plastique")
    app = QApplication(sys.argv)
    ex = ProcCODS()
    sys.exit(app.exec_())