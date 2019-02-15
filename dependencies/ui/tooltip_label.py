from PySide2.QtWidgets import QLabel
from PySide2 import QtCore

class tooltip_label(QLabel):

    def __init__(self, text, tooltip, style=True):
        super(tooltip_label,self).__init__(parent = None)
        self.setText(text)
        self.setToolTip(tooltip)
        if style:
            self.setStyleSheet("font: 30pt rockwell")
            self.setAlignment(QtCore.Qt.AlignCenter)
