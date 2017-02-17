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
        self.grid.setSpacing(15)
        
        self.et=''
        self.st=''
        self.archivoTLE='' 
    
        """
        Etiquetas
        """
        self.escenario       = QLabel('Escenario de Analisis')
        self.satelite        = QLabel('Seleccione la MISION')
        self.fi              = QLabel('Desde')
        self.ff              = QLabel('Hasta')
        self.verif_sol       = QLabel('Verificacion de la Solicitud')
        self.carga_datos     = QLabel('CARGAR LOS ARCHIVOS')
        self.TLE_label       = QLabel('Datos Crudos TLE')
        self.CODS_label      = QLabel('Datos Crudos CODS')
#         self.TLE_comp        = QLabel('TLEs para la Comparacion')
        self.CODS_comp       = QLabel('CODS para la Comparacion')
        """
        Campos de Edicion
        """
        self.TLE_edit       = QLineEdit()
        self.CODS_edit      = QLineEdit()
        self.TLE_comp_edit  = QLineEdit()
        self.CODS_comp_edit = QLineEdit()
        
        """
        Lista desplegada
        """
        self.listaSat       = QComboBox()
        self.listaSat.addItem("...");
        self.listaSat.addItem("SAC-D"); 
        self.listaSat.addItem("LAGEOS");

        
        """
        CALENDARIOS
        """
        self.cal = QCalendarWidget()
        self.cal.setGridVisible(True)
        self.cal.clicked[QDate].connect(self.verFinicio)
        self.cal1 = QCalendarWidget()
        self.cal1.setGridVisible(True)
        self.cal1.clicked[QDate].connect(self.verFfin)
                
        """
        Botones
        """
        self.boton_solCODS      = QPushButton('Solicitud a CODS')
        self.boton_solNORAD     = QPushButton('Solicitud a NORAD')
        self.boton_tle_cargado  = QPushButton('Preprocesamiento TLE')
        self.boton_cods_cargado = QPushButton('Preprocesamiento CODS')
        self.boton_cargar_tle   = QPushButton('TLEs para la Comparacion')
        self.boton_salir        = QPushButton('Salir')
                
        """
        GRILLA
        """
        self.grid.addWidget(self.escenario,1,0)
        self.grid.addWidget(self.satelite,2,0)
        self.grid.addWidget(self.fi,2,1)
        self.grid.addWidget(self.ff,2,2)
        self.grid.addWidget(self.listaSat,3,0)
        self.grid.addWidget(self.cal,3,1)
        self.grid.addWidget(self.cal1,3,2)
        self.grid.addWidget(self.boton_solCODS,4,1)
        self.grid.addWidget(self.boton_solNORAD,4,2)       
        self.grid.addWidget(self.TLE_label,5,0)
        self.grid.addWidget(self.TLE_edit,5,1)
        self.grid.addWidget(self.boton_tle_cargado,5,2)
        self.grid.addWidget(self.boton_cargar_tle,6,1)
        self.grid.addWidget(self.TLE_comp_edit,6,2)
        self.grid.addWidget(self.CODS_label,8,0)
        self.grid.addWidget(self.CODS_edit,8,1)
        self.grid.addWidget(self.boton_cods_cargado,8,2)
        self.grid.addWidget(self.CODS_comp,9,0)
        self.grid.addWidget(self.CODS_comp_edit,9,1)
        self.grid.addWidget(self.boton_salir,10,2)
        self.setLayout(self.grid)
        self.show()
        
        """
        Acciones
        """
        self.boton_salir.clicked.connect(self.salir)
        self.boton_tle_cargado.clicked.connect(self.TLEteme)
        self.boton_cargar_tle.clicked.connect(self.ArchivoTle)
    
    def verFinicio(self):
        self.st = self.cal.selectedDate()

    def verFfin(self):
        self.et = self.cal1.selectedDate()  
        
    def ArchivoTle(self):    
        print 'estoy aca'
        fname=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../TleAdmin/crudosTLE/*")
        nombre=str(fname).split('/')[-1]
        self.archivoTLE = nombre
        self.TLE_comp_edit.setText(self.archivoTLE)
        
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