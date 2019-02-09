from PySide2.QtWidgets import QComboBox, QVBoxLayout

from ..custom_config_parser import custom_config_parser

class choose_option(QComboBox):

    def __init__(self, settings_file):
        super(choose_option,self).__init__(parent = None)
        self.addItems(["Full", "Triqler", "MSconvert"])
        self.parser = custom_config_parser()
        self.parser.load(settings_file)
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        #print("Current index",i,"selection changed ",self.currentText())
        self.parser.write("params.workflow_choose", self.currentText())
        value = self.parser.get("params.workflow_choose")
