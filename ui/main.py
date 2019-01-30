import sys
import os
from PySide2.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTabWidget
from PySide2.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QApplication
from PySide2.QtWidgets import QLabel, QMainWindow, QComboBox, QTextEdit, QTableWidget
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtGui import QIcon
from PySide2 import QtCore

# Remember config
import configparser

# Widgets
from tab1.file_chooser import file_chooser
from tab1.database_viewer import database_viewer
from tab1.batch_file_viewer import batch_file_viewer
from tab1.run_button import run_button
from tab2.workflow_choose import workflow_choose
from tab3.msconvert_arguments import msconvert_arguments
from tab5.about import about

class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Quandenser-pipeline'
        self.setWindowIcon(QIcon('quandenser_icon.jpg'))
        self.left = 10
        self.top = 10
        self.WIDTH = 600
        self.HEIGHT = 400
        self.settings_path = '../config/ui.config'
        self.settings_obj = QtCore.QSettings(self.settings_path, QtCore.QSettings.IniFormat)
        # Restore window's previous geometry from file
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        self.initUI()

        if os.path.exists(self.settings_path):
            self.restoreGeometry(self.settings_obj.value("windowGeometry"))
            self.restoreState(self.settings_obj.value("State_main"))
            children = self.children()
            for child in children:
                self.recurse_children(child, save=False)
        self.show()

    def initUI(self):
        self.setWindowTitle(self.title)

        # Central widget
        self.tabs = QTabWidget()  # Multiple tabs, slow to load

        # Init tab1
        self.inittab1()

        # Tab 2
        self.inittab2()

        # Tab 3
        self.inittab3()

        # Tab 4
        self.inittab4()

        # Tab 5
        self.inittab5()

        # Add the tabs
        self.tabs.addTab(self.tab1, "MS files")
        self.tabs.addTab(self.tab2, "Edit workflow")
        self.tabs.addTab(self.tab3, "MSconvert")
        self.tabs.addTab(self.tab4, "How to use")
        self.tabs.addTab(self.tab5, "About")

        self.setCentralWidget(self.tabs)

        self.show()

    def inittab1(self):
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        # Widgets in leftbox
        self.fasta_chooser = file_chooser(type='fasta')
        self.database_viewer = database_viewer()
        self.ms_chooser = file_chooser(type='ms')
        self.batch_file_viewer = batch_file_viewer()
        self.run_button = run_button()

        self.tab1_layout.addWidget(self.fasta_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.database_viewer)
        self.tab1_layout.addWidget(self.ms_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.batch_file_viewer)
        self.tab1_layout.addWidget(self.run_button)

    def inittab2(self):
        self.tab2 = QWidget()
        self.tab2_layout = QHBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        # Left box
        self.leftbox = QWidget()
        self.leftbox_layout = QFormLayout()
        self.leftbox.setLayout(self.leftbox_layout)
        self.workflow_choose = workflow_choose()
        self.leftbox_layout.addRow(QLabel('Choose pipeline'), self.workflow_choose)

        # Right box
        self.rightbox = QWidget()
        self.rightbox_layout = QHBoxLayout()
        self.rightbox.setLayout(self.rightbox_layout)

        self.workflow = QWebEngineView()
        html_file = open("tab2/full.html")
        self.workflow.setHtml(html_file.read())
        self.rightbox_layout.addWidget(self.workflow)

        # Combine
        self.tab2_layout.addWidget(self.leftbox)
        self.tab2_layout.addWidget(self.rightbox)

    def inittab3(self):
        self.tab3 = QWidget()

    def inittab4(self):
        self.tab4 = QWidget()

    def inittab5(self):
        self.tab5 = QWidget()
        self.tab5_layout = QVBoxLayout()
        self.tab5.setLayout(self.tab5_layout)
        self.about = about()
        self.tab5_layout.addWidget(self.about)

    def closeEvent(self, event):
        self.settings_obj.setValue("windowGeometry", self.saveGeometry())
        self.settings_obj.setValue("State_main", self.saveState())
        children = self.children()
        self.widget_counter = 0  # Reset
        for child in children:
            self.recurse_children(child)


    def recurse_children(self, parent, save=True):
        children = parent.children()
        if children == []:
            return
        for child in children:
            self.child_settings(child, save=save)
            self.recurse_children(child, save=save)  # WE HAVE TO GO DEEPER!

    def child_settings(self, child, save=True):
        if isinstance(child, QPushButton):
            pass
        elif isinstance(child, QTextEdit):
            if save:
                self.settings_obj.setValue(f"State_{child.__class__.__name__}",
                                           child.toPlainText())
            else:
                if self.settings_obj.value(f"State_{child.__class__.__name__}") is None:
                    return
                else:
                    child.setPlainText(self.settings_obj.value(f"State_{child.__class__.__name__}"))
        elif isinstance(child, QLineEdit):
            if save:
                self.settings_obj.setValue(f"State_{child.__class__.__name__}",
                                           child.text())
            else:
                if self.settings_obj.value(f"State_{child.__class__.__name__}") is None:
                    return
                else:
                    child.setText(self.settings_obj.value(f"State_{child.__class__.__name__}"))
        elif isinstance(child, QTableWidget):
            if save:
                full_table = []
                for row in range(child.rowCount()):
                    for column in range(child.columnCount()):
                        full_table.append(child.item(row, column).text())
                        if not column == child.columnCount() - 1:
                            full_table.append(',')
                    full_table.append(';')
                full_table = ''.join(full_table)
                self.settings_obj.setValue(f"State_{child.__class__.__name__}",
                                           full_table)
            else:
                if self.settings_obj.value(f"State_{child.__class__.__name__}") is None:
                    return
                full_table = self.settings_obj.value(f"State_{child.__class__.__name__}")
                full_table = full_table.split(';')
                amount_of_rows = len(full_table) - 1
                amount_of_columns = len(full_table[0].split(','))
                child.setRowCount(amount_of_rows)
                child.setColumnCount(amount_of_columns)
                for row in range(amount_of_rows):
                    row_contents = full_table[row].split(',')
                    for column in range(amount_of_columns):
                        child.item(row, column).setText(row_contents[column])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
