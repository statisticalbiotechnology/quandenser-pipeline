import sys
from PySide2.QtWidgets import QFileDialog, QPushButton, QTextEdit, QLineEdit, QTableWidget, QSizePolicy
from PySide2.QtGui import QIcon

from custom_config_parser import custom_config_parser

class resume_chooser(QPushButton):

    def __init__(self, pipe_path):
        super(resume_chooser,self).__init__(parent = None)
        self.setFixedWidth(300)
        self.type = type
        self.id = id
        self.pipe_parser = custom_config_parser()
        self.pipe_parser.load(pipe_path)
        self.setText('Choose a previous output directory')
        self.clicked.connect(self.open_window)

    def open_window(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path = self.pipe_parser.get('pwd')
        output = QFileDialog.getExistingDirectory(self,
                                                  "Choose previous output directory",
                                                  path,
                                                  options=options)
        if output:
            self.display_in_file_viewer(output)

    def display_in_file_viewer(self, output):
        parent = self.parentWidget()
        for child in parent.children():
            if child.__class__.__name__ == 'resume_folder_viewer':
                child.setText(output)
