import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QApplication
from PyQt5.QtGui import QIcon
from file_chooser import file_chooser

class Main(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Quandenser'
        self.left = 10
        self.top = 10
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width(), self.height())
        self.main_layout = QVBoxLayout()
        self.file_button = file_chooser()
        self.main_layout.addWidget(self.file_button)
        self.show()

    def resizeEvent(self, event):
        print(self.width(), self.height())
        children = [self.main_layout.itemAt(i).widget() for i in range(self.main_layout.count())]
        for child in children:
            print(child)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
