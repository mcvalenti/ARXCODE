'''
Created on Feb 5, 2017

@author: mcvalenti
'''
import sys, glob, os, re
import numpy as np
from datetime import datetime, timedelta
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from CDM.cdmParser import CDM,extraeCDM
#from pruebas.claseTle import Tle, Encuentro
#from TleAdmin.TleArchivos import divide_setTLE
from TleAdmin.TLE import Tle
from Encuentro.Encuentro import Encuentro
#from TleAdmin.get_tle import importarSetTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle, difPrimario, genera_estadisticaBin
from Estadistica.maCovar import EjecutaMaCovar, EjecutaMaCovarCODS
#from Encuentro.akellaPoC import evaluaEncuentro
from Comparar.TlevsCodsOSW import ejecutaProcesamientoCods, dif_tleCODS15dias
from visual import ploteos
#from visual.trackencuentro import grafica_track
from visual.TleOsweiler import VerGrafico
# #from visual.TlevsCodsGraf import VerGraficoMision
# from visual.CodsOsweiler import VerGraficoCods
from visual.binGraf import histograma_bin, desviacion_standard_graf
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from Validaciones.valida_PoC import proyecta_plano_de_encuentro, calcula_Poc_manual

class ProcARxCODE(QMainWindow):
    
    def __init__(self):
        super(ProcARxCODE, self).__init__()
        
        self.setWindowTitle('ARxCODE')
        
        extractAction = QAction("Salir", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip("Salir de ARxCODE")
        extractAction.triggered.connect(self.close_application)
        
        extractAction1 = QAction("&Gestion de Claves", self)
        extractAction2 = QAction("&Directorios para inputs/outputs", self)
        
        self.center()
        self.statusBar().showMessage('Ready')
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)
        VerMenu = mainMenu.addMenu('&Settings')
        VerMenu.addAction(extractAction1)
        VerMenu.addAction(extractAction2) 
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.inicio = QLabel() 
        figura_inicio = QPixmap('../visual/imagenes/orbitas') #nubeDebris') #cords_contol.jpg')
        self.inicio.setPixmap(figura_inicio)
        self.central_widget.addWidget(self.inicio)

        """
        DockWidgets
        """
        # Lista de Encuentros.
        self.encuentros = QDockWidget("Carga de Encuentros", self)

        self.encuentros.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.encuentros) 
        self.encuentros.setFeatures(QDockWidget.NoDockWidgetFeatures)
        #Lista de Botones en el Dock
        midock = QWidget()
        self.boton_cargarCDM = QPushButton('CARGAR CDM')
        self.boton_carga_manual = QPushButton('Carga Manual')
        self.boton_anteriores = QPushButton('Encuentro Anterior')
        self.boton_cargarCDM.setStyleSheet("QPushButton { background-color: white; border:3px solid blue;font: bold 14px;height: 78px;width: 120px; }")
        self.boton_carga_manual.setStyleSheet("QPushButton { background-color: white; border:3px solid blue;font: bold 14px;height: 78px;width: 120px; }")
        self.boton_anteriores.setStyleSheet("QPushButton { background-color: white; border:3px solid yellow;font: bold 14px;height: 78px;width: 120px; }")
        # plantilla
        stylesheet = \
        ".QWidget {\n" \
        + "border: 5px solid gray;\n" \
        + "border-radius: 4px;\n" \
        + "background-color: rgb(255, 255, 255);\n" \
        + "}"
        midock.setStyleSheet(stylesheet)
        layout=QVBoxLayout()
        layout.addWidget(self.boton_cargarCDM)
        layout.addWidget(self.boton_carga_manual)
        layout.addWidget(self.boton_anteriores)
        midock.setLayout(layout)
        self.encuentros.setWidget(midock)
        # Acciones
        self.boton_cargarCDM.clicked.connect(self.cargar_CDM)
        self.boton_carga_manual.clicked.connect(self.carga_manual)
        self.show()

    def cargar_CDM(self):
        ventana1=ProcCDM()
        self.central_widget.addWidget(ventana1)
        self.central_widget.setCurrentWidget(ventana1)      
         
    def carga_manual(self):
        ventana2=ProcEncuentro()
        self.central_widget.addWidget(ventana2)
        self.central_widget.setCurrentWidget(ventana2)    

#     def item_click1(self):
#         c_item=self.listWidget1.currentItem().text()
#         if c_item == 'Procesamiento de un set de TLE':
#             ventana3=ProcTle()
#             self.setCentralWidget(ventana3)
#             ventana3.exec_()
#         else:
#             ventana4=ProcMision()
#             self.setCentralWidget(ventana4)
#             ventana4.exec_()
                
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
    
    def close_application(self):
        sys.exit()

    
