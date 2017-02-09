'''
Created on Feb 5, 2017

@author: mcvalenti
'''
import sys, glob, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from TleAdmin.TleArchivos import setTLE
from AjustarTLE.AjustarTLE import generadorDatos, ordenaTles, difTle, difPrimario
from Estadistica.maCovar import EjecutaMaCovar

class ProcARxCODE(QWidget):
    
    def __init__(self):
        super(ProcARxCODE, self).__init__()    
        
        self.resize(300, 300)
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.CDM_label       = QLabel('No se registran CDM')
        self.boton_ProManual = QPushButton('Procesamiento Manual')
        
        grid.addWidget(self.CDM_label)
        grid.addWidget(self.boton_ProManual)

        self.boton_ProManual.clicked.connect(self.AbrirProc)
        self.setLayout(grid)
        self.setWindowTitle('ARxCODE')
        self.show()
        
    def AbrirProc(self):
        ventana2=ProcManual()
        ventana2.exec_()


class ProcManual(QDialog):
    
    def __init__(self):
        super(ProcManual, self).__init__()
        
        self.filename = ''
        self.sat_id='99999'
        self.tles=0
        self.tleOrdenados={}
        self.diferencias=''
        self.macovarT=''
        
        self.initUI()
        
        
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
        grid.addWidget(self.estado_proc,10,0)
        grid.addWidget(self.estado_proc_edit,10,2)
        grid.addWidget(self.ma_covar_label,11,0)
        grid.addWidget(self.tableView,11,1)
        grid.addWidget(self.boton_ma_covar,11,2)
       
        grid.addWidget(self.boton_salir,17,2)
        
        """
        Acciones
        """
        self.boton_norad.clicked.connect(self.botonNorad)
        self.boton_equipo.clicked.connect(self.Archivo)
        self.boton_salir.clicked.connect(self.salir)
        self.boton_prepros.clicked.connect(self.PreProc)
        self.boton_procesa.clicked.connect(self.procesar)
        self.boton_ma_covar.clicked.connect(self.Macovar)
        
        self.setLayout(grid)
        self.setWindowTitle('Procesamiento de TLE')    
        self.show()
   
        
    def botonNorad(self):
        frm=ConexionNorad()
        frm.exec_()
        


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
        self.diferencias=difPrimario(self.filename,self.tles)
        self.estado_proc_edit.setText('Finalizado')
        
    def Macovar(self):
        self.macovarT=EjecutaMaCovar(self.diferencias)
        self.tableView.setRowCount(len(self.macovarT))
        self.tableView.setColumnCount(len(self.macovarT))
        for i,fila in enumerate(self.macovarT):
            for j,col in enumerate(fila):
                self.tableView.setItem(i,j,QTableWidgetItem(str(col)))
    
    def salir(self):
        exit()
        
class ConexionNorad(QWidget):
    
    def __init__(self):
        super(ConexionNorad, self).__init__()
        
    def initUI(self):
        self.palette = QPalette()
        self.palette.setColor(QPalette.Background,Qt.blue)
        self.setPalette(self.palette)
        self.resize(200, 500)
        
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        
        """
        Etiquetas
        """
        self.usuario    = QLabel('Usuario: ')
        self.clave      = QLabel('Password: ')
        """
        Botones
        """
        self.boton_cerrar = QPushButton('cerrar')
        """
        Campos de Edicion
        """
        self.usuario_edit = QLineEdit()
        self.clave_edit   = QLineEdit()
        
        """
        Acciones
        """
        self.boton_cerrar.clicked.connect(self.cerrar)
        
        self.grid.addWidget(self.usuario)
        
        
        self.setLayout(self.grid)
        self.setWindowTitle('Conexion con NORAD')    
        self.show()
        
    def cerrar(self):
        self.close()
   
        
        
        
def IniciaApp():
    
    app = QApplication(sys.argv)
    ex = ProcARxCODE()
    sys.exit(app.exec_())


