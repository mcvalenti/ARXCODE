'''
Created on Feb 5, 2017

@author: mcvalenti
'''
import sys, glob, os, re
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from TleAdmin.TleArchivos import setTLE
from TleAdmin.TLE import Tle
from TleAdmin.get_tle import importar_tle
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle, difPrimario
from Estadistica.maCovar import EjecutaMaCovar, EjecutaMaCovarCODS
from visual.TleOsweiler import VerGrafico
from Comparar.TleVsCods import generaTEME, EjecutaComparacion
from visual.TlevsCodsGraf import VerGraficoMision

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
        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)
                
        self.resize(300, 300)
        self.setWindowTitle('ARxCODE')
        self.home()
    
    def home(self):
        
        self.CDM_label       = QLabel('No se registran CDM')
        self.boton_ProManual = QPushButton('Procesamiento de TLE',self)
        self.boton_mision    = QPushButton('Procesamiento de Datos de Mision',self)
        self.boton_ProManual.move(100,100)
        self.boton_mision.move(100,200)
        self.boton_ProManual.resize(self.boton_ProManual.minimumSizeHint())
        self.boton_mision.resize(self.boton_mision.minimumSizeHint())
        self.boton_ProManual.clicked.connect(self.tleProc)
        self.boton_mision.clicked.connect(self.misProc)
        self.show()
        
    def close_application(self):
        sys.exit()
        
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
#     def __init__(self):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()

        self.filename = ''
        self.sat_id='99999'
        self.tles=0
        self.tleOrdenados={}
        self.diferencias=''
        self.grafico_pw=''
        self.arch_macovar=''
        self.macovarT=''        
        
    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.white)
        self.setPalette(self.palette)
        
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
        self.outputs         = QLabel('Outputs')
        self.ma_covar_label  = QLabel('Ma. de COVARIANZA')
        """
        Botones
        """
        self.boton_norad     = QPushButton('Space-Track')
        self.boton_equipo    = QPushButton('Directorios')
        self.boton_prepros   = QPushButton('Preprocesamiento')
        self.boton_procesa   = QPushButton('PROCESAR')
        self.boton_grafica   = QPushButton('Graficar')
        self.boton_salir     = QPushButton('Salir')
        self.boton_ma_covar  = QPushButton('Calcular Matriz')
        
        """
        Campos de Edicion
        """
        self.arch_cargado       = QLineEdit()
        self.sat_id_line        = QLineEdit()
        self.cant_tles_edit     = QLineEdit()
        self.matriz             = QLineEdit()
        self.estado_proc_edit   = QLineEdit()
        self.arch_grafico_edit  = QLineEdit()
        self.arch_macovar_edit  = QLineEdit()
        """
        OTROS
        """
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
        grid.addWidget(self.boton_grafica,10,2)
        grid.addWidget(self.arch_grafico_edit,10,4)
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
        self.sat_id, self.filename = self.w.datos()
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
        
    
    def procesar(self):
        files=glob.glob('../AjustarTLE/diferencias/*')
        for filename in files:
            os.unlink(filename)
        difTle(self.tleOrdenados, self.tles)
        self.diferencias=difPrimario(self.filename,self.tles-1)
        self.estado_proc_edit.setText(self.diferencias)
        self.boton_grafica.setEnabled(True)
        self.boton_ma_covar.setEnabled(True)
        
    def Graficar(self):
        self_grafico_pw=VerGrafico(self.diferencias)
        self.arch_grafico_edit.setText(self_grafico_pw)
        
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
        self.nombreTle.setText(self.nombreTle.text())
        self.usu1   = str(self.usuario_edit.text())
        self.passw1 = str(self.clave_edit.text())
        self.cat_id = str(self.norad_id_edit.text())
        self.tle=importar_tle(self.usu1,self.passw1,self.cat_id,self.pydate,self.pydate1,self.nombreTle.text())
        self.archTLE=self.nombreTle.text()
#             
    def verFinicio(self):
        self.date = self.cal.selectedDate()
        self.pydate = self.date.toPyDate()
        self.st.setText(self.date.toString())
