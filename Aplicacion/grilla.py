'''
Created on Feb 5, 2017

@author: mcvalenti
'''
import sys, glob, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from TleAdmin.TleArchivos import setTLE
from TleAdmin.get_tle import importar_tle
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle, difPrimario
from Estadistica.maCovar import EjecutaMaCovar
from visual.TleOsweiler import VerGrafico
from PyQt4.Qt import QDialog

class ProcARxCODE(QMainWindow):
    
    def __init__(self):
        super(ProcARxCODE, self).__init__()

        extractAction = QAction("Salir", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip('Leave The App')
        extractAction.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractAction)  
        
        self.resize(300, 300)
        self.setWindowTitle('ARxCODE')
        self.home()
    
    def home(self):
        self.CDM_label       = QLabel('No se registran CDM')
        self.boton_ProManual = QPushButton('Procesamiento Manual',self)
        self.boton_ProManual.move(100,100)
        self.boton_ProManual.resize(self.boton_ProManual.minimumSizeHint())
        self.boton_ProManual.clicked.connect(self.AbrirProc)
        self.show()
        
    def close_application(self):
        sys.exit()
        
    def AbrirProc(self):
        ventana2=ProcManual()
        ventana2._exec_()

class ProcManual(QWidget):
    
    def __init__(self):
        super(ProcManual, self).__init__()
        self.filename = ''
        self.sat_id='99999'
        self.tles=0
        self.tleOrdenados={}
        self.diferencias=''
        self.macovarT=''
        self.initUI()
        self.sufijo='dif_'
        
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
        self.estado_proc     = QLabel('Procesando ... ')
        self.ma_covar_label  = QLabel('Ma. de COVARIANZA')
        """
        Botonoes
        """
        self.boton_norad     = QPushButton('Space-Track')
        self.boton_equipo    = QPushButton('Directorios')
        self.boton_prepros   = QPushButton('Preprocesamiento')
        self.boton_procesa   = QPushButton('PROCESAR')
        self.boton_grafica   = QPushButton('Graficar')
        self.boton_salir     = QPushButton('Salir')
        self.boton_ma_covar  = QPushButton('Calcular')
        
        """
        Campos de Edicion
        """
        self.arch_cargado    = QLineEdit()
        self.sat_id_line     = QLineEdit()
        self.cant_tles_edit  = QLineEdit()
        self.matriz          = QLineEdit()
        self.estado_proc_edit= QLineEdit()
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
        grid.addWidget(self.sat_id_line,8,0)
        grid.addWidget(self.cant_tles_edit,8,1)
        grid.addWidget(self.boton_procesa,9,1)
        grid.addWidget(self.boton_grafica,9,2)
        grid.addWidget(self.estado_proc,10,0)
        grid.addWidget(self.estado_proc_edit,10,2)
        grid.addWidget(self.ma_covar_label,11,0)
        grid.addWidget(self.tableView,12,0,6,2)
        grid.addWidget(self.boton_ma_covar,12,2)
       
        grid.addWidget(self.boton_salir,17,2)
        
        """
        Acciones
        """
        self.boton_norad.clicked.connect(self.botonNorad)
        self.boton_equipo.clicked.connect(self.Archivo)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_prepros.clicked.connect(self.PreProc)
        self.boton_procesa.clicked.connect(self.procesar)
        self.boton_grafica.clicked.connect(self.Graficar)
        self.boton_ma_covar.clicked.connect(self.Macovar)
        
        """
        PRUEBA DIALOGO
        """
        btnAbrir = QPushButton("Abrir ventana",None)
        grid.addWidget(btnAbrir,3,2)
        
        self.setLayout(grid)
        self.setWindowTitle('Procesamiento de TLE')    
        self.show()
        
        self.w = ConexionNorad()
                
    def botonNorad(self):
        print "Opening NORAD window..."
        self.w.exec_()
        value1, value2 = self.w.save()
        print('Success!', value1, value2)
        
        #print self.filename
#         self.filename=self.w.archTLE
#         print self.filename
#         self.arch_cargado.setText(self.filename)
        
        
    def Archivo(self):    
        fname=QFileDialog.getOpenFileName(self, 'Seleccione el Archivo a Procesar', "../TleAdmin/crudosTLE/*")
        nombre=str(fname).split('/')[-1]
        self.filename = nombre
        self.sat_id = nombre.split('_')[0]
        self.arch_cargado.setText(self.filename)
        
    def PreProc(self):
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
        Preprocesamiento, ordenamiento de los TLEs
        """
        self.tledic=generadorDatos(self.lista)
        self.tleOrdenados=ordenaTles(self.tledic)
        
    
    def procesar(self):
        files=glob.glob('../AjustarTLE/diferencias/*')
        for filename in files:
            os.unlink(filename)
        difTle(self.tleOrdenados, self.tles)
        self.diferencias=difPrimario(self.filename,self.tles-1)

        self.estado_proc_edit.setText('Finalizado')
        
    def Graficar(self):
        VerGrafico(self.diferencias)
        
    def Macovar(self):
        self.macovarT=EjecutaMaCovar(self.diferencias)
        self.tableView.setRowCount(len(self.macovarT))
        self.tableView.setColumnCount(len(self.macovarT))
        for i,fila in enumerate(self.macovarT):
            for j,col in enumerate(fila):
                self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
    
    def salir(self):
        exit()

class ConexionNorad(QDialog):
#     def __init__(self):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)

        self.setWindowModality(Qt.ApplicationModal)
        self.archTLE=''
        self.eta1=''
        self.eta2=''
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
        self.usuario_edit  = QLineEdit()
        self.clave_edit    = QLineEdit()
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
        self.boton_guardar.clicked.connect(self.save)
        self.setWindowTitle('Conexion con NORAD')
#         
    def iniciaSolicitud(self):
        self.nombreTle.setText(self.nombreTle.text())
        self.usu1   = str(self.usuario_edit.text())
        self.passw1 = str(self.clave_edit.text())
        self.cat_id = str(self.norad_id_edit.text())
        self.tle=importar_tle(self.usu1,self.passw1,self.cat_id,self.pydate,self.pydate1,self.nombreTle.text())
        self.archTLE=self.nombreTle.text()
        print self.archTLE
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
        
    def save(self):
        self.eta1='Maria'
        self.eta2='Cecilia'
        return self.eta1, self.eta2  
        
def IniciaApp():
    QApplication.setStyle("plastique")
    app = QApplication(sys.argv)
    ex = ProcARxCODE()
    sys.exit(app.exec_())


