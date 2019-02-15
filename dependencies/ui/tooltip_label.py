from PySide2.QtWidgets import QLabel

class tooltip_label(QLabel):

    def __init__(self, tooltip):
        super(tooltip_label,self).__init__(parent = None)
        self.setToolTip(tooltip)
