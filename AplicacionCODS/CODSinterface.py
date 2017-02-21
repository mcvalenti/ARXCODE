'''
Created on 14/02/2017

@author: mcvalenti
'''
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Comparar.TleVsCods import generaTEME
from Comparar.TleVsCods import EjecutaComparacion
from Estadistica.maCovar import EjecutaMaCovarCODS
from visual.TlevsCodsGraf import VerGrafico
class ProcCODS(QWidget):
    
    def __init__(self):
        super(ProcCODS, self).__init__()
        self.resize(300, 300)
        self.setWindowTitle('PROCESAMIENTO de DATOS CODS')
       
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.white)
        self.setPalette(self.palette)
        
        self.Hlinea = QFrame()
        self.Hlinea.setFrameStyle(QFrame.HLine)
        self.Hlinea.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.grid   = QGridLayout()
        self.grid.setSpacing(5)
             
        
        self.sat_id='37673'
        self.et=''
        self.st=''
        self.archivoTLE='' 
        self.archivoCODS=''
        self.diferencias=''
        self.macovarT=''
    
        """
        Etiquetas
        """
        self.escenario       = QLabel('Escenario de Analisis')
        self.satelite        = QLabel('Seleccione la MISION')
        self.fi              = QLabel('Desde')
        self.ff              = QLabel('Hasta')
        self.verif_sol       = QLabel('Verificacion de la Solicitud')
        self.carga_datos     = QLabel('CARGAR LOS ARCHIVOS')
#         self.TLE_comp        = QLabel('TLEs para la Comparacion')
        self.CODS_comp       = QLabel('CODS para la Comparacion')
        """
        Campos de Edicion
        """
        self.st_edit        = QLineEdit()
        self.et_edit        = QLineEdit()
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
        self.boton_cods_cargado = QPushButton('Preprocesamiento CODS')
        self.boton_cargar_tle   = QPushButton('TLEs para la Comparacion')
        self.boton_cargar_cods  = QPushButton('CODS para la Comparacion')
        self.boton_diferencias  = QPushButton('Procesar DIFERENCIAS')
        self.boton_ma_covar     = QPushButton('Calcular Matriz de Covarianza')
        self.boton_grafico      = QPushButton('Graficar')
        self.boton_salir        = QPushButton('Salir')
        """
        OTROS
        """
        self.tableView       = QTableWidget()
             
        """
        GRILLA
        """
        self.grid.addWidget(self.escenario,1,0)
        self.grid.addWidget(self.satelite,2,0)
        self.grid.addWidget(self.fi,2,1)
        self.grid.addWidget(self.ff,2,2)
        self.grid.addWidget(self.listaSat,3,0)
        self.grid.addWidget(self.cal,3,1)
        self.grid.addWidget(self.st_edit,4,1)
        self.grid.addWidget(self.cal1,3,2)
        self.grid.addWidget(self.et_edit,4,2)
        
        self.grid.addWidget(self.Hlinea,6,0,1,4)
        self.grid.addWidget(self.boton_solCODS,7,1)
        self.grid.addWidget(self.CODS_edit,7,2)
        self.grid.addWidget(self.boton_solNORAD,8,1)  
        self.grid.addWidget(self.TLE_edit,8,2)
        self.grid.addWidget(self.boton_cods_cargado,8,3)
        self.grid.addWidget(self.Hlinea,9,0,1,4)           
        self.grid.addWidget(self.boton_cargar_tle,10,1)
        self.grid.addWidget(self.TLE_comp_edit,10,2)        
        self.grid.addWidget(self.boton_cargar_cods,11,1)
        self.grid.addWidget(self.CODS_comp_edit,11,2)
        self.grid.addWidget(self.boton_diferencias,11,3)
        self.grid.addWidget(self.boton_ma_covar,15,3)
        self.grid.addWidget(self.boton_grafico,16,3)
        self.grid.addWidget(self.tableView,14,1,8,2)
        self.grid.addWidget(self.boton_salir,26,3)
        self.setLayout(self.grid)
        self.show()
        
        """
        Acciones
        """
        self.boton_salir.clicked.connect(self.salir)
        self.boton_cargar_tle.clicked.connect(self.ArchivoTle)
        self.boton_cargar_cods.clicked.connect(self.ArchivoCODS)
        self.boton_diferencias.clicked.connect(self.ProcDif)
        self.boton_ma_covar.clicked.connect(self.Macovar)
        self.boton_grafico.clicked.connect(self.verGrafico)
    
    def verFinicio(self):
        self.st = self.cal.selectedDate()
        self.st.setText(self.date.toString())

    def verFfin(self):
        self.et = self.cal1.selectedDate()  
        self.et.setText(self.date1.toString())
        
    def ArchivoTle(self):    
        fname=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../TleAdmin/crudosTLE/*")
        nombre=str(fname).split('/')[-1]
        self.archivoTLE = nombre
        print 'El archivo TLE es: ',self.archivoTLE
        self.TLE_comp_edit.setText(self.archivoTLE)
        
    def ArchivoCODS(self):  
        fname1=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../CodsAdmin/TOD_O/*")
        nombre1=str(fname1).split('/')[-1]
        self.archivoCODS = nombre1
        print 'El archivo CODS es: ', self.archivoCODS
        self.CODS_comp_edit.setText(self.archivoCODS)
        
    def ProcDif(self):
        self.diferencias=EjecutaComparacion(self.sat_id, self.archivoTLE, self.archivoCODS)
        
    def Macovar(self):
        self.macovarT=EjecutaMaCovarCODS(self.diferencias)
        self.tableView.setRowCount(len(self.macovarT))
        self.tableView.setColumnCount(len(self.macovarT))
        for i,fila in enumerate(self.macovarT):
            for j,col in enumerate(fila):
                self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
        
    def verGrafico(self):
        VerGrafico()
        
    def salir(self):
        self.close()
    
if __name__=='__main__':
    #IniciaApp():
    QApplication.setStyle("plastique")
    app = QApplication(sys.argv)
    ex = ProcCODS()
    sys.exit(app.exec_())