import sys
from PySide2.QtWidgets import QLineEdit

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser

class additional_arguments(QLineEdit):
    def __init__(self, argument, nf_settings_path):
        super(additional_arguments,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.argument = argument
        if "password" in self.argument:
            self.setEchoMode(QLineEdit.Password)  # Hide password
        self.setText('')
        self.default()
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        all_txt = self.text()  # Copy, dont use
        self.nf_settings_parser.write(f"{self.argument}", all_txt)
        self.blockSignals(False)

    def default(self):
        self.blockSignals(True)
        self.setText(self.nf_settings_parser.get(f"{self.argument}"))
        self.blockSignals(False)
