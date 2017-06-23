'''
Created on Feb 5, 2017

@author: mcvalenti
'''
import sys, glob, os, re
import numpy as np
from datetime import datetime, timedelta
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from CDM.cdmParser import extraeCDM
from pruebas.claseTle import Tle, Encuentro
from TleAdmin.TleArchivos import divide_setTLE
#from TleAdmin.TLE import Tle
from TleAdmin.get_tle import importarSetTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle, difPrimario, genera_estadisticaBin
from Estadistica.maCovar import EjecutaMaCovar, EjecutaMaCovarCODS
from Encuentro.akellaPoC import evaluaEncuentro
from Comparar.TlevsCodsOSW import ejecutaProcesamientoCods, dif_tleCODS15dias
from visual import ploteos
from visual.trackencuentro import grafica_track
from visual.TleOsweiler import VerGrafico
# #from visual.TlevsCodsGraf import VerGraficoMision
# from visual.CodsOsweiler import VerGraficoCods
from visual.binGraf import histograma_bin, desviacion_standard_graf
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class ProcARxCODE(QMainWindow):
    
    def __init__(self):
        super(ProcARxCODE, self).__init__()
        
        self.setWindowTitle('ARxCODE')
        self.setWindowIcon(QIcon('nave.png'))
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
    
        self.inicio = QLabel() 
        pixmap = QPixmap('../visual/imagenes/orbitas') #nubeDebris') #cords_contol.jpg')
        self.inicio.setPixmap(pixmap)
        self.setCentralWidget(self.inicio)

        
        #IMAGEN
#         palette    = QPalette()
#         palette.setBrush(QPalette.Background,QBrush(QPixmap('../visual/imagenes/cords_contol.jpg')))
#         self.setPalette(palette)
        """
        DockWidgets
        """
        # Lista de Encuentros.
        self.encuentros = QDockWidget("Registro de Encuentros", self)
        self.listWidget = QListWidget()
        self.listWidget.addItem("PROXIMO ENCUENTRO")
        self.listWidget.addItem("Encuentros Anteriores.")
        self.encuentros.setWidget(self.listWidget)
        self.encuentros.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.encuentros)
        # Lista de Procesamientos.
        self.procesamientos = QDockWidget("Procesamientos", self)
        self.listWidget1 = QListWidget()
        self.listWidget1.addItem("Procesamiento de un set de TLE")
        self.listWidget1.addItem("Procesamiento de Datos de Mision")
        self.procesamientos.setWidget(self.listWidget1)
        self.procesamientos.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.procesamientos)
        
        """
        Acciones
        """
        self.listWidget.itemClicked.connect(self.item_click)
        self.listWidget1.itemClicked.connect(self.item_click1)

        self.show()

        
    def item_click(self):       
        cdm_click=self.listWidget.currentItem().text()
        if cdm_click == 'PROXIMO ENCUENTRO':
            ventana1=ProcCDM()
            self.setCentralWidget(ventana1)
            ventana1.exec_()
        else:
            ventana2=ProcEncuentro()
            self.setCentralWidget(ventana2)
            ventana2.exec_()

    def item_click1(self):
        c_item=self.listWidget1.currentItem().text()
        if c_item == 'Procesamiento de un set de TLE':
            ventana3=ProcTle()
            self.setCentralWidget(ventana3)
            ventana3.exec_()
        else:
            ventana4=ProcMision()
            self.setCentralWidget(ventana4)
            ventana4.exec_()
                
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
    
    def close_application(self):
        sys.exit()
    
