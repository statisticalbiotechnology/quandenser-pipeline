import sys
from PyQt5.QtWidgets import QPushButton, QFileDialog, QApplication
from PyQt5.QtGui import QIcon

class file_chooser(QPushButton):

    def __init__(self):
        super(QPushButton,self).__init__(parent = None)
        self.setText('Choose MS files')
        self.clicked.connect(self.open_window)

    def open_window(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            self.display_in_file_viewer(files)

    def display_in_file_viewer(self, files):
        print([o.showMinimized() for o in QApplication.topLevelWidgets()])

    def set_size(self, width, height):
        pass
        #self.resize(width, height)
