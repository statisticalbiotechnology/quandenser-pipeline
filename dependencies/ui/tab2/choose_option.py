from PySide2.QtWidgets import QComboBox, QVBoxLayout, QFrame

from ..custom_config_parser import custom_config_parser

class choose_option(QComboBox):

    def __init__(self, settings_file, parameter):
        super(choose_option,self).__init__(parent = None)
        self.parameter = parameter
        if self.parameter == 'workflow':
            self.addItems(["Full", "MSconvert"])
        elif self.parameter == 'parallell_msconvert':
            self.addItems(["true", "false"])
        elif self.parameter == 'profile':
            self.addItems(["local", "cluster"])
        self.parser = custom_config_parser()
        self.parser.load(settings_file)
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        if self.parameter == 'workflow':
            self.parser.write("params.workflow", self.currentText())
        elif self.parameter == 'parallell_msconvert':
            self.parser.write("params.parallell_msconvert", self.currentText(), isString=False)
        elif self.parameter == 'profile':
            self.parser.write("PROFILE", self.currentText())
            self.check_hidden()

    def check_hidden(self):
        parent = self.parentWidget()
        parent = parent.parentWidget()  # Exist two levels up
        children = parent.children()
        if self.currentText() == "cluster":  # Add widgets
            for child in children:
                if hasattr(child, "hidden_object"):
                    child.show()
        elif self.currentText() == "local":
            for child in children:
                if hasattr(child, "hidden_object"):
                    child.hide()
