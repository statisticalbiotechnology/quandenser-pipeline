import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTabWidget
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QApplication
from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtGui import QIcon

# Remember config
import configparser

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
        self.config = configparser.ConfigParser()
        self.config.read_file(open('../config/ui.config'))
        self.WIDTH = int(self.config['graphics']['WIDTH'])  # Note: self.width overwrites self.width() function!
        self.HEIGHT = int(self.config['graphics']['HEIGHT'])  # Config to remember size
        self.setMinimumWidth(200)
        self.setMinimumHeight(200)
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.WIDTH, self.HEIGHT)

        # Central widget
        self.tabs = QTabWidget()  # Multiple tabs

        # Tab 1
        self.tab1 = QWidget()
        self.tab1_layout = QHBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        # Init left box
        self.initLeft_box()

        # Init right box
        self.initRight_box()

        # Tab 2
        self.tab2 = QWidget()

        # Add the tabs
        self.tabs.addTab(self.tab1, "Run pipeline")
        self.tabs.addTab(self.tab2, "Edit workflow")


        self.setCentralWidget(self.tabs)

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
        self.tab1_layout.addWidget(self.left_box)

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
        self.tab1_layout.addWidget(self.right_box)


    def resizeEvent(self, event):
        self.config.set('graphics', 'WIDTH', str(self.width())
        self.config.set('graphics', 'HEIGHT', str(self.height()))

        """
        print(self.width(), self.height())
        children = [self.tab1_layout.itemAt(i).widget() for i in range(self.tab1_layout.count())]
        for child in children:
            print(child)
            if hasattr(child, 'set_size'):
                child.set_size(self.width(), self.height())
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
