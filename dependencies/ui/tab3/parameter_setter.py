import sys
from PySide2.QtWidgets import QDoubleSpinBox, QSpinBox

# Custom parser for both sh files and nf configs
from ..custom_config_parser import custom_config_parser

class parameter_setter_single(QSpinBox):
    def __init__(self, parameter, nf_settings_path):
        super(parameter_setter_single,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.parameter = parameter
        if self.parameter == "max_missing":  # Quandenser
            self.setValue(3)
        elif self.parameter == "missed_clevages":  # Crux
            self.setValue(2)
        self.valueChanged.connect(self.check_value)

    def check_value(self):
        self.blockSignals(True)
        self.nf_settings_parser.write(f"params.{self.parameter}",
                                      self.value(),
                                      isString=False)
        self.blockSignals(False)

class parameter_setter_double(QDoubleSpinBox):
    def __init__(self, parameter, nf_settings_path):
        super(parameter_setter_double,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.parameter = parameter
        if self.parameter == "precursor_window":  # Crux
            self.setSuffix(" ppm")
            self.setValue(20.0)
        if self.parameter == "fold_change_eval":  # Triqler
            self.setValue(0.8)
            self.setSingleStep(0.05)
        self.valueChanged.connect(self.check_value)

    def check_value(self):
        self.blockSignals(True)
        self.nf_settings_parser.write(f"params.{self.parameter}",
                                      self.value(),
                                      isString=False)
        self.blockSignals(False)
