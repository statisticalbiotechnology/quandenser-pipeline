from PySide2.QtWidgets import QPushButton

class run_button(QPushButton):

    def __init__(self):
        super(run_button,self).__init__(parent = None)
        self.setText('RUN')
        self.clicked.connect(self.run)

    def run(self):
        print("LETS GO")

    def set_size(self, width, height):
        pass
        #self.resize(width, height)