#         
    def verFfin(self):
        self.date1 = self.cal1.selectedDate()
        self.pydate1 = self.date1.toPyDate()
        self.et.setText(self.date1.toString())
        
    def datos(self):
        return self.cat_id, self.archTLE
    
class ProcMision(QDialog):

    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()
        
        self.sat_id='99999'
        self.sat_nombre=''
        self.crudo_mision=''
        self.tlesTeme=''
        self.dif_cvstle= ''
        self.macovarT=''
        
    def initUI(self):
        self.grilla = QGridLayout()
        self.grilla.setSpacing(2)
        
        """
        Etiquetas
        """
        self.mision_lab     = QLabel('Mision')
        self.ma_lab       = QLabel('Ma. Varianza-Covarianza')
        
        """
        Botones
        """
        self.boton_tle_xyz    = QPushButton('Datos TLE (sist:TEME)')
        self.boton_datos_mis  = QPushButton('Datos de Mision')
        self.boton_dif        = QPushButton('Calcular diferencias')
        self.boton_grafico    = QPushButton('Ver Grafico')
        self.boton_macovar    = QPushButton('Calcular Matriz')
        self.boton_salir      = QPushButton('Salir')
        
        """
        Campos de Edicion
        """
        self.tle_xyz_edit   = QLineEdit()
        self.datos_mis_edit = QLineEdit()
        
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
        self.grilla.addWidget(self.boton_tle_xyz,2,0)
        self.grilla.addWidget(self.tle_xyz_edit ,2,1)
        self.grilla.addWidget(self.boton_datos_mis,3,0)
        self.grilla.addWidget(self.datos_mis_edit,3,1)
        self.grilla.addWidget(self.boton_dif,4,1)
        self.grilla.addWidget(self.boton_grafico,5,1)
        self.grilla.addWidget(self.tableView,6,0,7,1)
        self.grilla.addWidget(self.boton_macovar,7,1)
        self.grilla.addWidget(self.boton_salir,15,1)
        
        """
        Acciones
        """
        self.listaSat.currentIndexChanged.connect(self.selectionchange)
        self.boton_dif.setEnabled(False)
        self.boton_grafico.setEnabled(False)
        self.boton_tle_xyz.clicked.connect(self.tleTeme)
        self.boton_datos_mis.clicked.connect(self.ArchivoCODS)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_dif.clicked.connect(self.calcDif)
        self.boton_grafico.clicked.connect(self.graficar)
        self.boton_macovar.clicked.connect(self.Macovar)
#        self.datos_mis_edit.textChanged.connect(self.validar_nombre)
                
        self.setWindowTitle('PROCESAMIENTO de DATOS CODS')
        self.setLayout(self.grilla) 
        
    def selectionchange(self,i):
        self.sat_nombre= self.listaSat.currentText()
        self.dic_satelites={'SAC-D':37673,'LAGEOS':8820,'ICESAT':27642}
        self.sat_id=self.dic_satelites[str(self.sat_nombre)]
        
    def tleTeme(self):
        tles = glob.glob('../TleAdmin/tle/*')
        self.tlesTeme=generaTEME(tles,self.sat_id) 
        self.tle_xyz_edit.setText(str(self.tlesTeme))
        
    def ArchivoCODS(self):  
        fname1=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../CodsAdmin/TOD_O/*")
        nombre1=str(fname1).split('/')[-1]
        self.crudo_mision = nombre1
        self.datos_mis_edit.setText(self.crudo_mision)
        self.boton_dif.setEnabled(True)
        
#     def validar_nombre(self):
#         nombre = self.nombre.text()
# 
#         if nombre == "":
#             self.nombre.setStyleSheet("border: 1px solid yellow;")
#             return False
        
    def calcDif(self):
        self.dif_cvstle=EjecutaComparacion(self.sat_id,self.tlesTeme,self.crudo_mision)
        self.boton_grafico.setEnabled(True)
        
    def Macovar(self):
        self.macovarT=EjecutaMaCovarCODS(self.dif_cvstle)
        self.tableView.setRowCount(len(self.macovarT))
        self.tableView.setColumnCount(len(self.macovarT))
        for i,fila in enumerate(self.macovarT):
            for j,col in enumerate(fila):
                self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
        
    def graficar(self):
        VerGraficoMision(self.dif_cvstle)
        
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


