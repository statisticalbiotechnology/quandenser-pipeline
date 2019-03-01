import sys
from PySide2.QtWidgets import QLineEdit
from PySide2.QtGui import QColor
import os

from custom_config_parser import custom_config_parser

class resume_folder_viewer(QLineEdit):
    def __init__(self, nf_settings_path, id=0):
        super(resume_folder_viewer,self).__init__(parent = None)
        self.type = type
        self.id = id
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(nf_settings_path)
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        all_txt = self.text()  # Copy, dont use
        self.clear()
        self.pick_color(all_txt)
        self.blockSignals(False)

    def pick_color(self, txt):
        if os.path.isdir(txt):
            self.setStyleSheet("color: rgb(0, 255, 150);") # Check if path
            self.setText(txt)
            self.nf_settings_parser.write('params.resume_directory', self.text())
        else:
            self.setStyleSheet("color: red;") # Check if path
            self.setText(txt)
            self.nf_settings_parser.write('params.resume_directory', '')
