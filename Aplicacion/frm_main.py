'''
Created on Feb 5, 2017

@author: mcvalenti
'''
import sys, glob, os, re
import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import Tle
from TleAdmin.get_tle import importar_tle
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle, difPrimario, genera_estadisticaBin
from Estadistica.maCovar import EjecutaMaCovar, EjecutaMaCovarCODS
from Comparar.TlevsCodsOSW import ejecutaProcesamientoCods
from visual.ploteos import *
from visual import ploteos
# from visual.TleOsweiler import VerGrafico
# #from visual.TlevsCodsGraf import VerGraficoMision
# from visual.CodsOsweiler import VerGraficoCods
from visual.binGraf import histograma_bin, desviacion_standard_graf
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# import matplotlib.pyplot as plt

class ProcARxCODE(QMainWindow):
    
    def __init__(self):
        super(ProcARxCODE, self).__init__()
        
        extractAction = QAction("Salir", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip('Leave The App')
        extractAction.triggered.connect(self.close_application)
        
        """
        Intento de correr desde el menu
        """
#         tleAction= QWidgetAction('TLE',self)
#         tleAction.setStatusTip('Procesa datos TLE')
#         tleAction.triggered.connect(self.ProcManual)
        self.center()
        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)
                
#        self.resize(900, 600)
        self.setWindowTitle('ARxCODE')
        
        #IMAGEN
#         palette    = QPalette()
#         palette.setBrush(QPalette.Background,QBrush(QPixmap('../visual/imagenes/cords_contol.jpg')))
#         self.setPalette(palette)

        self.dock = QDockWidget("NUEVO CDM")
        self.dock1 = QDockWidget("ENCUENTROS ANTERIORES")
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock1)

        self.centro=self.home()
        self.setCentralWidget(self.centro)
        self.show()
    
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
    
    def close_application(self):
        sys.exit()
    
    class home(QWidget):
        def __init__(self, *args):
            QWidget.__init__(self, *args)
    #     def home(self):
    #         self.centralwi=QWidget()
    #         self.setCentralWidget(self.centralwi)
            self.grid   = QGridLayout()
            """
            Botones
            """
            self.boton_ProManual = QPushButton('Procesamiento de TLE',self)
            self.boton_mision    = QPushButton('Procesamiento de Datos de Mision',self)
#         self.boton_ProManual.move(100,500)
#         self.boton_ProManual.setFixedSize(160,60)
#         self.boton_mision.move(400,500)
#         self.boton_mision.setFixedSize(240,60)
            self.boton_ProManual.clicked.connect(self.tleProc)
            self.boton_mision.clicked.connect(self.misProc)
        
            """
            GRILLA
            """
            self.grid.addWidget(self.boton_ProManual,2,2)
            self.grid.addWidget(self.boton_mision,3,2)
            self.setLayout(self.grid)
#            self.show()
            
        def tleProc(self):
            """
            Despliega la ventana para el procesamiento de los TLE,
            mediante el metodo de Osweiler.
            """
            ventana2=ProcTle()
            ventana2.exec_()
            
        def misProc(self):
            """
            Despliega la ventana para el procesamiento de los datos
            de CODS. 
            """
            ventana3=ProcMision()
            ventana3.exec_()

class ProcTle(QDialog):

    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

