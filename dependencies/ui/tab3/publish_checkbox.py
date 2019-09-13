import sys
from PySide2.QtWidgets import QCheckBox

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser

class publish_checkbox(QCheckBox):
    def __init__(self, parameter, nf_settings_path):
        super(publish_checkbox,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.parameter = parameter
        self.default()
        self.stateChanged.connect(self.check_check)

    def check_check(self):
        if self.isChecked():
            check_state = 'true'
        else:
            check_state = 'false'
        self.nf_settings_parser.write(f"{self.parameter}",
                                      check_state,
                                      isString=False)

    def default(self):
        check_or_no_check = self.nf_settings_parser.get(f"{self.parameter}")
        if check_or_no_check == 'true':  # Yes, it uses strings
            self.setChecked(True)
        else:
            self.setChecked(False)
