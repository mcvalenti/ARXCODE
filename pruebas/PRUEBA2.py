'''
Created on 15/03/2017

@author: mcvalenti
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
 
class Example(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initUI()      
 
    def initUI(self):
        self.viewAndTableLayout = QHBoxLayout()
        self.dockView = QDockWidget("View")
        self.grview = QGraphicsView(self.dockView)
        self.dockView.setWidget(self.grview)
        self.viewAndTableLayout.addWidget(self.dockView)
 
        self.dockTable = QDockWidget("Table")
        self.table = QTableView()
        self.dockTable.setWidget(self.table)
        self.viewAndTableLayout.addWidget(self.dockTable)
        self.layout.addLayout(self.viewAndTableLayout)
 
 
        self.listAndTreeLayout = QHBoxLayout()
        self.dockList = QDockWidget("List")
        self.list = QListView()
        self.dockList.setWidget(self.list)
        self.listAndTreeLayout.addWidget(self.dockList)
 
        self.dockTree = QDockWidget("Tree")
        self.tree = QTreeView()
        self.listAndTreeLayout.addWidget(self.dockTree)
        self.layout.addLayout(self.listAndTreeLayout)
 
app = QApplication(sys.argv)
ex = Example()
ex.show()
ex.raise_()
sys.exit(app.exec_())