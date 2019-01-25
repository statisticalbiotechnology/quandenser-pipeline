import sys
from PyQt5.QtWidgets import QTextBrowser, QTextEdit

class batch_file_viewer(QTextBrowser):
    def __init__(self):
        super(QTextBrowser,self).__init__(parent = None)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setObjectName("Test")
        self.setText('Hello, this is a test')