class ProcCDM(QWidget):
    def __init__(self,parent=None):
        
        super(ProcCDM, self).__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()        
        # Construccion
        self.TCA=None
        self.MISS_DISTANCE=None
        self.POC=None
        self.cov_rtn=None
        self.propagacion_errores=[]

    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.blue)
        self.setPalette(self.palette)
        # group boxes
        cdmFile_gbox       = QGroupBox('&Seleccion de CDM')
        results_gbox       = QGroupBox('&Datos del CDM')
        gbox_satMa         = QGroupBox('&Satelite MaCovar')    
        gbox_debMa         = QGroupBox('&Desecho  MaCovar')   
        """
        Etiquetas
        """
        self.cdm_archivo = QLabel('Archivo CDM: ')   
        self.opciones    = QLabel('Opciones')
        self.object1     = QLabel('Objeto 1')
        self.object2     = QLabel('Objeto 2')
        self.noradId     = QLabel('NORAD ID')      
        """
        Campos de Edicion
        """   
        self.archivo_tex  =QLineEdit('cdmTerraPegasus10.xml') # seteo el archivo para las pruebas
        self.noradId_obj1 =QLineEdit()
        self.noradId_obj2 =QLineEdit()
        """
        Botones
        """
        self.boton_dir      = QPushButton('Directorios')
        self.boton_cargar   = QPushButton('CARGAR')
        self.boton_grafCdm  = QPushButton('Graficos')
        self.boton_informe  = QPushButton('Generar Informe')
        self.boton_arcode   = QPushButton('Procesar con ARxCODE')
        self.boton_salirCdm = QPushButton('SALIR')
        """
        OTROS
        """
        self.tablePOC   = QTableWidget() # Tabla con los resultados
        self.tablePOC.setRowCount(1)
        self.tablePOC.setColumnCount(3)
        listaHLabels=['TCA','Dist. total [m]','PoC']
        listaVLabels=['CDM']
        header = self.tablePOC.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        width = self.tablePOC.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)
        self.tablePOC.setHorizontalHeaderLabels(listaHLabels)
        self.tablePOC.setVerticalHeaderLabels(listaVLabels)        
        # CDM box layout
        cdm_hlayout = QHBoxLayout()
        cdm_hlayout.addWidget(self.cdm_archivo)
        cdm_hlayout.addWidget(self.archivo_tex)
        cdm_hlayout.addWidget(self.boton_dir)
        cdmFile_gbox.setLayout(cdm_hlayout)       
        #------------------
        # Results layout
        #------------------
        result_vlayout = QVBoxLayout()
        # Data Grid layout
        data_glayout = QGridLayout()
        data_glayout.addWidget(self.object1,0,1)
        data_glayout.addWidget(self.object2,0,2)
        data_glayout.addWidget(self.noradId,1,0)
        data_glayout.addWidget(self.noradId_obj1,1,1)
        data_glayout.addWidget(self.noradId_obj2,1,2)
        result_vlayout.addLayout(data_glayout)
        result_vlayout.addWidget(self.tablePOC)
        results_gbox.setLayout(result_vlayout)   
        #--------------------
        # MATRICES
        #--------------------
        # Ma. del satelite
        self.tablesatelite   = QTableWidget()
        self.tablesatelite.setRowCount(3)
        self.tablesatelite.setColumnCount(3)
        listaLabels=['Radial','Transverse','Normal']
        header = self.tablesatelite.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        width = self.tablesatelite.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)
        self.tablesatelite.setHorizontalHeaderLabels(listaLabels)
        # Ma. del desecho
        self.tabledesecho   = QTableWidget()
        self.tabledesecho.setRowCount(3)
        self.tabledesecho.setColumnCount(3)
        listaLabels=['Radial','Transverse','Normal']
        header = self.tabledesecho.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        width = self.tabledesecho.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)
        self.tabledesecho.setHorizontalHeaderLabels(listaLabels) 
        
        # GBOX matriz del satelite
        layH_masat = QHBoxLayout()
        layH_masat.addWidget(self.tablesatelite)
        gbox_satMa.setLayout(layH_masat)   
        # GBOX matriz del satelite
        layH_madeb = QHBoxLayout()
        layH_madeb.addWidget(self.tabledesecho)
        gbox_debMa.setLayout(layH_madeb)

        # Layout Matrices
        layH_matrices = QHBoxLayout()
        layH_matrices.addWidget(gbox_satMa)
        layH_matrices.addWidget(gbox_debMa)
                     
        # vertical box layout
        vlayout = QVBoxLayout()
        vlayout.addWidget(cdmFile_gbox)
        vlayout.addWidget(self.boton_cargar)
        vlayout.addWidget(results_gbox)
        vlayout.addLayout(layH_matrices)
        vlayout.addWidget(self.boton_arcode)
        vlayout.addWidget(self.boton_salirCdm)
        self.setLayout(vlayout)
        self.setFixedSize(vlayout.sizeHint())
        
        self.setWindowTitle('Procesamiento de CDM')    
        """
        Acciones
        """
        self.boton_dir.clicked.connect(self.Archivo)
        self.boton_cargar.clicked.connect(self.Carga_CDM)
        self.boton_arcode.clicked.connect(self.procesa_arcode)
        self.boton_salirCdm.clicked.connect(self.salirCdm)      
#         TCAc,mod_dif,poc=evaluaEncuentro(self.TCA,self.sat_idc,self.deb_idc,Cd,Cm)
#         TCAstr=datetime.strftime(TCAc,'%Y-%m-%d %H:%M:%S.%f')
#         mod_dif=int(mod_dif*1000.0)
#         # set data self.TCA, self.MISS_DISTANCE,self.POC

    def Archivo(self):    
        self.cdm_xml=QFileDialog.getOpenFileName(self, 'Seleccione el CDM a Procesar', "../CDM/archivos/*")
        self.cdm_nombre=str(self.cdm_xml).split('/')[-1]
        self.archivo_tex.setText(self.cdm_nombre)
        
        
    def Carga_CDM(self):
