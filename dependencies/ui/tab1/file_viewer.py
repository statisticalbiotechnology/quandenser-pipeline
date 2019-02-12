import sys
from PySide2.QtWidgets import QLineEdit
from PySide2.QtGui import QColor
import os

class file_viewer(QLineEdit):
    def __init__(self, type='file', id=0):
        super(file_viewer,self).__init__(parent = None)
        self.type = type
        self.id = id
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        all_txt = self.text()  # Copy, dont use
        self.clear()
        self.pick_color(all_txt)
        self.blockSignals(False)

    def pick_color(self, txt):
        if self.type == 'file':
            if os.path.isfile(txt) and txt.split('.')[-1] in ["Fasta", "fasta", "FASTA"]:
                self.setStyleSheet("color: rgb(0, 255, 150);") # Check if path
                self.setText(txt)
            else:
                self.setStyleSheet("color: red;") # Check if path
                self.setText(txt)
        elif self.type == 'directory':
            if os.path.isdir(txt):
                self.setStyleSheet("color: rgb(0, 255, 150);") # Check if path
                self.setText(txt)
            else:
                self.setStyleSheet("color: red;") # Check if path
                self.setText(txt)
