import sys
from PyQt5.QtWidgets import QPushButton, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon

class run_button(QPushButton):

    def __init__(self):
        super(QPushButton,self).__init__(parent = None)
        self.setText('RUN')
        self.clicked.connect(self.run)

    def run(self):
        print("LETS GO")

    def set_size(self, width, height):
        pass
        #self.resize(width, height)