#        self.cdm_nombre='cdmTerraPegasus10.xml' # seteo el archivo para las pruebas
        self.CDM=CDM(self.cdm_nombre)
        self.TCA=self.CDM.TCA
        self.MISS_DISTANCE=self.CDM.MISS_DISTANCE
        self.POC=self.CDM.POC
        self.mision_name=self.CDM.mision_name
        self.noradID_mision=self.CDM.noradID_mision
        self.r_sat=self.CDM.r_sat
        self.v_sat=self.CDM.v_sat
        self.deb_name=self.CDM.deb_name
        self.noradID_deb=self.CDM.noradID_deb
        self.r_deb=self.CDM.r_deb
        self.v_deb=self.CDM.v_deb
        # Posiciones Relativas.
        self.dr=float(self.CDM.dr)/1000.0
        self.ds=float(self.CDM.ds)/1000.0
        self.dw=float(self.CDM.dw)/1000.0
        self.rsw_vect=[self.dr,self.ds,self.dw]
        # Ma. Covarianza - objeto 1
        self.cr_r_1=float(self.CDM.cr_r_1)*(0.001*0.001)
        self.ct_r_1=float(self.CDM.ct_r_1)*(0.001*0.001)
        self.ct_t_1=float(self.CDM.ct_t_1)*(0.001*0.001)
        self.cn_r_1=float(self.CDM.cn_r_1)*(0.001*0.001)
        self.cn_t_1=float(self.CDM.cn_t_1)*(0.001*0.001)
        self.cn_n_1=float(self.CDM.cn_n_1)*(0.001*0.001) 
        self.cov_rtn_1=np.array([[self.cr_r_1,self.ct_r_1,self.cn_r_1],[self.ct_r_1,self.ct_t_1,self.cn_t_1],[self.cn_r_1,self.cn_t_1,self.cn_n_1]])
        # Ma. Covarianza - objeto 2
        self.cr_r_2=float(self.CDM.cr_r_2)*(0.001*0.001)
        self.ct_r_2=float(self.CDM.ct_r_2)*(0.001*0.001)
        self.ct_t_2=float(self.CDM.ct_t_2)*(0.001*0.001)
        self.cn_r_2=float(self.CDM.cn_r_2)*(0.001*0.001)
        self.cn_t_2=float(self.CDM.cn_t_2)*(0.001*0.001)
        self.cn_n_2=float(self.CDM.cn_n_2)*(0.001*0.001) 
        self.cov_rtn_2=np.array([[self.cr_r_2,self.ct_r_2,self.cn_r_2],[self.ct_r_2,self.ct_t_2,self.cn_t_2],[self.cn_r_2,self.cn_t_2,self.cn_n_2]])     
        print'**********************'
        print 'r_sat = ',self.r_sat
        print 'v_sat = ',self.v_sat
        print 'r_deb = ',self.r_deb
        print 'v_deb = ',self.v_deb
        print '======================'
        print '------Posiciones Rel--'
        print '======================'
        print self.dr,self.ds,self.dw
        print '*********************'
        print self.cr_r_1
        print self.ct_r_1,self.ct_t_1
        print self.cn_r_1,self.cn_t_1,self.cn_n_1        
        #Calculo el angulo entre los vectores velocidad.
        cos_phi=np.dot(self.v_sat,self.v_deb)/(np.sqrt(np.dot(self.v_sat,self.v_sat))*np.sqrt(np.dot(self.v_deb,self.v_deb)))
        phi=np.arccos(cos_phi) 
    
        #Validacion del calculo POC a partir de datos CDM.
        mu_x,mu_y,sig2_xc,sig2_yc=proyecta_plano_de_encuentro(self.rsw_vect,self.cov_rtn_1,phi)
        poc, poc_int=calcula_Poc_manual(mu_x, mu_y, sig2_xc, sig2_yc)
        print '======================'
        print '------POC-------------'
        print '======================'
        print poc, poc_int[0]
        """
        Carga de Informacion 
        """
        self.noradId_obj1.setText(self.noradID_mision)
        self.noradId_obj2.setText(self.noradID_deb)
        # Cargar la tabla
        self.tablePOC.setItem(0,0, QTableWidgetItem(self.TCA))
        self.tablePOC.setItem(0,1, QTableWidgetItem(self.MISS_DISTANCE))
        self.tablePOC.setItem(0,2, QTableWidgetItem(self.POC))
        self.tablePOC.setItem(1,0, QTableWidgetItem('---'))        
        self.tablePOC.setItem(1,1, QTableWidgetItem('---'))       
        self.tablePOC.setItem(1,2, QTableWidgetItem(str(round(poc_int[0],10))))
        #------------------------
        # Cargar Matrices
        #------------------------
        # OBJ 1
        self.tablesatelite.setItem(0,0,QTableWidgetItem(str(self.cr_r_1)))
        self.tablesatelite.setItem(1,0,QTableWidgetItem(str(self.ct_r_1)))
        self.tablesatelite.setItem(1,1,QTableWidgetItem(str(self.ct_t_1)))
        self.tablesatelite.setItem(2,0,QTableWidgetItem(str(self.cn_r_1)))
        self.tablesatelite.setItem(2,1,QTableWidgetItem(str(self.cn_t_1)))
        self.tablesatelite.setItem(2,2,QTableWidgetItem(str(self.cn_n_1)))
        # OBJ 2
        self.tabledesecho.setItem(0,0,QTableWidgetItem(str(self.cr_r_2)))
        self.tabledesecho.setItem(1,0,QTableWidgetItem(str(self.ct_r_2)))
        self.tabledesecho.setItem(1,1,QTableWidgetItem(str(self.ct_t_2)))
        self.tabledesecho.setItem(2,0,QTableWidgetItem(str(self.cn_r_2)))
        self.tabledesecho.setItem(2,1,QTableWidgetItem(str(self.cn_t_2)))
        self.tabledesecho.setItem(2,2,QTableWidgetItem(str(self.cn_n_2)))      

        print 'FIN DE LA CARGA'
    
    def procesa_arcode(self):
        ventana2=ProcEncuentro(norad_sat=self.noradID_mision,norad_deb=self.noradID_deb,TCA=self.TCA)
        self.central_widget.addWidget(ventana2)
        self.central_widget.setCurrentWidget(ventana2)   
    
    def salirCdm(self):
        self.close()
        
