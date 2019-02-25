from PySide2.QtWidgets import QComboBox, QVBoxLayout, QFrame, QTableWidget, QLabel

from custom_config_parser import custom_config_parser
from tab2.parameter_setter import parameter_setter_single

class choose_option(QComboBox):

    def __init__(self, parameter, settings_file):
        super(choose_option,self).__init__(parent = None)
        self.parameter = parameter
        if self.parameter == 'workflow':
            self.addItems(["Full", "MSconvert"])
        elif 'parallel' in self.parameter:
            self.addItems(["true", "false"])
        elif self.parameter == 'profile':
            self.addItems(["local", "cluster"])
        elif self.parameter == 'process.executor':
            self.addItems(["slurm"])
        self.parser = custom_config_parser()
        self.parser.load(settings_file)
        self.settings_file = settings_file
        self.default()
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        if self.parameter == 'workflow':
            self.parser.write(f"params.{self.parameter}", self.currentText())
            window = self.window()  # Update batch_file_viewers on tab 1
            self.recurse_children(window)
        elif 'parallel' in self.parameter:
            self.parser.write(f"params.{self.parameter}", self.currentText(), isString=False)
            if not hasattr(self, 'max_forks_widget'):
                self.max_forks_widget = parameter_setter_single(f"{self.parameter}_max_forks", self.settings_file)
                self.label = QLabel(f"Max forks {self.parameter.replace('_', ' ')}")
                parent = self.parent().layout()
                parent.addRow(self.label, self.max_forks_widget)
                self.max_forks_widget.hide()
                self.label.hide()
            if self.currentText() == "true":
                self.max_forks_widget.show()
                self.label.show()
            else:
                self.max_forks_widget.hide()
                self.label.hide()
        elif self.parameter == 'profile':
            self.parser.write("PROFILE", self.currentText())
            self.check_hidden()
        elif self.parameter == 'process.executor':
            self.parser.write(f"{self.parameter}", self.currentText(),
                              additional_information="cluster {")

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

    def default(self):
        if self.parameter == 'profile':
            index = self.findText(self.parser.get("PROFILE"))
        elif self.parameter == 'process.executor':
            index = self.findText(self.parser.get(f"{self.parameter}", additional_information="cluster {"))
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
