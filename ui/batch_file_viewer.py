import sys
from PyQt5.QtWidgets import QTextBrowser, QTextEdit

class batch_file_viewer(QTextEdit):
    def __init__(self):
        super(QTextEdit,self).__init__(parent = None)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setObjectName("Test")
        self.setText('Hello, this is a test')