class ProcEncuentro(QWidget):
 #   def __init__(self,parent=None):
    def __init__(self, **kwargs):
        QWidget.__init__(self)

        self.setWindowModality(Qt.ApplicationModal)      
        # Parametros
        if not bool(kwargs):
            self.sat_id="25415"
            self.deb_id="31445"
            self.qdate= QDate(2013,03,18)
            self.qhora=QTime(14,44,34.0)
        else:            
            self.sat_id=kwargs["norad_sat"]
            self.deb_id=kwargs["norad_deb"]
            self.tca=kwargs["TCA"]
            self.qdate= QDate(2013,03,18)
            self.qhora=QTime(14,44,34.0)
            self.hit_rad='0.01'
            self.min_dist=None
            self.tca_calc=None 
            self.ma_comb=None 
            self.maCovar_sat=None
            self.maCovar_deb=None  
            self.propagacion_errores=[]   
        self.initUI()
        
    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.white)
        self.setPalette(self.palette)  
        """
        Group Boxes
        """     
        gbox_evento      = QGroupBox('&Cargar EVENTO')
        gbox_poc_config  = QGroupBox('&Configurar Procesamiento')
        gbox_resultados  = QGroupBox('&Resultados')
        gbox_satMa         = QGroupBox('&Satelite MaCovar')    
        gbox_debMa         = QGroupBox('&Desecho  MaCovar')  
        """
        Etiquetas
        """
        self.sat_lab  = QLabel('Satelite NORAD ID')
        self.deb_lab  = QLabel('Desecho NORAD ID')
        self.time_lab = QLabel('TCA')

        # imagen 
        self.track = QLabel() 
        self.dif   = QLabel()
        """
        Botones
        """
        self.boton_encuetro = QPushButton('Procesar Encuentro')
#        self.boton_dif      = QPushButton('Ver diferencias')
        self.boton_track    = QPushButton('Track')
        btn_errores         = QPushButton('Analizar Errores')
        self.boton_salir    = QPushButton('Salir')
        """
        Campos de Edicion
        """
        self.sat_id_text = QLineEdit()
        self.sat_id_text.setText(str(self.sat_id))
        self.deb_id_text = QLineEdit() 
        self.deb_id_text.setText(str(self.deb_id))
        # calendario
        # nice widget for editing the date  
        self.tca_text    = QDateEdit()  
        self.tca_text.setDate(self.qdate)
        self.tca_text.setCalendarPopup(True)
        """
        Otros
        """
        self.tableEncuentro   = QTableWidget()
        self.tableEncuentro.setRowCount(1)
        self.tableEncuentro.setColumnCount(3)
        listaLabels=['TCA','MinD [km]','PoC']
        self.tableEncuentro.setHorizontalHeaderLabels(listaLabels)
        header = self.tableEncuentro.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch) 
        width = self.tableEncuentro.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)    
#       # Fecha y Hora
        self.hora = QTimeEdit()
        self.hora.setDisplayFormat("HH:mm:ss.zzz")
        self.hora.setTime(self.qhora)
        """
        Plantilla
        """
        #####
        # Gbox - Evento
        layGrid_evento = QGridLayout()
        layGrid_evento.addWidget(self.sat_lab,2,1)
        layGrid_evento.addWidget(self.sat_id_text,2,2)
        layGrid_evento.addWidget(self.deb_lab,3,1)
        layGrid_evento.addWidget(self.deb_id_text,3,2)
        layGrid_evento.addWidget(self.time_lab,4,1)
        layGrid_evento.addWidget(self.tca_text,4,2)
        layGrid_evento.addWidget(self.tca_text,4,2)
        layGrid_evento.addWidget(self.hora,5,2) 
        gbox_evento.setLayout(layGrid_evento)
        # Gbox - Configuracion PoC
        layH_config = QHBoxLayout()
        lab_metodo     = QLabel('METODO')
        lab_hitradio   = QLabel('HR (hitradius) [km]')
        self.le_hitradio    = QLineEdit()
        cbox_metodos   = QComboBox()
        metodos_list   = ['Lei-Chen','Akella','Max Poc']
        cbox_metodos.addItems(metodos_list)
        layH_config.addWidget(lab_metodo)
        layH_config.addWidget(cbox_metodos)
        layH_config.addWidget(lab_hitradio)
        layH_config.addWidget(self.le_hitradio)
        gbox_poc_config.setLayout(layH_config)
        # Gbox - Resultados
        layH_resultados = QHBoxLayout()
        layH_resultados.addWidget(self.tableEncuentro)
        gbox_resultados.setLayout(layH_resultados)
        self.setFixedSize(layH_resultados.sizeHint())
        #--------------------
        # MATRICES
        #--------------------
        # Ma. del satelite
        self.tablesatelite   = QTableWidget()
        self.tablesatelite.setRowCount(3)
        self.tablesatelite.setColumnCount(3)
        listaLabels=['Radial','Transverse','Normal']
        header = self.tablesatelite.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        width = self.tablesatelite.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)
        self.tablesatelite.setHorizontalHeaderLabels(listaLabels)
        # Ma. del desecho
        self.tabledesecho   = QTableWidget()
        self.tabledesecho.setRowCount(3)
        self.tabledesecho.setColumnCount(3)
        listaLabels=['Radial','Transverse','Normal']
        header = self.tabledesecho.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        width = self.tabledesecho.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)
        self.tabledesecho.setHorizontalHeaderLabels(listaLabels) 
        
        # GBOX matriz del satelite
        layH_masat = QHBoxLayout()
        layH_masat.addWidget(self.tablesatelite)
        gbox_satMa.setLayout(layH_masat)   
        # GBOX matriz del satelite
        layH_madeb = QHBoxLayout()
        layH_madeb.addWidget(self.tabledesecho)
        gbox_debMa.setLayout(layH_madeb)

        # Layout Matrices
        layH_matrices = QHBoxLayout()
        layH_matrices.addWidget(gbox_satMa)
        layH_matrices.addWidget(gbox_debMa)
        
        # Layout Principal
        layV_principal = QVBoxLayout()
        layV_principal.addWidget(gbox_evento)  
        layV_principal.addWidget(gbox_poc_config)
        layV_principal.addWidget(self.boton_encuetro)
        layV_principal.addWidget(gbox_resultados)
        layV_principal.addLayout(layH_matrices)
        layV_principal.addWidget(btn_errores)
        layV_principal.addWidget(self.boton_salir)
     
