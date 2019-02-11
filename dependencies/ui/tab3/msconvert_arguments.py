import sys
from PySide2.QtWidgets import QLineEdit

# Custom parser for both sh files and nf configs
from ..custom_config_parser import custom_config_parser

class msconvert_arguments(QLineEdit):
    def __init__(self, nf_settings_path):
        super(msconvert_arguments,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.setText('')
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        all_txt = self.text()  # Copy, dont use
        self.nf_settings_parser.write("params.msconvert_additional_arguments", all_txt)
        self.blockSignals(False)
