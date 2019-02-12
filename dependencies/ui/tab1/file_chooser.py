import sys
from PySide2.QtWidgets import QFileDialog, QPushButton, QTextEdit, QLineEdit, QTableWidget, QSizePolicy
from PySide2.QtGui import QIcon

class file_chooser(QPushButton):

    def __init__(self, type='ms'):
        super(file_chooser,self).__init__(parent = None)
        self.setFixedWidth(200)
        self.type = type
        self.id = id
        if self.type=='ms':
            self.setText('Choose MS files')
        elif self.type=='fasta':
            self.setText('Choose fasta file')
        elif self.type=='directory':
            self.setText('Choose output directory')
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
            choose_string += ";;".join(ms_file_types)
            output, _ = QFileDialog.getOpenFileNames(self,
                                                    "Choose MS files",
                                                    "",
                                                    f"MS files ({choose_string});;All Files (*)",
                                                    options=options)
        elif self.type=='fasta':
            output, _ = QFileDialog.getOpenFileName(self,
                                                   "Choose fasta files",
                                                   "",
                                                   "Fasta files (.*fasta | *.Fasta | *.FASTA);;All Files (*)",
                                                   options=options)
        elif self.type=='directory':
            output = QFileDialog.getExistingDirectory(self,
                                                      options=options)
        if output:
            self.display_in_file_viewer(output)

    def display_in_file_viewer(self, output):
        parent = self.parentWidget()
        if self.type=='ms':
            batch_file_viewer = parent.findChildren(QTableWidget)[0]
            for file in output:
                batch_file_viewer.auto_assign(file)
        elif self.type=='fasta':
            database_file_viewer = parent.findChildren(QLineEdit)[0]
            database_file_viewer.setText(output)
        elif self.type=='directory':
            output_viewer = parent.findChildren(QLineEdit)[1]
            output_viewer.setText(output)
