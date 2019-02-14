import sys
from PySide2.QtWidgets import QLineEdit

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser

class cluster_arguments(QLineEdit):
    def __init__(self, argument, nf_settings_path):
        super(cluster_arguments,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.argument = argument
        self.default()
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        all_txt = self.text()  # Copy, dont use
        self.nf_settings_parser.write(self.argument, all_txt)
        self.blockSignals(False)

    def default(self):
        txt = self.nf_settings_parser.get(self.argument)
        self.setText(txt)
