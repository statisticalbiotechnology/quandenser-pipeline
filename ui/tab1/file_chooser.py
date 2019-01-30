import sys
from PySide2.QtWidgets import QFileDialog, QPushButton, QTextEdit, QLineEdit, QTableWidget, QSizePolicy
from PySide2.QtGui import QIcon

class file_chooser(QPushButton):

    def __init__(self, type='ms'):
        super(file_chooser,self).__init__(parent = None)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)
        self.setFixedWidth(200)
        self.type = type
        if self.type=='ms':
            self.setText('Choose MS files')
        elif self.type=='fasta':
            self.setText('Choose fasta file')
        self.clicked.connect(self.open_window)

    def open_window(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        if self.type=='ms':
            ms_file_types = ["*.mzML",
                             "*.D | *.d",
                             "*.YEP",
                             "*.BAF",
                             "*.FID",
                             "*.WIFF",
                             "*.raw | *.RAW"]
            choose_string = " | ".join(ms_file_types)
            files, _ = QFileDialog.getOpenFileNames(self,
                                                    "Choose MS files",
                                                    "",
                                                    f"MS files ({choose_string});;All Files (*)",
                                                    options=options)
        elif self.type=='fasta':
            files, _ = QFileDialog.getOpenFileName(self,
                                                   "Choose fasta files",
                                                   "",
                                                   "Fasta files (.*fasta | *.Fasta | *.FASTA);;All Files (*)",
                                                   options=options)
        if files:
            self.display_in_file_viewer(files)

    def display_in_file_viewer(self, files):
        parent = self.parentWidget()
        if self.type=='ms':
            batch_file_viewer = parent.findChildren(QTableWidget)[0]
            for file in files:
                batch_file_viewer.auto_assign(file)
        elif self.type=='fasta':
            database_file_viewer = parent.findChildren(QLineEdit)[0]
            database_file_viewer.setText(files)
