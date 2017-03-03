'''
Created on 14/02/2017

@author: mcvalenti
'''
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import matplotlib.dates as mdates
import datetime as dt
from Comparar.TleVsCods import generaTEME
from Comparar.TleVsCods import EjecutaComparacion
from Estadistica.maCovar import EjecutaMaCovarCODS
from visual.TlevsCodsGraf import VerGraficoMision
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt


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
        self.grid.setSpacing(20)
             
        self.sat_nombre=''
        self.dic_satelites={}
        self.sat_id='9999'       
        self.st=''
        self.et=''
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
        self.sat_nom_edit   = QLineEdit()
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
        self.listaSat.addItem("ICESAT");

        
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
        self.grid.addWidget(self.sat_nom_edit,4,0)
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

        self.listaSat.currentIndexChanged.connect(self.selectionchange)
        
        self.boton_salir.clicked.connect(self.salir)
        self.boton_cargar_tle.clicked.connect(self.ArchivoTle)
        self.boton_cargar_cods.clicked.connect(self.ArchivoCODS)
        self.boton_diferencias.clicked.connect(self.ProcDif)
        self.boton_ma_covar.clicked.connect(self.Macovar)
        #self.boton_grafico.clicked.connect(self.verGrafico)
        self.boton_grafico.clicked.connect(self.plotear)
        
    
    def selectionchange(self,i):
        self.sat_nombre= self.listaSat.currentText()
        self.sat_nom_edit.setText(self.sat_nombre)
        self.dic_satelites={'SAC-D':37673,'LAGEOS':8820,'ICESAT':27642}
        self.sat_id=self.dic_satelites[str(self.sat_nombre)]

    
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
        
    def plotear(self):
        fig=Figura()
        fig.exec_()
        
    def verGrafico(self):
        VerGraficoMision()
        
        
    def salir(self):
        self.close()
    
    
class Figura(QDialog):
    def __init__(self, parent=None):
        super(Figura, self).__init__(parent)
        
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QPushButton('Plot')
        self.boton_cerrar=QPushButton('Cerrar')
        self.button.clicked.connect(self.plot)
        self.boton_cerrar.clicked.connect(self.salir)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.boton_cerrar)
        self.setLayout(layout)  

     
    def plot(self):
        f=open('../main/codsOsweiler.dif','r')
        listas=f.readlines()
    
        data0=[]
        data1=[]
        data2=[]
        data3=[]
        
        for l in listas:
            linea=l.split(' ')
            data0.append(linea[0])
            data1.append(float(linea[2]))
            data2.append(float(linea[3]))
            data3.append(float(linea[4]))

        """
        Gestion de Fechas
        """
        date_fmt = '%Y-%m-%d'
        epoca=[dt.datetime.strptime(str(i), date_fmt) for i in data0]
        x = [mdates.date2num(i) for i in epoca]
        date_formatter = mdates.DateFormatter('%d-%m-%y')
    
        # create an axis
        ax1 = self.figure.add_subplot(311) 
        ax2 = self.figure.add_subplot(312) 
        ax3 = self.figure.add_subplot(313) 
        ax1.xaxis.set_major_formatter(date_formatter)
        ax2.xaxis.set_major_formatter(date_formatter)
        ax3.xaxis.set_major_formatter(date_formatter)
        ax1.grid(True)
        ax2.grid(True)
        ax3.grid(True)
        
        # discards the old graph
        #ax.hold(False)
        
        # plot data
        ax1.plot_date(x, data1,'x')
        ax2.plot_date(x, data2,'x')
        ax3.plot_date(x, data3,'x')

        # refresh canvas
        self.canvas.draw() 
        
    def salir(self):
        self.close()
    
if __name__=='__main__':
    #IniciaApp():
    QApplication.setStyle("plastique")
    app = QApplication(sys.argv)
    ex = ProcCODS()
    sys.exit(app.exec_())