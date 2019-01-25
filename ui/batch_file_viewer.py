import sys
from PyQt5.QtWidgets import QTextBrowser, QTextEdit
from PyQt5 import QtGui
import os

class batch_file_viewer(QTextEdit):
    def __init__(self):
        super(QTextEdit,self).__init__(parent = None)
        self.textChanged.connect(self.check_text)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setText('Hello, this is a test')
        self.append("I'm blue /media/!")
        self.append("I'm red !")
        self.append("/imgreen/  A")

    def check_text(self):
        self.blockSignals(True)
        all_txt = str(self.toPlainText())  # Copy, dont use
        all_txt = all_txt.split('\n')
        self.clear()
        print(all_txt)
        for txt in all_txt:
            self.pick_color(txt)
            self.append(txt)
        self.blockSignals(False)

    def pick_color(self, txt):
        txt = txt.split('\t')
        if len(txt) == 1:
            if not os.path.isfile(txt[0]):
                self.setTextColor(QtGui.QColor("red"))
            else:
                self.setTextColor(QtGui.QColor("blue"))
        elif len(txt) == 2:
            if not os.path.isfile(txt[0]):
                self.setTextColor(QtGui.QColor("red"))
            else:
                self.setTextColor(QtGui.QColor("green"))  # Check if path
        else:
            self.setTextColor(QtGui.QColor("red"))
