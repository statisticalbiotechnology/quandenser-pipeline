import sys
from PySide2.QtWidgets import QDoubleSpinBox, QSpinBox

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser

class parameter_setter_single(QSpinBox):
    def __init__(self, parameter, nf_settings_path):
        super(parameter_setter_single,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.parameter = parameter
        self.default()
        self.valueChanged.connect(self.check_value)

    def check_value(self):
        self.blockSignals(True)
        self.nf_settings_parser.write(f"{self.parameter}",
                                      self.value(),
                                      isString=False)
        self.blockSignals(False)

    def default(self):
        value = int(self.nf_settings_parser.get(f"{self.parameter}"))
        self.setValue(value)

class parameter_setter_double(QDoubleSpinBox):
    def __init__(self, parameter, nf_settings_path):
        super(parameter_setter_double,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.parameter = parameter
        self.default()
        self.valueChanged.connect(self.check_value)

    def check_value(self):
        self.blockSignals(True)
        value = round(self.value(), 4)  # Prevents weird behavior with 0.0000001
        self.nf_settings_parser.write(f"{self.parameter}",
                                      value,
                                      isString=False)
        self.blockSignals(False)

    def default(self):
        if self.parameter == "precursor_window":  # Crux
            self.setSuffix(" ppm")
        if self.parameter == "fold_change_eval":  # Triqler
            self.setSingleStep(0.05)
        value = float(self.nf_settings_parser.get(f"{self.parameter}"))
        self.setValue(value)
