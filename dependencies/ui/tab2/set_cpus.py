import sys
from PySide2.QtWidgets import QSpinBox

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser

class set_cpus(QSpinBox):
    def __init__(self, parameter, nf_settings_path):
        super(set_cpus,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.parameter = parameter
        self.valueChanged.connect(self.check_value)
        self.default()

    def check_value(self):
        self.blockSignals(True)
        #additional_information = self.parameter.replace('_cpus', '')  # Get name of process
        #additional_information = "withName: " + additional_information
        self.nf_settings_parser.write_all(f"cpus",
                                         self.value(),
                                         isString=False)
        self.blockSignals(False)

    def default(self):
        value = int(self.nf_settings_parser.get(f"cpus"))
        self.setValue(value)