class ProcCDM(QDialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        
        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()


    def initUI(self):
        
        """
        Etiquetas
        """
        self.cdm_titulo = QLabel('Informe CDM')      
        """
        Botones
        """
        self.boton_grafCdm  = QPushButton('Graficos')
        self.boton_informe  = QPushButton('Generar Informe')
        self.boton_salirCdm = QPushButton('SALIR')
        """
        OTROS
        """
        self.CDM_edit    = QTextEdit()
        self.tablePOC   = QTableWidget()
        self.tablePOC.setRowCount(2)
        self.tablePOC.setColumnCount(8)
        listaLabels=['Norad Id','Nombre','TCAcdm','TCAarx','MinD cdm','MinD arx','PoC cdm','PoC arx']
        self.tablePOC.setHorizontalHeaderLabels(listaLabels)
        
        grid = QGridLayout()
        grid.setSpacing(5)
        
        grid.addWidget(self.CDM_edit,2,1)
        grid.addWidget(self.cdm_titulo,1,1)
        grid.addWidget(self.boton_grafCdm,4,2)
        grid.addWidget(self.boton_informe,5,2)
        grid.addWidget(self.boton_salirCdm,6,2)
        grid.addWidget(self.tablePOC,3,1)
        
        self.setLayout(grid)
        self.setWindowTitle('Procesamiento de CDM')    
        self.show()
        
        """
        Acciones
        """
        self.boton_salirCdm.clicked.connect(self.salirCdm)
        
        """
        Carga de Informacion principal
        """
        self.cdm_xml=QFileDialog.getOpenFileName(self, 'Seleccione el CDM a Procesar', "../CDM/archivos/*")
        self.cdm_nombre=str(self.cdm_xml).split('/')[-1]
        self.TCA, self.MISS_DISTANCE,self.POC,self.obj_list=extraeCDM(self.cdm_nombre)
        infoCDM='Mision = '+str(self.obj_list[0][0])+'---- ID= '+str(self.obj_list[0][1])+'\n'+'Desecho = '+str(self.obj_list[1][0])+'---- ID= '+str(self.obj_list[1][1])+'\n'+'TCA = '+self.TCA+'\n'+'Minima Distancia [m] = '+self.MISS_DISTANCE+'\n'+'Probabilidad de Colision = '+self.POC                                                          
        self.CDM_edit.setText(infoCDM)
                
        """
        Pruebas ENVISAT-COSMOS
        """
        self.TCA=datetime(2008,1,9,19,0,30,6)
        TCAstr0=datetime.strftime(self.TCA,'%Y-%m-%dT%H:%M:%S')
        self.sat_idc='27386' #ENVISAT
        self.deb_idc='15482' #COSMOS
        
        Cd=np.array([[4.1345498441906514,-0.031437388833697122,0.078011634263035007],
                [-0.031437388833697122,0.0025693554190851101,-0.014250096142904997],
                [0.078011634263035007,-0.014250096142904997,0.096786625771746529]])
    
        Cm=np.array([[4.8247926515782202,0.05994752830943241,0.049526867540809635],
                [0.05994752830943241,0.019150349628774828,0.012470649611436152],
                [0.049526867540809635,0.012470649611436152,0.012649606483621921]])
        
        TCAc,mod_dif,poc=evaluaEncuentro(self.TCA,self.sat_idc,self.deb_idc,Cd,Cm)
        TCAstr=datetime.strftime(TCAc,'%Y-%m-%d %H:%M:%S.%f')
        mod_dif=int(mod_dif*1000.0)
        # set data self.TCA, self.MISS_DISTANCE,self.POC
        self.tablePOC.setItem(0,0, QTableWidgetItem('Mision'))
        self.tablePOC.setItem(1,0, QTableWidgetItem('Debris'))
        self.tablePOC.setItem(0,1, QTableWidgetItem(self.sat_idc))
        self.tablePOC.setItem(1,1, QTableWidgetItem(self.deb_idc))
        self.tablePOC.setItem(0,2, QTableWidgetItem(TCAstr0))
        self.tablePOC.setItem(0,3, QTableWidgetItem(TCAstr))
        self.tablePOC.setItem(0,4, QTableWidgetItem(self.MISS_DISTANCE))
        self.tablePOC.setItem(0,5, QTableWidgetItem(str(mod_dif)))
        self.tablePOC.setItem(0,6, QTableWidgetItem(self.POC))
        self.tablePOC.setItem(0,7, QTableWidgetItem(poc))

    def salirCdm(self):
        self.accept()
class ProcEncuentro(QDialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()
    # Parametros
        self.sat_id=''
        self.deb_id=''
        self.tca=''
        self.min_dist=None
        self.tca_calc=None
        
        
    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.white)
        self.setPalette(self.palette)
        
        """
        Etiquetas
        """
        self.sat_lab  = QLabel('Satelite NORAD ID')
        self.deb_lab  = QLabel('Desecho NORAD ID')
        self.time_lab = QLabel('TCA')
        self.hs_lab   = QLabel('Hs:')
        self.min_lab  = QLabel('min:')
        self.seg_lab  = QLabel('seg')
        self.mseg_lab = QLabel('mseg')
        # imagen 
        self.track = QLabel() 
        self.dif   = QLabel()
        #track.setPixmap(pixmap)
        """
        Botones
        """
        self.boton_encuetro = QPushButton('Procesar Encuentro')
        self.boton_dif      = QPushButton('Ver diferencias')
        self.boton_track    = QPushButton('Track')
        self.boton_salir    = QPushButton('Salir')
        """
        Campos de Edicion
        """
        self.sat_id_text = QLineEdit()
        self.deb_id_text = QLineEdit()
        self.tca_text    = QCalendarWidget()
        self.hs_tex      = QLineEdit()
        self.min_tex     = QLineEdit()
        self.seg_tex     = QLineEdit()
        self.mseg_tex    = QLineEdit()

        """
        Otros
        """
        self.tableEncuentro   = QTableWidget()
        self.tableEncuentro.setRowCount(1)
        self.tableEncuentro.setColumnCount(4)
        listaLabels=['Norad Id','Nombre','TCAarx','MinD arx']
        self.tableEncuentro.setHorizontalHeaderLabels(listaLabels)
        """
        Plantilla
        """
        grid = QGridLayout()
        grid.setSpacing(5)
        scroll = QScrollArea()

        
        grid.addWidget(self.sat_lab,2,1)
        grid.addWidget(self.sat_id_text,2,2)
        grid.addWidget(self.deb_lab,3,1)
        grid.addWidget(self.deb_id_text,3,2)
        grid.addWidget(self.time_lab,4,1)
        grid.addWidget(self.tca_text,4,2)
        grid.addWidget(self.hs_tex,4,3)
        grid.addWidget(self.hs_lab,4,4)
        grid.addWidget(self.min_tex,4,5)
        grid.addWidget(self.min_lab,4,6)
        grid.addWidget(self.seg_tex,4,7)
        grid.addWidget(self.seg_lab,4,8)
        grid.addWidget(self.mseg_tex,4,9)
        grid.addWidget(self.mseg_lab,4,10)        
        grid.addWidget(self.tableEncuentro,6,2,2,5)
        grid.addWidget(self.track,8,2)
        grid.addWidget(self.dif,8,3)
        grid.addWidget(self.boton_encuetro,6,10)
        grid.addWidget(self.boton_dif,7,10)
        grid.addWidget(self.boton_track,8,10)
        grid.addWidget(self.boton_salir,9,10)
        
        """
        Acciones
        """
        self.boton_encuetro.clicked.connect(self.procesoSimple)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_track.clicked.connect(self.mostrarTrack)
        self.boton_dif.clicked.connect(self.mostrarDif)
        self.boton_track.setEnabled(False)
        self.boton_dif.setEnabled(False)
        
        self.setLayout(grid)
        self.setWindowTitle('Procesamiento de Encuentro')    
        self.show()
    
    def procesoSimple(self):
        """
        Propaga los objetos involucrados un intervalos [tca-90:tca+10]
        Calcula:
            Miss Distance
            TCA calculado
            Diferencias en RTN ---> Plotea.
            Genera archivo lat, long ---> Plotea.
          
        """
        # Importar los TLE de NORAD.
    
        usuario='macecilia'
        clave='MaCeciliaSpace17'
        self.sat_id=str(self.sat_id_text.text())
        self.deb_id=str(self.deb_id_text.text())
        hs =int(self.hs_tex.text())
        min=int(self.min_tex.text())
        seg=int(self.seg_tex.text())
        fecha = self.tca_text.selectedDate()#.toPyDate()
        hora = QTime(hs,min,seg)
        self.tca=QDateTime(fecha,hora).toPyDateTime()
        tle_sat=Tle.creadoxParam(usuario, clave, self.sat_id, self.tca)
        tle_deb=Tle.creadoxParam(usuario, clave, self.deb_id, self.tca)
#         
        """
        Propagacion hasta el Encuentro
        """
        encuentro1=Encuentro(tle_sat,tle_deb,self.tca)
        self.min_dist= encuentro1.mod_minDist
        self.tca_calc= encuentro1.tca_c
        self.tableEncuentro.setItem(0,0, QTableWidgetItem(self.sat_id))
        self.tableEncuentro.setItem(0,1, QTableWidgetItem(self.deb_id))
        self.tableEncuentro.setItem(0,2, QTableWidgetItem(datetime.strftime(self.tca_calc,'%Y-%m-%d %H:%M:%S')))
        self.tableEncuentro.setItem(0,3, QTableWidgetItem(str(self.min_dist)))
        # archivo de diferencias.
        self.archivo_dif=encuentro1.archivo_dif
        

        print 'Minima Distancia = ', encuentro1.mod_minDist,encuentro1.epoca_ini
        grafica_track('../Encuentro/archivos/'+str(self.sat_id)+'U', '../Encuentro/archivos/'+str(self.deb_id)+'U')
        print 'fin del procesamiento.'
        
        self.boton_track.setEnabled(True)
        self.boton_dif.setEnabled(True)
    
    def mostrarDif(self):
        self.grafico_dif= ploteos.grafica_diferenciasRIC(self.archivo_dif)
        self.pixmap1 = QPixmap(self.grafico_dif)
        self.dif.setPixmap(self.pixmap1)
    
    def mostrarTrack(self):
        self.pixmap = QPixmap('../visual/archivos/ploteo_track.ps')
        self.track.setPixmap(self.pixmap)
        
    def salir(self):
        self.accept()    
        
        
class ProcTle(QDialog):

    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()

        self.filename = ''
        self.sat_id='99999'
        self.fini=''
        self.ffin=''
        self.fin_tle=datetime(1957,1,1,0,0,0)
        self.ini_tle=datetime(1957,1,1,0,0,0)
        self.tles=0
        self.tleOrdenados={}
        self.data=[]
        self.coef=[]
        self.path='../AjustarTLE/diferencias/'
        self.diferencias=''
        self.set_data=[]
        self.set_pri=[]
        self.arch_macovar=''
        self.macovarT=''  
        self.cantxbin=[]
        self.mediaxbin=[]      
        
    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.white)
        self.setPalette(self.palette)
        
        """
        Etiquetas
        """
        self.carga           = QLabel('CARGADO DE TLEs')
        self.norad           = QLabel('A partir de NORAD')  
        self.equipo          = QLabel('Desde el Equipo')
        self.arch_prepro     = QLabel('Archivo a Procesar: ')
        self.sat_id_label    = QLabel('NORAD_ID')
        self.cant_tles       = QLabel('Cantidad de TLEs')
        self.tle_pri         = QLabel('Ultimo TLE del set.')
        self.outputs         = QLabel('Output')
        self.ma_covar_label  = QLabel('Ma. de COVARIANZA')
        """
        Botones
        """
        self.boton_norad        = QPushButton('Space-Track')
        self.boton_equipo       = QPushButton('Directorios')
        self.boton_procesa      = QPushButton('PROCESAR')
        self.boton_dtotales     = QPushButton('Graficar Diferencias Totales')
        self.boton_dxcoord      = QPushButton('Graficar Diferencias por Coordenadas')
        self.boton_dsetprimario = QPushButton ('Graficar Diferencias del Set primario')
        self.boton_salir        = QPushButton('Salir')
        """
        Campos de Edicion
        """
        self.arch_cargado       = QLineEdit()
        self.sat_id_line        = QLineEdit()
        self.cant_tles_edit     = QLineEdit()
        self.matriz             = QLineEdit()
        self.estado_proc_edit   = QLineEdit()
        """
        OTROS
        """
        self.tle_pri_edit    = QTextEdit()
        self.tableView       = QTableWidget()
        """
        Plantilla
        """
        grid = QGridLayout()
        grid.setSpacing(5)
        
        grid.addWidget(self.carga,2,0)
        grid.addWidget(self.norad,3,0)
        grid.addWidget(self.boton_norad,3,1)
        grid.addWidget(self.equipo,4,0)
        grid.addWidget(self.boton_equipo,4,1)
        grid.addWidget(self.arch_prepro,5,0)
        grid.addWidget(self.arch_cargado,5,1)
        grid.addWidget(self.boton_procesa,5,2)
        grid.addWidget(self.sat_id_label,7,0)
        grid.addWidget(self.sat_id_line,7,1)
        grid.addWidget(self.cant_tles,8,0)
        grid.addWidget(self.cant_tles_edit,8,1)        
        grid.addWidget(self.tle_pri,9,0)
        grid.addWidget(self.tle_pri_edit,10,0,1,4)
        grid.addWidget(self.ma_covar_label,11,0) 
        grid.addWidget(self.tableView,12,0)
        grid.addWidget(self.outputs,23,1)
        grid.addWidget(self.estado_proc_edit,23,2)
        grid.addWidget(self.boton_dsetprimario,24,2)
        grid.addWidget(self.boton_salir,25,2)
