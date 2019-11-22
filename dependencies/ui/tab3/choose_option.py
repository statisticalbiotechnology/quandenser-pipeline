from PySide2.QtWidgets import QComboBox, QVBoxLayout, QFrame, QTableWidget, QLabel, QStackedLayout
from PySide2 import QtCore, QtGui, QtWidgets

from custom_config_parser import custom_config_parser
from tooltip_label import tooltip_label
from tab2.parameter_setter import parameter_setter_single

class choose_option(QComboBox):

    def __init__(self, parameter, settings_file):
        super(choose_option,self).__init__(parent = None)
        self.parameter = parameter
        self.addItems(["true", "false"])
        self.parser = custom_config_parser()
        self.parser.load(settings_file)
        self.settings_file = settings_file
        self.default()
        # Fix for long combo boxes
        delegate = QtWidgets.QStyledItemDelegate()
        self.setItemDelegate(delegate)
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        self.parser.write(f"{self.parameter}", self.currentText(), isString=False)

    def default(self):
        index = self.findText(self.parser.get(f"{self.parameter}"))
        self.setCurrentIndex(index)
