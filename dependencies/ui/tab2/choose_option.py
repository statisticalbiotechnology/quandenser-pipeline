from PySide2.QtWidgets import QComboBox, QVBoxLayout

from ..custom_config_parser import custom_config_parser

class choose_option(QComboBox):

    def __init__(self, settings_file, parameter):
        super(choose_option,self).__init__(parent = None)
        self.parameter = parameter
        if self.parameter == 'workflow':
            self.addItems(["Full", "MSconvert"])
        elif self.parameter == 'parallell_msconvert':
            self.addItems(["true", "false"])
        self.parser = custom_config_parser()
        self.parser.load(settings_file)
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        if self.parameter == 'workflow':
            self.parser.write("params.workflow", self.currentText())
        elif self.parameter == 'parallell_msconvert':
            self.parser.write("params.parallell_msconvert", self.currentText(), isString=False)
