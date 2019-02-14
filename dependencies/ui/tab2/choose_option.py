from PySide2.QtWidgets import QComboBox, QVBoxLayout, QFrame, QTableWidget

from custom_config_parser import custom_config_parser

class choose_option(QComboBox):

    def __init__(self, settings_file, parameter):
        super(choose_option,self).__init__(parent = None)
        self.parameter = parameter
        if self.parameter == 'workflow':
            self.addItems(["Full", "MSconvert"])
        elif self.parameter == 'parallell_msconvert':
            self.addItems(["true", "false"])
        elif self.parameter == 'profile':
            self.addItems(["local", "slurm_cluster"])
        self.parser = custom_config_parser()
        self.parser.load(settings_file)
        self.default()
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        if self.parameter == 'workflow':
            self.parser.write("params.workflow", self.currentText())
            self.window()
            window = self.window()
            self.recurse_children(window)
        elif self.parameter == 'parallell_msconvert':
            self.parser.write("params.parallell_msconvert", self.currentText(), isString=False)
        elif self.parameter == 'profile':
            self.parser.write("PROFILE", self.currentText())
            self.check_hidden()

    def check_hidden(self):
        parent = self.parentWidget()
        parent = parent.parentWidget()  # Exist two levels up
        children = parent.children()
        if self.currentText() == "slurm_cluster":  # Add widgets
            for child in children:
                if hasattr(child, "hidden_object"):
                    child.show()
        elif self.currentText() == "local":
            for child in children:
                if hasattr(child, "hidden_object"):
                    child.hide()

    def default(self):
        if self.parameter == 'profile':
            index = self.findText(self.parser.get("PROFILE"))
        else:
            index = self.findText(self.parser.get(f"params.{self.parameter}"))
        self.setCurrentIndex(index)

    def recurse_children(self, parent):
        children = parent.children()
        if children == []:
            return
        for child in children:
            if isinstance(child, QTableWidget) and child.__class__.__name__ == "batch_file_viewer":
                child.update()
                return
            self.recurse_children(child)  # WE HAVE TO GO DEEPER!
