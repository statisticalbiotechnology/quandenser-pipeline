import sys
from PyQt5.QtWidgets import QLineEdit

class msconvert_arguments(QLineEdit):
    def __init__(self):
        super(QLineEdit,self).__init__(parent = None)
        self.setText('')

    def run(self):
        return self.text()
