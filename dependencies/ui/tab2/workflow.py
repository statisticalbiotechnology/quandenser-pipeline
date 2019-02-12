from PySide2.QtWidgets import QLabel
from PySide2.QtGui import QPixmap


class workflow(QLabel):

    def __init__(self):
        super(workflow,self).__init__(parent = None)
        pixmap = QPixmap('ui/tab2/flowchart.png')
        self.setScaledContents(True)
        self.setPixmap(pixmap)
