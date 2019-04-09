from PySide2.QtWidgets import QComboBox, QVBoxLayout, QFrame, QTableWidget, QLabel, QStackedLayout

from custom_config_parser import custom_config_parser
from tooltip_label import tooltip_label
from tab2.parameter_setter import parameter_setter_single

class choose_option(QComboBox):

    def __init__(self, parameter, settings_file):
        super(choose_option,self).__init__(parent = None)
        self.parameter = parameter
        self.parser = custom_config_parser()
        self.parser.load(settings_file)
        self.settings_file = settings_file
        if self.parameter == 'workflow':
            self.addItems(["Full", "MSconvert", "Quandenser"])
        elif 'parallel' in self.parameter:
            self.addItems(["true", "false"])
        elif self.parameter == 'profile':
            self.addItems(["local", "cluster"])
        elif self.parameter == 'process.executor':
            self.addItems(["slurm"])
        self.default()
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        if self.parameter == 'workflow':
            self.parser.write(f"params.{self.parameter}", self.currentText())
            window = self.window()  # Update batch_file_viewers on tab 1
            self.recurse_children(window)
        elif 'parallel' in self.parameter:
            self.parser.write(f"params.{self.parameter}", self.currentText(), isString=False)
            self.parallel_option()
            self.change_stack()
        elif self.parameter == 'profile':
            self.parser.write("PROFILE", self.currentText())
            self.change_stack()
        elif self.parameter == 'process.executor':
            self.parser.write(f"{self.parameter}", self.currentText(),
                              additional_information="cluster {")

    def change_stack(self):
        parent = self.parentWidget()
        # Check if parallel quandenser is enabled
        for child in parent.children():
            if hasattr(child, 'parameter'):
                if child.parameter == 'parallel_quandenser':
                    quandenser_parallel = child.currentText()
                elif child.parameter == 'profile':
                    profile = child.currentText()

        if profile == "local":
            current_stack = 0
        elif quandenser_parallel == 'false':
            current_stack = 1
        elif quandenser_parallel == 'true':
            current_stack = 2

        parent = parent.parentWidget()  # To get to hidden box, widget is 2 levels up
        children = parent.children()
        for child in children:
            if hasattr(child, "hidden_object"):
                child.layout().setCurrentIndex(current_stack)
                stack = child.layout().currentWidget()
                for w in stack.children():
                    if hasattr(w, 'default'):
                        w.default()

    def parallel_option(self):  # Will trigger on tab change
        if not hasattr(self, 'max_forks_widget') and self.parameter != 'parallel_quandenser_tree':
            self.max_forks_widget = parameter_setter_single(f"{self.parameter}_max_forks", self.settings_file)
            self.label = tooltip_label(f"Max forks {self.parameter.replace('_', ' ')}",
                                       "Maximum amount of parallel processes. Set to 0 for no limit")
            parent = self.parent().layout()
            parent.addRow(self.label, self.max_forks_widget)
            self.max_forks_widget.hide()
            self.label.hide()
        if self.currentText() == "true" and self.parameter != 'parallel_quandenser_tree':
            self.max_forks_widget.show()
            self.label.show()
        elif self.parameter != 'parallel_quandenser_tree':
            self.max_forks_widget.hide()
            self.label.hide()

        if not hasattr(self, 'quandenser_tree') and self.parameter == 'parallel_quandenser':
            self.quandenser_tree = choose_option(f"{self.parameter}_tree", self.settings_file)
            self.tree_label = tooltip_label(f"Quandenser tree parallelization",
                                             """EXPERIMENTAL: Enable this to run parallel_3 in parallel. This may cause unforseen crashes""")
            parent = self.parent().layout()
            parent.addRow(self.tree_label, self.quandenser_tree)
            self.quandenser_tree.hide()
            self.tree_label.hide()
        if self.currentText() == "true" and self.parameter == 'parallel_quandenser':
            self.quandenser_tree.show()
            self.tree_label.show()
        elif self.parameter == 'parallel_quandenser':
            self.quandenser_tree.hide()
            self.tree_label.hide()

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
