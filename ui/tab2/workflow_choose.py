from PySide2.QtWidgets import QComboBox, QVBoxLayout

class workflow_choose(QComboBox):

    def __init__(self):
        super(workflow_choose,self).__init__(parent = None)
        self.addItem("C")
        self.addItem("C++")
        self.addItems(["Java", "C#", "Python"])
        self.currentIndexChanged.connect(self.selectionchange)

    def selectionchange(self,i):
        print("Items in the list are :")

        for count in range(self.count()):
            print(self.itemText(count))
        print("Current index",i,"selection changed ",self.currentText())
