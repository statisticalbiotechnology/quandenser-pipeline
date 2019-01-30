from PySide2.QtWidgets import QComboBox, QVBoxLayout

class workflow_choose(QComboBox):

    def __init__(self):
        super(workflow_choose,self).__init__(parent = None)
        self.addItems(["Full", "Triqler", "MSconvert"])
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        print("Current index",i,"selection changed ",self.currentText())