#         grid.addWidget(self.progress,10,1)
#         grid.addWidget(self.track,2,4,5,3)
#         grid.addWidget(self.dif,12,4)
#         grid.addWidget(self.boton_dif,12,10)
#         grid.addWidget(self.boton_track,13,10)

        """
        Acciones
        """
        self.boton_encuetro.clicked.connect(self.procesoSimple)
        btn_errores.clicked.connect(self.analizar_errores)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_track.clicked.connect(self.mostrarTrack)
#        self.boton_dif.clicked.connect(self.mostrarDif)
        self.boton_track.setEnabled(False)
#        self.boton_dif.setEnabled(False)

        self.setLayout(layV_principal)
        self.setFixedSize(layV_principal.sizeHint())
        self.setWindowTitle('Procesamiento con ARxCODE')    
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

        self.cal = self.tca_text.calendarWidget()
        self.fecha = self.cal.selectedDate().toPyDate()
        self.horas = self.hora.time()
        self.tca = QDateTime(self.fecha,self.horas).toPyDateTime()

#         # Importar los TLE de NORAD.    
        self.sat_id=str(self.sat_id_text.text())
        self.deb_id=str(self.deb_id_text.text())

        tle_sat=Tle.creadoxParam(self.sat_id, self.tca)
        tle_deb=Tle.creadoxParam(self.deb_id, self.tca)
#         
        """
        Propagacion hasta el Encuentro
        """
        self.n=3
        self.hit_rad=float(self.le_hitradio.text())
        encuentro1=Encuentro(tle_sat,tle_deb,self.tca,self.hit_rad,self.n)
        self.min_dist= encuentro1.mod_minDist
        self.tca_calc= encuentro1.tca_c
        self.ma_comb, self.maCovar_sat, self.maCovar_deb= encuentro1.calculaMacombinada()
        self.poc_arx, self.poc_int=encuentro1.calculaPoC_circ()
        self.tableEncuentro.setItem(0,0, QTableWidgetItem(datetime.strftime(self.tca_calc,'%Y-%m-%d %H:%M:%S')))
        self.tableEncuentro.setItem(0,1, QTableWidgetItem(str(round(self.min_dist,6))))
        self.tableEncuentro.setItem(0,2, QTableWidgetItem(str(round(self.poc_arx,8))))
        # formato de tabla
#         header = self.tableEncuentro.horizontalHeader()
#         header.setResizeMode(0,QHeaderView.ResizeToContents)
#         header.setResizeMode(1,QHeaderView.ResizeToContents)
#         header.setResizeMode(2,QHeaderView.ResizeToContents)
#         header.setResizeMode(3,QHeaderView.ResizeToContents)
        # archivo de diferencias.
        self.archivo_dif=encuentro1.archivo_dif
        print 'Minima Distancia = ', encuentro1.mod_minDist,encuentro1.epoca_ini
#        grafica_track('../Encuentro/archivos/'+str(self.sat_id)+'U', '../Encuentro/archivos/'+str(self.deb_id)+'U')
#        print 'fin del procesamiento.'
       
        self.boton_track.setEnabled(True)
#        self.boton_dif.setEnabled(True)

        # Tablas de Satelite y de Desecho
        self.tablesatelite.setItem(0,0,QTableWidgetItem(str(round(self.maCovar_sat[0][0],4))))
        self.tablesatelite.setItem(0,1,QTableWidgetItem(str(round(self.maCovar_sat[0][1],4))))
        self.tablesatelite.setItem(0,2,QTableWidgetItem(str(round(self.maCovar_sat[0][2],4))))
        self.tablesatelite.setItem(1,1,QTableWidgetItem(str(round(self.maCovar_sat[1][1],4))))
        self.tablesatelite.setItem(1,2,QTableWidgetItem(str(round(self.maCovar_sat[1][2],4))))
        self.tablesatelite.setItem(2,2,QTableWidgetItem(str(round(self.maCovar_sat[2][2],4))))
        #--------------------
        self.tabledesecho.setItem(0,0,QTableWidgetItem(str(round(self.maCovar_deb[0][0],4))))
        self.tabledesecho.setItem(0,1,QTableWidgetItem(str(round(self.maCovar_deb[0][1],4))))
        self.tabledesecho.setItem(0,2,QTableWidgetItem(str(round(self.maCovar_deb[0][2],4))))
        self.tabledesecho.setItem(1,1,QTableWidgetItem(str(round(self.maCovar_deb[1][1],4))))
        self.tabledesecho.setItem(1,2,QTableWidgetItem(str(round(self.maCovar_deb[1][2],4))))
        self.tabledesecho.setItem(2,2,QTableWidgetItem(str(round(self.maCovar_deb[2][2],4))))

    def mostrarDif(self):
        self.grafico_dif= ploteos.grafica_diferenciasRIC(self.archivo_dif)
        self.pixmap1 = QPixmap(self.grafico_dif)
        self.dif.setPixmap(self.pixmap1)
    
    def mostrarTrack(self):
        self.track_graf = QPixmap('../visual/archivos/ploteo_track.ps')
        self.track.setPixmap( self.track_graf)
        
    def analizar_errores(self):
        """
        DATA SET
        data_set[0] : satelite norad id
        data_set[1] : desecho norad id
        data_set[2] : minima distancia
        data_set[3] : PoC
        data_set[4] : Matriz del satelite
        data_set[5] : Matriz del desecho
        data_set[6] : vector de errores (n dias, sigmas)
        """
        
        data_set=[self.sat_id_text,self.deb_id_text,self.min_dist,self.poc_arx,self.ma_comb, self.ma_comb,self.propagacion_errores]
        ventana3=Errores(data_set)
        ventana3.exec_()
        
    def salir(self):
        self.close() 
    
    