#         grid.addWidget(self.boton_dtotales,25,1)
#         grid.addWidget(self.boton_dxcoord,25,2)
        
        """
        Acciones
        """
        self.boton_procesa.setEnabled(False)
        self.boton_norad.clicked.connect(self.botonNorad)
        self.boton_equipo.clicked.connect(self.Archivo)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_procesa.clicked.connect(self.procesar)
        self.boton_dsetprimario.clicked.connect(self.ver_dif_set_primario)
#         self.boton_dxcoord.clicked.connect(self.ver_dif_x_coordenadas)
#         self.boton_dtotales.clicked.connect(self.ver_diferencias_totales)
        self.setLayout(grid)
        self.setWindowTitle('Procesamiento de TLE')    
        self.show()
          
    def botonNorad(self):
        print ("Procesando la Conexion con NORAD para la Descarga...")
        self.w = ConexionNorad()
        self.w.exec_()
        self.sat_id, self.fini, self.ffin, self.filename = self.w.iniciaSolicitud()
        self.arch_cargado.setText(self.filename)
        self.sat_id_line.setText(self.sat_id) 
        self.boton_procesa.setEnabled(True) 
        
    def Archivo(self):    
        fname=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../TleAdmin/crudosTLE/*")
        nombre=str(fname).split('/')[-1]
        self.filename = nombre
        self.sat_id = nombre.split('_')[0]
        self.arch_cargado.setText(self.filename)
        self.boton_procesa.setEnabled(True)
        
    
    def procesar(self):
        """
        Invoca a la funcion divide_setTLE, para fragmentar
        cada uno de los TLE del dato crudo en archivos
        individuales; y los guarda en: TleAdmin/tle
        """
        files=glob.glob('../TleAdmin/tle/*')
        for filename in files:
            os.unlink(filename)
        if os.stat('../TleAdmin/crudosTLE/'+self.filename).st_size == 0:
            print('El archivo esta vacio')
        divide_setTLE(self.sat_id, self.filename)
        self.sat_id_line.setText(self.sat_id)
        self.lista=glob.glob('../TleAdmin/tle/*')
        self.tles=len(self.lista)
        self.cant_tles_edit.setText(str(self.tles))
        """
        Ordenamiento de los TLEs
        """
        self.tledic=generadorDatos(self.lista)
        self.tleOrdenados=ordenaTles(self.tledic)

        """
        Impresiones de info de TLEs.
        """
        print 'PROCESAMIENTO DE TLE'
        print '-----------------------------------------------------'
        print 'TLE PRIMARIO'
        print '-----------------------------------------------------'
        tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+self.tleOrdenados[-1][0])
        linea1= tle_primario.linea1
        linea2= tle_primario.linea2
        self.fin_tle=tle_primario.epoca()
        self.ffin=self.fin_tle.strftime('%Y-%m-%d %H:%M:%S.%f' )
        self.tle_pri_edit.setText(linea1+'\n'+linea2)
        print linea1
        print linea2
        print '-----------------------------------------------------'
        print 'TLE INICIAL DEL SET'
        print '-----------------------------------------------------'
        tle_inial = Tle.creadoxArchivo('../TleAdmin/tle/'+self.tleOrdenados[0][0])
        linea1_0= tle_inial.linea1
        linea2_0= tle_inial.linea2
        self.ini_tle=tle_inial.epoca()
        print linea1_0
        print linea2_0
        print '-----------------------------------------------------'
        
        """
        PROCESAMIENTO.
        """
        files=glob.glob('../AjustarTLE/diferencias/*')
        for filename in files:
            os.unlink(filename)
#        self.bin, self.data, self.set_pri, self.coef=difTle(self.tleOrdenados, self.tles)
        self.set_pri=difPrimario(self.tleOrdenados, self.tles)
        self.dt=self.set_pri[0]
        self.data1=self.set_pri[1]
        self.coef=self.set_pri[2]
        self.nombre_archivo=self.set_pri[3]
#         self.cantxbin,self.mediaxbin=genera_estadisticaBin(self.bin)
#         self.diferencias=difPrimario(self.nombre_archivo,self.tles-1)
        self.estado_proc_edit.setText(self.nombre_archivo)

        """
        Ma. de Covarianza
        """
        self.macovarT, self.arch_macovar=EjecutaMaCovar(self.nombre_archivo)
        self.tableView.setRowCount(len(self.macovarT))
        self.tableView.setColumnCount(len(self.macovarT))
        for i,fila in enumerate(self.macovarT):
            for j,col in enumerate(fila):
                self.tableView.setItem(i,j,QTableWidgetItem(str(col)))    
        
        print 'Fin del Procesamiento'
        
#     def ver_dif_x_coordenadas(self):
#         ploteos.grafica_setcompleto(self.sat_id,self.path,self.data1, self.coef)
#      
#     def ver_diferencias_totales(self):
#         ploteos.grafica_diferenciasTotales(self.sat_id,self.path,self.data1,self.coef) 
        
    def ver_dif_set_primario(self):
        ploteos.grafica_set_principal(self.sat_id,self.path, self.data1,self.coef)
        
#     def Graficar(self):
# #        data=[self.sat_id,self.diferencias,self.cantxbin, self.mediaxbin]
#         data=[self.sat_id,self.diferencias]
#         self.graf = RepresentacionGrafica(data)
#         self.graf.exec_()
        
    def ver_mediasxbin(self):
        desviacion_standard_graf(self.sat_id, self.mediaxbin[0], self.mediaxbin[1], self.mediaxbin[2])

#     def Macovar(self):
#         self.macovarT, self.arch_macovar=EjecutaMaCovar(self.diferencias)
#         self.tableView.setRowCount(len(self.macovarT))
#         self.tableView.setColumnCount(len(self.macovarT))
#         for i,fila in enumerate(self.macovarT):
#             for j,col in enumerate(fila):
#                 self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
#         self.arch_macovar_edit.setText(self.arch_macovar)        
    
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
        self.arhcivoTLE = QLabel('Archivo Generado')
        """
        Botones
        """
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.boton_request = QPushButton('Enviar Solicitud')

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
        self.grilla.addWidget(self.boton_request,8,2)
        self.grilla.addWidget(self.arhcivoTLE,9,1)
        self.grilla.addWidget(self.nombreTle,9,2)
        

        self.grilla.addWidget(self.buttons,13,2) 
        self.setLayout(self.grilla) 
        
        """
        Acciones
        """
        self.boton_request.clicked.connect(self.iniciaSolicitud)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)  
        self.setWindowTitle('Conexion con NORAD')
#         
    def iniciaSolicitud(self):
        
        self.usu1   = str(self.usuario_edit.text())
        self.passw1 = str(self.clave_edit.text())
        self.cat_id = str(self.norad_id_edit.text())
        self.nombreTle.setText(self.cat_id+'_'+self.fini+'_'+self.ffin+'.tle')
        self.tle=importarSetTLE(self.usu1,self.passw1,self.cat_id,self.pydate,self.pydate1,self.nombreTle.text())
        self.archTLE=self.nombreTle.text()
        return self.cat_id, self.fini, self.ffin, self.archTLE
#             
    def verFinicio(self):
        self.date = self.cal.selectedDate()
        self.pydate = self.date.toPyDate()
        self.st.setText(self.date.toString())
        self.fini=str(self.pydate.year)+str(self.pydate.month).zfill(2)+str(self.pydate.day).zfill(2)
#         
    def verFfin(self):
        self.date1 = self.cal1.selectedDate()
        self.pydate1 = self.date1.toPyDate()
        self.et.setText(self.date1.toString())
        self.ffin=str(self.pydate1.year)+str(self.pydate1.month).zfill(2)+str(self.pydate1.day).zfill(2)

    
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
        self.path='../Comparar/diferencias/'
        self.dt=[]
        self.data=[]
        self.set_datos15dias=[]
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
        self.boton_procesar     = QPushButton('Procesar')
        self.boton_dtotales     = QPushButton('Graficar Diferencias Totales')
        self.boton_dxcoord      = QPushButton('Graficar Diferencias por Coordenadas')
        self.boton_dsetprimario = QPushButton ('Graficar Diferencias del Set primario')
        self.boton_macovar      = QPushButton('Calcular Matriz')
        self.boton_salir        = QPushButton('Salir')
        
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
        self.grilla.addWidget(self.boton_dsetprimario,6,2)
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
        self.boton_dsetprimario.setEnabled(False)
        self.boton_macovar.setEnabled(False)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_dtotales.clicked.connect(self.ver_diferencias_totales)
        self.boton_dxcoord.clicked.connect(self.ver_dif_x_coordenadas)
        self.boton_dsetprimario.clicked.connect(self.ver_dif_set_primario)
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
        files=glob.glob('../Comparar/diferencias/*')
        for filename in files:
            os.unlink(filename)
#        self.set_datos =ejecutaProcesamientoCods()
        self.set_datos= dif_tleCODS15dias()
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
        self.boton_dsetprimario.setEnabled(True)
        self.boton_macovar.setEnabled(True)
        
    def ver_diferencias_totales(self):
        ploteos.grafica_diferenciasTotales(self.sat_id,self.path,self.data,self.coef)
        
    def ver_dif_x_coordenadas(self):
        ploteos.grafica_setcompleto(self.sat_id,self.path,self.data, self.coef)
        
    def ver_dif_set_primario(self):
        ploteos.grafica_set15dias(self.data, self.coef)
#        ploteos.grafica_set_principal(self.sat_id,self.path,self.grafico_arch,self.ffin)
        
        
    def Macovar(self):
        self.macovarT=EjecutaMaCovarCODS(self.grafico_arch)
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
    d2b='../Comparar/diferencias'
    if not os.path.exists(d2b):
        os.mkdir(d2b)
    d3='../main/matrices/'
    if not os.path.exists(d3):
        os.mkdir(d3)
    d4='../visual/archivos/TLE'
    if not os.path.exists(d4):
        os.mkdir(d4)
    d5='../visual/archivos/CODS'
    if not os.path.exists(d5):
        os.mkdir(d5) 
    d6='../Estadistica/archivos'
    if not os.path.exists(d6):
        os.mkdir(d6)
    
    """
    INICIA LA INTERFAZ
    """
    QApplication.setStyle("Windows")
    app = QApplication(sys.argv)
    ex = ProcARxCODE()
    sys.exit(app.exec_())
