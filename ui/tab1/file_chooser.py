import sys
from PySide2.QtWidgets import QFileDialog, QPushButton, QTextEdit
from PySide2.QtGui import QIcon
from difflib import SequenceMatcher

class file_chooser(QPushButton):

    def __init__(self):
        super(file_chooser,self).__init__(parent = None)
        self.setText('Choose MS files')
        self.clicked.connect(self.open_window)

    def open_window(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,
                                                "QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)",
                                                options=options)
        if files:
            self.display_in_file_viewer(files)

    def display_in_file_viewer(self, files):
        parent = self.parentWidget()
        batch_file_viewer = parent.findChildren(QTextEdit)[0]
        for file in files:
            batch_file_viewer.append(file + '\t' + 'A')

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