#        self.resize(1200, 600)
        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()

        self.filename = ''
        self.sat_id='99999'
        self.fini=''
        self.ffin=''
        self.tles=0
        self.tleOrdenados={}
        self.diferencias=''
        self.grafico_pw=''
        self.arch_macovar=''
        self.macovarT=''  
        self.cantxbin=[]
        self.mediaxbin=[]      
        
    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.white)
        self.setPalette(self.palette)
        
        """
        Grafico
        """
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        """
        Etiquetas
        """
        self.inicio          = QLabel('Inicio del Procedimiento.')
        self.carga           = QLabel('CARGADO DE TLEs')
        self.norad           = QLabel('A partir de NORAD')  
        self.equipo          = QLabel('Desde el Equipo')
        self.arch_prepro     = QLabel('Archivo a Procesar: ')
        self.verificacion    = QLabel('Verificacion de Datos:')
        self.sat_id_label    = QLabel('NORAD_ID')
        self.cant_tles       = QLabel('Cantidad de TLEs')
        self.tle_pri         = QLabel('Ultimo TLE del set.')
        self.outputs         = QLabel('Outputs')
        self.ma_covar_label  = QLabel('Ma. de COVARIANZA')
        """
        Botones
        """
        self.boton_norad     = QPushButton('Space-Track')
        self.boton_equipo    = QPushButton('Directorios')
        self.boton_prepros   = QPushButton('Preprocesamiento')
        self.boton_procesa   = QPushButton('PROCESAR')
        self.boton_grafica   = QPushButton('VER Graficos')
        self.boton_ma_covar  = QPushButton('Calcular Matriz')
        self.boton_salir     = QPushButton('Salir')
        
        
        """
        Campos de Edicion
        """
        self.arch_cargado       = QLineEdit()
        self.sat_id_line        = QLineEdit()
        self.cant_tles_edit     = QLineEdit()
        self.matriz             = QLineEdit()
        self.estado_proc_edit   = QLineEdit()
        self.arch_macovar_edit  = QLineEdit()
        """
        OTROS
        """
        self.tle_pri_edit    = QTextEdit()
        self.tableView       = QTableWidget()
        
        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(self.inicio, 1, 0)
        grid.addWidget(self.carga,2,0)
        grid.addWidget(self.norad,3,0)
        grid.addWidget(self.boton_norad,3,1)
        grid.addWidget(self.equipo,4,0)
        grid.addWidget(self.boton_equipo,4,1)
        grid.addWidget(self.arch_prepro,5,0)
        grid.addWidget(self.arch_cargado,5,1)
        grid.addWidget(self.boton_prepros,5,2)
        grid.addWidget(self.verificacion,6,0)
        grid.addWidget(self.sat_id_label,7,0)
        grid.addWidget(self.cant_tles,7,1)
        grid.addWidget(self.outputs,7,4)
        grid.addWidget(self.sat_id_line,8,0)
        grid.addWidget(self.cant_tles_edit,8,1)
        grid.addWidget(self.boton_procesa,8,2)
        grid.addWidget(self.estado_proc_edit,8,4)
        grid.addWidget(self.tle_pri,9,0)
        grid.addWidget(self.tle_pri_edit,9,1,1,4)
        grid.addWidget(self.boton_grafica,10,4)
        grid.addWidget(self.ma_covar_label,11,0) 
        grid.addWidget(self.tableView,12,0,6,2)
        grid.addWidget(self.boton_ma_covar,12,2)
        grid.addWidget(self.arch_macovar_edit,12,4)

        grid.addWidget(self.boton_salir,17,2)
        
        """
        Acciones
        """
        self.boton_procesa.setEnabled(False)
        self.boton_grafica.setEnabled(False)
        self.boton_ma_covar.setEnabled(False)
        self.boton_norad.clicked.connect(self.botonNorad)
        self.boton_equipo.clicked.connect(self.Archivo)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_prepros.clicked.connect(self.PreProc)
        self.boton_procesa.clicked.connect(self.procesar)
        self.boton_grafica.clicked.connect(self.Graficar)
        self.boton_ma_covar.clicked.connect(self.Macovar)
        
        
        self.setLayout(grid)
        self.setWindowTitle('Procesamiento de TLE')    
        self.show()
        
                
    def botonNorad(self):
        print "Procesando la Conexion con NORAD para la Descarga..."
        self.w = ConexionNorad()
        self.w.exec_()
        self.sat_id, self.fini, self.ffin, self.filename = self.w.datos()
        self.arch_cargado.setText(self.filename)
        self.sat_id_line.setText(self.sat_id)  
        
    def Archivo(self):    
        fname=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../TleAdmin/crudosTLE/*")
        nombre=str(fname).split('/')[-1]
        self.filename = nombre
        self.sat_id = nombre.split('_')[0]
        self.arch_cargado.setText(self.filename)
        
    def PreProc(self):
        """
        Invoca a la funcion setTLE, para fragmentar
        cada uno de los TLE del dato crudo en archivos
        individuales; y los guarda en: TleAdmin/tle
        """
        files=glob.glob('../TleAdmin/tle/*')
        for filename in files:
            os.unlink(filename)
        if os.stat('../TleAdmin/crudosTLE/'+self.filename).st_size == 0:
            print('El archivo esta vacio')
        setTLE(self.sat_id, self.filename)
        self.sat_id_line.setText(self.sat_id)
        self.lista=glob.glob('../TleAdmin/tle/*')
        self.tles=len(self.lista)
        self.cant_tles_edit.setText(str(self.tles))
        """
        Ordenamiento de los TLEs
        """
        self.tledic=generadorDatos(self.lista)
        self.tleOrdenados=ordenaTles(self.tledic)
        self.boton_procesa.setEnabled(True)
        """
        Impresiones de info de TLEs.
        """
        print 'TLE PRIMARIO'
        print '-----------------------------------------------------'
        tle_primario = Tle('../TleAdmin/tle/'+self.tleOrdenados[-1][0])
        linea1= tle_primario.linea1
        linea2= tle_primario.linea2
        self.tle_pri_edit.setText(linea1+'\n'+linea2)
        print linea1
        print linea2
        print '-----------------------------------------------------'
    
    def procesar(self):
        files=glob.glob('../AjustarTLE/diferencias/*')
        for filename in files:
            os.unlink(filename)
        self.bin=difTle(self.tleOrdenados, self.tles)
        self.cantxbin,self.mediaxbin=genera_estadisticaBin(self.bin)
        self.diferencias=difPrimario(self.filename,self.tles-1)
        self.estado_proc_edit.setText(self.diferencias)
        self.boton_grafica.setEnabled(True)
        self.boton_ma_covar.setEnabled(True)
        
        
#     def Graficar(self):
#         self_grafico_pw=VerGrafico(self.diferencias)
        
    def Graficar(self):
#        data=[self.sat_id,self.diferencias,self.cantxbin, self.mediaxbin]
        data=[self.sat_id,self.diferencias]
        self.graf = RepresentacionGrafica(data)
        self.graf.exec_()
        
    def ver_mediasxbin(self):
        desviacion_standard_graf(self.sat_id, self.mediaxbin[0], self.mediaxbin[1], self.mediaxbin[2])

    def Macovar(self):
        self.macovarT, self.arch_macovar=EjecutaMaCovar(self.diferencias)
        self.tableView.setRowCount(len(self.macovarT))
        self.tableView.setColumnCount(len(self.macovarT))
        for i,fila in enumerate(self.macovarT):
            for j,col in enumerate(fila):
                self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
        self.arch_macovar_edit.setText(self.arch_macovar)        
    
    def salir(self):
        self.accept()

class ConexionNorad(QDialog):
#     def __init__(self):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.archTLE=''
        self.cat_id=''
        self.fini=''
        self.ffin=''
#         
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.lightGray)
        self.setPalette(self.palette)
#         
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
        Etiquetas
        """
        self.usuario    = QLabel('Usuario: ')
        self.passw      = QLabel('Password: ')
        self.norad_id   = QLabel('NORAD ID: ')
        self.stime      = QLabel('Fecha Inicio')
        self.ftime      = QLabel('Fecha Fin')
        self.arhcivoTLE = QLabel('Ingrese el nombre para guardar el archivo')
        """
        Botones
        """
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.boton_request = QPushButton('Enviar Solicitud')
        self.boton_guardar = QPushButton('guardar')
        """
        Campos de Edicion
        """
        self.usuario_edit  = QLineEdit('macecilia')
        self.clave_edit    = QLineEdit('MaCeciliaSpace17')
        self.clave_edit.setEchoMode(QLineEdit.Password)
        self.norad_id_edit = QLineEdit()
        self.st            = QLineEdit()
        self.et            = QLineEdit()
        self.nombreTle     = QLineEdit()

        """
        Solapas
        """        
        self.grilla = QGridLayout()
        self.grilla.setSpacing(2)
        self.grilla.addWidget(self.usuario,1,1)
        self.grilla.addWidget(self.usuario_edit,1,2)
        self.grilla.addWidget(self.passw,2,1)
        self.grilla.addWidget(self.clave_edit,2,2)
        self.grilla.addWidget(self.norad_id,3,2)
        self.grilla.addWidget(self.norad_id_edit,4,2)
        self.grilla.addWidget(self.stime,5,1)
        self.grilla.addWidget(self.ftime,5,2)
        self.grilla.addWidget(self.cal,6,1)
        self.grilla.addWidget(self.cal1,6,2)
        self.grilla.addWidget(self.st,7,1)
        self.grilla.addWidget(self.et,7,2)
        self.grilla.addWidget(self.arhcivoTLE,8,1)
        self.grilla.addWidget(self.nombreTle,8,2)
        self.grilla.addWidget(self.boton_request,11,2)
        self.grilla.addWidget(self.boton_guardar,12,2)
        self.grilla.addWidget(self.buttons,13,2) 
        self.setLayout(self.grilla) 
        
        """
        Acciones
        """
        self.boton_request.clicked.connect(self.iniciaSolicitud)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)  
        self.boton_guardar.clicked.connect(self.datos)
        self.setWindowTitle('Conexion con NORAD')
#         
    def iniciaSolicitud(self):
        
        self.usu1   = str(self.usuario_edit.text())
        self.passw1 = str(self.clave_edit.text())
        self.cat_id = str(self.norad_id_edit.text())
        self.nombreTle.setText(self.cat_id+'_'+self.fini+'_'+self.ffin+'.tle')
        self.tle=importar_tle(self.usu1,self.passw1,self.cat_id,self.pydate,self.pydate1,self.nombreTle.text())
        self.archTLE=self.nombreTle.text()
#             
    def verFinicio(self):
        self.date = self.cal.selectedDate()
        self.pydate = self.date.toPyDate()
        self.st.setText(self.date.toString())
        self.fini=str(self.pydate.year)+str(self.pydate.month)+str(self.pydate.day)
#         
    def verFfin(self):
        self.date1 = self.cal1.selectedDate()
        self.pydate1 = self.date1.toPyDate()
        self.et.setText(self.date1.toString())
        self.ffin=str(self.pydate1.year)+str(self.pydate1.month)+str(self.pydate1.day)
        
    def datos(self):
        return self.cat_id, self.fini, self.ffin, self.archTLE
    
class RepresentacionGrafica(QDialog):
        
    def __init__(self,set_datos=None,parent=None):
        QDialog.__init__(self,parent)

        self.sat_id=set_datos[0]
        self.dt=set_datos[5]
        self.data=set_datos[6]
        self.coef=set_datos[7]
        
        self.setWindowModality(Qt.ApplicationModal)
        layout = QHBoxLayout()

        graficos=["Diferencias Totales","Diferencias por Coordenada","Diferencias del Set Principal","Histograma de Bin"]
        self.listWidget = QListWidget()
        self.listWidget.addItems(graficos)
        

        self.figura=plt.figure()
        self.canvas = FigureCanvas(self.figura)
        """
        Boton
        """
        self.boton_salir = QPushButton('Salir')
        
        """
        Etiquetas
        """
        self.escribir = QTextEdit()
        
        """
        Acciones
        """
        self.listWidget.itemSelectionChanged.connect(self.itemChanged)
#        self.listWidget.itemClicked.connect(self.item_click)
        self.boton_salir.clicked.connect(self.salir)


        layout.addWidget(self.listWidget)
        layout.addWidget(self.canvas)
        layout.addWidget(self.boton_salir)
        self.setLayout(layout)
        self.setWindowTitle('Graficos')

#     def add_items(self):
#         for item_text in ['item1', 'item2', 'item3']:
#             item = QListWidgetItem(item_text)
#             self.addItem(item)

            

    def itemChanged(self):
        item = QListWidgetItem(self.listWidget.currentItem())
        item_str=item.text()
        if item_str == "Diferencias Totales":
            self.figura = ploteos.grafica_setcompleto(self.dt, self.data, self.coef)
#            ploteos.grafica_diferenciasTotales(self.sat_id,self.dt,self.data,self.coef)
            self.canvas = FigureCanvas(self.figura)
            self.canvas.draw()
    #        elif item_str == 'Diferencias por Coordenada':
#         else:
#             ploteos.grafica_setcompleto(self.dt, self.data, self.coef)
#             self.canvas.draw()

#     def item_click(self, item):
#         item_str=self.listWidget.currentItem().text()
#         if item_str == "Diferencias Totales":
#             ploteos.grafica_diferenciasTotales(self.sat_id,self.dt,self.data,self.coef)
#             self.canvas.draw()
# #        elif item_str == 'Diferencias por Coordenada':
#         else:
#             ploteos.grafica_setcompleto(self.dt, self.data, self.coef)
#             self.canvas.draw()
#         else:
#             desviacion_standard_graf(self.sat_id, self.mediaxbin[0], self.mediaxbin[1], self.mediaxbin[2])
#             self.canvas.draw()      
        
    def salir(self):
        self.accept()
        

    
class ProcMision(QDialog):
    """
    REQUIERE CORRER PRIMERO EL PROCESAMIENTO TLE!!!
    Utiliza los datos ya cargados en TleAdmin/tle y los Datos de los archivos CODS.
    Carga el set de datos TLE y realiza el metodo de Osweiler para estimar las diferenicas
    """

    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

        self.setWindowModality(Qt.ApplicationModal)
#       self.resize(1200, 600)
#        self.resize(1700, 700)
        self.initUI()
        
        self.sat_id='99999'
        self.sat_nombre=''
        self.linea1=''
        self.linea2=''
        self.grafico_arch=''
        self.dif_cvstle= ''
        self.macovarT=''
        self.dt=[]
        self.data=[]
        self.coef=[]
        self.set_datos=[]
        
    def initUI(self):
        self.grilla = QGridLayout()
        self.grilla.setSpacing(10)
        
        """
        Etiquetas
        """
        self.mision_lab     = QLabel('Mision')
        self.fechaini_lab   = QLabel('Fecha Inicio')
        self.fechafin_lab   = QLabel('Fecha Fin')
        self.ma_lab       = QLabel('Ma. Varianza-Covarianza')
        
        """
        Botones
        """
        self.boton_procesar   = QPushButton('Procesar')
        self.boton_dtotales   = QPushButton('Graficar Diferencias Totales')
        self.boton_dxcoord    = QPushButton('Graficar Diferencias por Coordenadas')
        self.boton_macovar    = QPushButton('Calcular Matriz')
        self.boton_salir      = QPushButton('Salir')
        
        """
        Campos de Edicion
        """
        self.fechaini_edit   = QLineEdit()
        self.fechafin_edit   = QLineEdit()
        self.tlepri_edit     = QTextEdit()
                
        """
        Lista desplegada
        """
        self.listaSat       = QComboBox()
        self.listaSat.addItem("...");
        self.listaSat.addItem("SAC-D"); 
        self.listaSat.addItem("LAGEOS");
        self.listaSat.addItem("ICESAT");
        """
        tabla
        """
        self.tableView       = QTableWidget()
        
        self.grilla.addWidget(self.mision_lab,1,0)
        self.grilla.addWidget(self.listaSat,1,1)
        self.grilla.addWidget(self.boton_procesar,2,1)
        self.grilla.addWidget(self.fechaini_lab,3,0)
        self.grilla.addWidget(self.fechaini_edit,3,1)
        self.grilla.addWidget(self.fechafin_lab,4,0)
        self.grilla.addWidget(self.fechafin_edit,4,1)
        self.grilla.addWidget(self.tlepri_edit,5,0,1,2)
        self.grilla.addWidget(self.boton_dtotales,6,0)
        self.grilla.addWidget(self.boton_dxcoord,6,1)
        self.grilla.addWidget(self.tableView,7,0,7,1)
        self.grilla.addWidget(self.boton_macovar,8,1)
        self.grilla.addWidget(self.boton_salir,17,1)
        
        """
        Acciones
        """
        self.listaSat.currentIndexChanged.connect(self.selectionchange)
        self.boton_procesar.clicked.connect(self.procesarCods)
        self.boton_procesar.setEnabled(False)
        self.boton_dtotales.setEnabled(False)
        self.boton_dxcoord.setEnabled(False)
        self.boton_macovar.setEnabled(False)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_dtotales.clicked.connect(self.ver_diferencias_totales)
        self.boton_dxcoord.clicked.connect(self.ver_dif_x_coordenadas)
        self.boton_macovar.clicked.connect(self.Macovar)
#        self.datos_mis_edit.textChanged.connect(self.validar_nombre)
                
        self.setWindowTitle('PROCESAMIENTO de DATOS CODS')
        self.setLayout(self.grilla) 
        
    def selectionchange(self,i):
        self.sat_nombre= self.listaSat.currentText()
        self.dic_satelites={'SAC-D':37673,'LAGEOS':8820,'ICESAT':27642}
        self.sat_id=self.dic_satelites[str(self.sat_nombre)]
        self.boton_procesar.setEnabled(True)
        
    def procesarCods(self):
        self.set_datos=ejecutaProcesamientoCods()
        self.sat_id=self.set_datos[0]
        self.linea1=self.set_datos[1]
        self.linea2=self.set_datos[2]
        self.fini=self.set_datos[3]
        self.ffin=self.set_datos[4]
        self.dt=self.set_datos[5]
        self.data=self.set_datos[6]
        self.coef=self.set_datos[7]
        self.grafico_arch=self.set_datos[8]
        self.fechaini_edit.setText(self.fini)
        self.fechafin_edit.setText(self.ffin)
        self.tlepri_edit.setText(self.linea1+'\n'+self.linea2)
        self.boton_dtotales.setEnabled(True)
        self.boton_dxcoord.setEnabled(True)
        self.boton_macovar.setEnabled(True)
        
    def ver_diferencias_totales(self):
#         self.graf = RepresentacionGrafica(self.set_datos)
#         self.graf.exec_()
        ploteos.grafica_diferenciasTotales(self.sat_id,self.dt,self.data,self.coef)
        
    def ver_dif_x_coordenadas(self):
        ploteos.grafica_setcompleto(self.dt, self.data, self.coef)
        
        
    def Macovar(self):
        self.macovarT=EjecutaMaCovarCODS(self.grafico_arch)
#self.dif_cvstle)
        self.tableView.setRowCount(len(self.macovarT))
        self.tableView.setColumnCount(len(self.macovarT))
        for i,fila in enumerate(self.macovarT):
            for j,col in enumerate(fila):
                self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
   
    def salir(self):
        self.accept()
        
        
#def IniciaApp():
if __name__ == '__main__':
    
    """
    Se crean los directorios necesarios.
    """
    
    d1='../TleAdmin/tle'
    if not os.path.exists(d1):
        os.mkdir(d1)
    d2='../AjustarTLE/diferencias'
    if not os.path.exists(d2):
        os.mkdir(d2)
    d3='../main/matrices/'
    if not os.path.exists(d3):
        os.mkdir(d3)
    d4='../visual/archivos'
    if not os.path.exists(d4):
        os.mkdir(d4)
    
    """
    INICIA LA INTERFAZ
    """
    QApplication.setStyle("plastique")
    app = QApplication(sys.argv)
    ex = ProcARxCODE()
    sys.exit(app.exec_())