class Errores(QDialog):
    def __init__(self, data_set, parent=None):
        super(Errores, self).__init__(parent)
        """
        DATA SET
        data_set[0] : satelite norad id
        data_set[1] : desecho norad id
        data_set[2] : minima distancia
        data_set[3] : PoC
        data_set[4] : Matriz del satelite
        data_set[5] : Matriz del desecho
        data_set[6] : vector de errores (n dias, sigmas)
        """
        self.satId   =data_set[0]
        self.debId   =data_set[1]
        self.minDist =data_set[2]
        self.poc     =data_set[3]
        self.maSat   =data_set[4]
        self.maDeb   =data_set[5]
        self.propag  =data_set[6]

        self.initUI()
        
    def initUI(self):
        
        # group boxes
        gbox_sitRiesgo = QGroupBox('&Situacion de Riesgo') 
        gbox_satMa     = QGroupBox('&Satelite MaCovar')    
        gbox_debMa     = QGroupBox('&Desecho  MaCovar') 
        gbox_prop      = QGroupBox('&Propagacion de Errores')      
        
        # Satellite Data
        self.sat_id         = QLabel('SATELITE')
        self.noradSAT_text  = QLineEdit(self.satId)
        self.deb_id         = QLabel('DESECHO')
        self.noradDEB_text  = QLineEdit(self.debId)
        self.min_dist       = QLabel('Min. Dist [m]')
        self.mindist_text   = QLineEdit(self.minDist)
        self.min_dist_r     = QLabel('Dist. radial')
        self.rdist_text     = QLineEdit('1200')
        self.lbl_poc        = QLabel('PoC')
        self.poc_text       = QLineEdit(self.poc)
        self.btn_salir      = QPushButton('Salir')
        
        # GBOX Situacion de Riesgo
        layG_sitRiesgo  = QGridLayout()
        layG_sitRiesgo.addWidget(self.sat_id,1,1)
        layG_sitRiesgo.addWidget(self.noradSAT_text,1,2)
        layG_sitRiesgo.addWidget(self.min_dist,1,3)
        layG_sitRiesgo.addWidget(self.mindist_text,1,4)
        layG_sitRiesgo.addWidget(self.deb_id,2,1)
        layG_sitRiesgo.addWidget(self.noradDEB_text,2,2)
        layG_sitRiesgo.addWidget(self.lbl_poc,2,3)
        layG_sitRiesgo.addWidget(self.poc_text,2,4)
        gbox_sitRiesgo.setLayout(layG_sitRiesgo)
        
        # Ma. del satelite
        self.tablesatelite   = QTableWidget()
        self.tablesatelite.setRowCount(3)
        self.tablesatelite.setColumnCount(3)
        listaLabels=['Radial','Transverse','Normal']
        header = self.tablesatelite.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        width = self.tablesatelite.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)
        self.tablesatelite.setHorizontalHeaderLabels(listaLabels)
        self.tablesatelite.setItem(0,0, QTableWidgetItem(str(3)))
        # Ma. del desecho
        self.tabledesecho   = QTableWidget()
        self.tabledesecho.setRowCount(3)
        self.tabledesecho.setColumnCount(3)
        listaLabels=['Radial','Transverse','Normal']
        header = self.tabledesecho.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)
        width = self.tabledesecho.verticalHeader()
        width.setResizeMode(QHeaderView.Stretch)
        self.tabledesecho.setHorizontalHeaderLabels(listaLabels)  
        
        
        # GBOX matriz del satelite
        layH_masat = QHBoxLayout()
        layH_masat.addWidget(self.tablesatelite)
        gbox_satMa.setLayout(layH_masat)   
        # GBOX matriz del satelite
        layH_madeb = QHBoxLayout()
        layH_madeb.addWidget(self.tabledesecho)
        gbox_debMa.setLayout(layH_madeb)

        # Layout Matrices
        layH_matrices = QHBoxLayout()
        layH_matrices.addWidget(gbox_satMa)
        layH_matrices.addWidget(gbox_debMa)
        
        # GBOX propagacion de errores
        layG_errores = QGridLayout()
        lab_prop     = QLabel('Tiempo propagado [dias]')
        le_prop      = QLineEdit()
        lab_sigx     = QLabel('Sigma2 X')
        le_sigx      = QLineEdit()
        lab_sigy     = QLabel('Sigma2 Y')
        le_sigy      = QLineEdit()
        lab_sigz     = QLabel('Sigma2 Z')
        le_sigz      = QLineEdit()
        layG_errores.addWidget(lab_prop,1,1)
        layG_errores.addWidget(le_prop,1,2)
        layG_errores.addWidget(lab_sigx,2,1)
        layG_errores.addWidget(le_sigx,2,2)
        layG_errores.addWidget(lab_sigy,2,3)
        layG_errores.addWidget(le_sigy,2,4)
        layG_errores.addWidget(lab_sigz,2,5)
        layG_errores.addWidget(le_sigz,2,6)
        gbox_prop.setLayout(layG_errores)       

        # Layout Principal
        layV_principal = QVBoxLayout()
        layV_principal.addWidget(gbox_sitRiesgo)
        layV_principal.addLayout(layH_matrices)
        layV_principal.addWidget(gbox_prop)
        layV_principal.addWidget(self.btn_salir)
        self.setLayout(layV_principal)
        
        self.btn_salir.clicked.connect(self.salir)

        self.setWindowTitle('Analisis de Errores')
        
    def salir(self):
        self.accept()
        
