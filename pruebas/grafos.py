'''
Created on Mar 1, 2017

@author: mcvalenti
'''
import sys
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class Ui_MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(Ui_MainWindow, self).__init__(parent)

        self.figure = Figure() # don't use matplotlib.pyplot at all!
        self.canvas = FigureCanvas(self.figure)

        # use addToolbar to add toolbars to the main window directly!
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(self.toolbar)

        self.button = QtGui.QPushButton('Plot')
        self.lineEditMomentum1 = QtGui.QLineEdit()
        self.lineEditMomentum1.setMaximumSize(200, 30)

        self.main_widget = QtGui.QWidget(self)
        self.setCentralWidget(self.main_widget)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.lineEditMomentum1)

        self.main_widget.setLayout(layout)

if __name__ == "__main__":
    qApp = QtGui.QApplication(sys.argv)
    main_window = Ui_MainWindow()