import sys
from PyQt5.QtWidgets import QPushButton, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon

class file_chooser(QPushButton):

    def __init__(self):
        super().__init__()
        self.title = 'Choose MS files'
        self.button = QPushButton('Choose MS files', self)
        self.button.resize(200,300)
        self.button.clicked.connect(self.open_window)

    def open_window(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            return files
