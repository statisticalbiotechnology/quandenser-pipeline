import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QApplication
from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtGui import QIcon

# Widgets
from file_chooser import file_chooser
from msconvert_arguments import msconvert_arguments
from batch_file_viewer import batch_file_viewer
from run_button import run_button

class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Quandenser'
        self.left = 10
        self.top = 10
        self.setMinimumWidth(200)
        self.setMinimumHeight(200)
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width(), self.height())

        # Central widget
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        # Init left box
        self.initLeft_box()

        # Init right box
        self.initRight_box()

        self.setCentralWidget(self.main_widget)

        self.show()

    def initLeft_box(self):
        # Left box
        self.left_box = QWidget()
        self.left_box_layout = QFormLayout()
        self.left_box.setLayout(self.left_box_layout)

        # Widgets in leftbox
        self.file_chooser = file_chooser()
        self.msconvert_arguments = msconvert_arguments()

        # Add
        self.left_box_layout.addRow(self.file_chooser)
        self.left_box_layout.addRow(QLabel("msconvert arguments"), self.msconvert_arguments)
        self.main_layout.addWidget(self.left_box)

    def initRight_box(self):
        # Right box
        self.right_box = QWidget()
        self.right_box_layout = QVBoxLayout()
        self.right_box.setLayout(self.right_box_layout)

        # Right box widgets
        self.batch_file_viewer = batch_file_viewer()
        self.run_button = run_button()

        # Add
        self.right_box_layout.addWidget(self.batch_file_viewer)
        self.right_box_layout.addWidget(self.run_button)
        self.main_layout.addWidget(self.right_box)


    def resizeEvent(self, event):
        print(self.width(), self.height())
        children = [self.main_layout.itemAt(i).widget() for i in range(self.main_layout.count())]
        for child in children:
            print(child)
            if hasattr(child, 'set_size'):
                child.set_size(self.width(), self.height())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
