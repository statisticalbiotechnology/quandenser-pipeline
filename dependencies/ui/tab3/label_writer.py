import sys
from PySide2.QtWidgets import QLineEdit
from PySide2.QtGui import QColor
import os

from custom_config_parser import custom_config_parser

class label_writer(QLineEdit):
    def __init__(self, sh_path, id=0):
        super(label_writer,self).__init__(parent = None)
        self.type = type
        self.id = id
        self.sh_parser = custom_config_parser()
        self.sh_parser.load(sh_path)
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        all_txt = self.text()  # Copy, dont use
        self.pick_color(all_txt)
        self.blockSignals(False)

    def pick_color(self, txt):
        if self.text() != '' and not '/' in self.text():
            self.setStyleSheet("color: rgb(0, 255, 150);") # Check if path
            self.sh_parser.write('OUTPUT_PATH_LABEL', '/' + self.text())
        else:
            self.setStyleSheet("color: red;") # Check if path
            self.sh_parser.write('OUTPUT_PATH_LABEL', '')

    def default(self):
        txt = self.nf_settings_parser.get('OUTPUT_PATH_LABEL')
        seelf.setText(txt)
