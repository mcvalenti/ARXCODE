'''
Created on 17/05/2017

@author: mcvalenti
'''

import sys
from PyQt4.QtGui import *  
from PyQt4.QtCore import * 

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setFixedWidth(800)
        self.setFixedHeight(800)

        self.widget = QWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)
        
        self.widget.setStyleSheet("""
        .QWidget {
            border: 20px solid black;
            border-radius: 10px;
            background-color: rgb(255, 255, 255);
            }
        """)
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())