# class ProcTle(QDialog):
# 
#     def __init__(self,parent=None):
#         QDialog.__init__(self,parent)
# 
#         self.setWindowModality(Qt.ApplicationModal)
#         self.initUI()
# 
#         self.filename = ''
#         self.sat_id='99999'
#         self.fini=''
#         self.ffin=''
#         self.fin_tle=datetime(1957,1,1,0,0,0)
#         self.ini_tle=datetime(1957,1,1,0,0,0)
#         self.tles=0
#         self.tleOrdenados={}
#         self.data=[]
#         self.coef=[]
#         self.path='../AjustarTLE/diferencias/'
#         self.diferencias=''
#         self.set_data=[]
#         self.set_pri=[]
#         self.arch_macovar=''
#         self.macovarT=''  
#         self.cantxbin=[]
#         self.mediaxbin=[]      
#         
#     def initUI(self):
#         self.palette = QPalette()
#         self.palette.setColor(QPalette.Background,Qt.white)
#         self.setPalette(self.palette)
#         
#         """
#         Etiquetas
#         """
#         self.carga           = QLabel('CARGADO DE TLEs')
#         self.norad           = QLabel('A partir de NORAD')  
#         self.equipo          = QLabel('Desde el Equipo')
#         self.arch_prepro     = QLabel('Archivo a Procesar: ')
#         self.sat_id_label    = QLabel('NORAD_ID')
#         self.cant_tles       = QLabel('Cantidad de TLEs')
#         self.tle_pri         = QLabel('Ultimo TLE del set.')
#         self.outputs         = QLabel('Output')
#         self.ma_covar_label  = QLabel('Ma. de COVARIANZA')
#         """
#         Botones
#         """
#         self.boton_norad        = QPushButton('Space-Track')
#         self.boton_equipo       = QPushButton('Directorios')
#         self.boton_procesa      = QPushButton('PROCESAR')
#         self.boton_dtotales     = QPushButton('Graficar Diferencias Totales')
#         self.boton_dxcoord      = QPushButton('Graficar Diferencias por Coordenadas')
#         self.boton_dsetprimario = QPushButton ('Graficar Diferencias del Set primario')
#         self.boton_salir        = QPushButton('Salir')
#         """
#         Campos de Edicion
#         """
#         self.arch_cargado       = QLineEdit()
#         self.sat_id_line        = QLineEdit()
#         self.cant_tles_edit     = QLineEdit()
#         self.matriz             = QLineEdit()
#         self.estado_proc_edit   = QLineEdit()
#         """
#         OTROS
#         """
#         self.tle_pri_edit    = QTextEdit()
#         self.tableView       = QTableWidget()
#         """
#         Plantilla
#         """
#         grid = QGridLayout()
#         grid.setSpacing(5)
#         
#         grid.addWidget(self.carga,2,0)
#         grid.addWidget(self.norad,3,0)
#         grid.addWidget(self.boton_norad,3,1)
#         grid.addWidget(self.equipo,4,0)
#         grid.addWidget(self.boton_equipo,4,1)
#         grid.addWidget(self.arch_prepro,5,0)
#         grid.addWidget(self.arch_cargado,5,1)
#         grid.addWidget(self.boton_procesa,5,2)
#         grid.addWidget(self.sat_id_label,7,0)
#         grid.addWidget(self.sat_id_line,7,1)
#         grid.addWidget(self.cant_tles,8,0)
#         grid.addWidget(self.cant_tles_edit,8,1)        
#         grid.addWidget(self.tle_pri,9,0)
#         grid.addWidget(self.tle_pri_edit,10,0,1,4)
#         grid.addWidget(self.ma_covar_label,11,0) 
#         grid.addWidget(self.tableView,12,0)
#         grid.addWidget(self.outputs,23,1)
#         grid.addWidget(self.estado_proc_edit,23,2)
#         grid.addWidget(self.boton_dsetprimario,24,2)
#         grid.addWidget(self.boton_salir,25,2)
# #         grid.addWidget(self.boton_dtotales,25,1)
# #         grid.addWidget(self.boton_dxcoord,25,2)
#         
#         """
#         Acciones
#         """
#         self.boton_procesa.setEnabled(False)
#         self.boton_norad.clicked.connect(self.botonNorad)
#         self.boton_equipo.clicked.connect(self.Archivo)
#         self.boton_salir.clicked.connect(self.salir)
#         self.boton_procesa.clicked.connect(self.procesar)
#         self.boton_dsetprimario.clicked.connect(self.ver_dif_set_primario)
# #         self.boton_dxcoord.clicked.connect(self.ver_dif_x_coordenadas)
# #         self.boton_dtotales.clicked.connect(self.ver_diferencias_totales)
#         self.setLayout(grid)
#         self.setWindowTitle('Procesamiento de TLE')    
#         self.show()
#           
#     def botonNorad(self):
#         print ("Procesando la Conexion con NORAD para la Descarga...")
#         self.w = ConexionNorad()
#         self.w.exec_()
#         self.sat_id, self.fini, self.ffin, self.filename = self.w.iniciaSolicitud()
#         self.arch_cargado.setText(self.filename)
#         self.sat_id_line.setText(self.sat_id) 
#         self.boton_procesa.setEnabled(True) 
#         
#     def Archivo(self):    
#         fname=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../TleAdmin/crudosTLE/*")
#         nombre=str(fname).split('/')[-1]
#         self.filename = nombre
#         self.sat_id = nombre.split('_')[0]
#         self.arch_cargado.setText(self.filename)
#         self.boton_procesa.setEnabled(True)
#         
#     
#     def procesar(self):
#         """
#         Invoca a la funcion divide_setTLE, para fragmentar
#         cada uno de los TLE del dato crudo en archivos
#         individuales; y los guarda en: TleAdmin/tle
#         """
#         files=glob.glob('../TleAdmin/tle/*')
#         for filename in files:
#             os.unlink(filename)
#         if os.stat('../TleAdmin/crudosTLE/'+self.filename).st_size == 0:
#             print('El archivo esta vacio')
#         divide_setTLE(self.sat_id, self.filename)
#         self.sat_id_line.setText(self.sat_id)
#         self.lista=glob.glob('../TleAdmin/tle/*')
#         self.tles=len(self.lista)
#         self.cant_tles_edit.setText(str(self.tles))
#         """
#         Ordenamiento de los TLEs
#         """
#         self.tledic=generadorDatos(self.lista)
#         self.tleOrdenados=ordenaTles(self.tledic)
# 
#         """
#         Impresiones de info de TLEs.
#         """
#         print 'PROCESAMIENTO DE TLE'
#         print '-----------------------------------------------------'
#         print 'TLE PRIMARIO'
#         print '-----------------------------------------------------'
#         tle_primario = Tle.creadoxArchivo('../TleAdmin/tle/'+self.tleOrdenados[-1][0])
#         linea1= tle_primario.linea1
#         linea2= tle_primario.linea2
#         self.fin_tle=tle_primario.epoca()
#         self.ffin=self.fin_tle.strftime('%Y-%m-%d %H:%M:%S.%f' )
#         self.tle_pri_edit.setText(linea1+'\n'+linea2)
#         print linea1
#         print linea2
#         print '-----------------------------------------------------'
#         print 'TLE INICIAL DEL SET'
#         print '-----------------------------------------------------'
#         tle_inial = Tle.creadoxArchivo('../TleAdmin/tle/'+self.tleOrdenados[0][0])
#         linea1_0= tle_inial.linea1
#         linea2_0= tle_inial.linea2
#         self.ini_tle=tle_inial.epoca()
#         print linea1_0
#         print linea2_0
#         print '-----------------------------------------------------'
#         
#         """
#         PROCESAMIENTO.
#         """
#         files=glob.glob('../AjustarTLE/diferencias/*')
#         for filename in files:
#             os.unlink(filename)
# #        self.bin, self.data, self.set_pri, self.coef=difTle(self.tleOrdenados, self.tles)
#         self.set_pri=difPrimario()
#         self.dt=self.set_pri[0]
#         self.data1=self.set_pri[1]
#         self.coef=self.set_pri[2]
#         self.nombre_archivo=self.set_pri[3]
# #         self.cantxbin,self.mediaxbin=genera_estadisticaBin(self.bin)
# #         self.diferencias=difPrimario(self.nombre_archivo,self.tles-1)
#         self.estado_proc_edit.setText(self.nombre_archivo)
# 
#         """
#         Ma. de Covarianza
#         """
#         self.macovarT, self.arch_macovar=EjecutaMaCovar(self.nombre_archivo)
#         self.tableView.setRowCount(len(self.macovarT))
#         self.tableView.setColumnCount(len(self.macovarT))
#         for i,fila in enumerate(self.macovarT):
#             for j,col in enumerate(fila):
#                 self.tableView.setItem(i,j,QTableWidgetItem(str(col)))    
#         
#         print 'Fin del Procesamiento'
#         
# #     def ver_dif_x_coordenadas(self):
# #         ploteos.grafica_setcompleto(self.sat_id,self.path,self.data1, self.coef)
# #      
# #     def ver_diferencias_totales(self):
# #         ploteos.grafica_diferenciasTotales(self.sat_id,self.path,self.data1,self.coef) 
#         
#     def ver_dif_set_primario(self):
#         ploteos.grafica_set_principal(self.sat_id,self.path, self.data1,self.coef)
#         
# #     def Graficar(self):
# # #        data=[self.sat_id,self.diferencias,self.cantxbin, self.mediaxbin]
# #         data=[self.sat_id,self.diferencias]
# #         self.graf = RepresentacionGrafica(data)
# #         self.graf.exec_()
#         
#     def ver_mediasxbin(self):
#         desviacion_standard_graf(self.sat_id, self.mediaxbin[0], self.mediaxbin[1], self.mediaxbin[2])
# 
# #     def Macovar(self):
# #         self.macovarT, self.arch_macovar=EjecutaMaCovar(self.diferencias)
# #         self.tableView.setRowCount(len(self.macovarT))
# #         self.tableView.setColumnCount(len(self.macovarT))
# #         for i,fila in enumerate(self.macovarT):
# #             for j,col in enumerate(fila):
# #                 self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
# #         self.arch_macovar_edit.setText(self.arch_macovar)        
#     
#     def salir(self):
#         self.accept()

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
#        self.tle=importarSetTLE(self.usu1,self.passw1,self.cat_id,self.pydate,self.pydate1,self.nombreTle.text())
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
    QApplication.setStyle("windows") # plastique, cde, motif, sgi, windows, cleanlooks, mac
    app = QApplication(sys.argv)
    ex = ProcARxCODE()
    sys.exit(app.exec_())
