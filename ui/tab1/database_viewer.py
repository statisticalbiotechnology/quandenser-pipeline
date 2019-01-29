import sys
from PySide2.QtWidgets import QLineEdit
from PySide2.QtGui import QColor
import os

class database_viewer(QLineEdit):
    def __init__(self):
        super(database_viewer,self).__init__(parent = None)
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        all_txt = self.text()  # Copy, dont use
        self.clear()
        self.pick_color(all_txt)
        self.blockSignals(False)

    def pick_color(self, txt):
        if os.path.isfile(txt) and txt.split('.')[-1] in ["Fasta", "fasta", "FASTA"]:
            self.setStyleSheet("color: green;") # Check if path
            self.setText(txt)
        else:
            self.setStyleSheet("color: red;") # Check if path
            self.setText(txt)
