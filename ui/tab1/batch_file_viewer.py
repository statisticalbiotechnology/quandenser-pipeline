import sys
from PySide2.QtWidgets import QTextEdit
from PySide2.QtGui import QColor
import os

class batch_file_viewer(QTextEdit):
    def __init__(self):
        super(batch_file_viewer,self).__init__(parent = None)
        self.textChanged.connect(self.check_text)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.append("/media/storage/timothy/MSfiles/mzML/A1.mzML\ttab")
        self.append("/media/storage/timothy/MSfiles/mzML/A1.mzML")
        self.append("/media/storage/timothy/MSfiles/mzML/A1.mzML blankspace")
        self.append("/notafile/test.txt\tnotafile")

    def check_text(self):
        self.blockSignals(True)
        all_txt = str(self.toPlainText())  # Copy, dont use
        all_txt = all_txt.split('\n')
        self.clear()
        for txt in all_txt:
            self.pick_color(txt)
            self.append(txt)
        self.blockSignals(False)

    def pick_color(self, txt):
        txt = txt.split('\t')
        if len(txt) == 1:
            self.setTextColor(QColor("red"))
        elif len(txt) == 2:
            if not os.path.isfile(txt[0]):
                self.setTextColor(QColor("red"))
            elif len(txt[1]) == 0:
                self.setTextColor(QColor("red"))
            elif txt[0].split('.')[-1] != "mzML":  # If extension != mzML
                self.setTextColor(QColor("blue"))
            else:
                self.setTextColor(QColor("green"))  # Check if path
        else:
            self.setTextColor(QColor("red"))
