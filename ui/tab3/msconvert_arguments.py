import sys
from PySide2.QtWidgets import QLineEdit

class msconvert_arguments(QLineEdit):
    def __init__(self):
        super(msconvert_arguments,self).__init__(parent = None)
        self.setText('')

    def run(self):
        return self.text()
