# System
import sys
import os
from colorama import Fore, Back, Style
import pdb
import time

# Style for PySide2
import qdarkstyle
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # Bug where futurewarning triggers for pyside2

# PySide2 imports
from PySide2.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTabWidget
from PySide2.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QApplication, QDoubleSpinBox, QSpinBox
from PySide2.QtWidgets import QLabel, QMainWindow, QComboBox, QTextEdit, QTableWidget, QMessageBox, QTableWidgetItem, QFrame
from PySide2.QtGui import QIcon, QFontDatabase
from PySide2 import QtCore

from tab1.init_tab1 import init_tab1
from tab2.init_tab2 import init_tab2
from tab3.init_tab3 import init_tab3
from tab4.init_tab4 import init_tab4
from tab5.init_tab5 import init_tab5

# Custom parser
from custom_config_parser import custom_config_parser
from tooltip_label import tooltip_label

# Utils
from utils import check_corrupt, check_running, ERROR

# read user and create config location
user = os.environ.get('USER')
config_path = f"/var/tmp/quandenser_pipeline_{user}"
#print(Style.BRIGHT, end='\r')  # Set style

class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Quandenser-pipeline'
        self.setWindowIcon(QIcon('images/logo.png'))
        QFontDatabase.addApplicationFont("fonts/rockwell.ttf")
        self.resize(1000, 800)

        # Check file integrety
        check_corrupt(config_path)
        self.paths = {}
        self.paths['config'] = f"{config_path}"
        self.paths['ui'] = f"{config_path}/ui.config"
        self.paths['nf'] = f"{config_path}/nf.config"
        self.paths['sh'] = f"{config_path}/run_quandenser.sh"
        self.paths['pipe'] = f"{config_path}/PIPE"
        self.paths['jobs'] = f"{config_path}/jobs.txt"

        # Open pipe and read
        self.pipe_parser = custom_config_parser()
        self.pipe_parser.load(self.paths['pipe'])
        check_running(config_path)
        self.pipe_parser.write('exit_code', '2', isString=False)  # Add error code 2. If we manage to load, change to 1

        # To restore settings of window
        self.settings_obj = QtCore.QSettings(self.paths['ui'], QtCore.QSettings.IniFormat)
        # Restore window's previous geometry from file
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        self.initUI()
        if os.path.exists(self.paths['ui']):
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
        self.tabs.currentChanged.connect(self.tab_changed)

        # Init tabs
        self.tab1 = init_tab1(self.paths)  # Tab 1
        self.tab2 = init_tab2(self.paths)  # Tab 2
        self.tab3 = init_tab3(self.paths)  # Tab 3
        self.tab4 = init_tab4(self.paths)  # Tab 4
        self.tab5 = init_tab5(self.paths)  # Tab 5

        # Add the tabs
        self.tabs.addTab(self.tab1, "MS files")
        self.tabs.addTab(self.tab2, "Edit workflow")
        self.tabs.addTab(self.tab3, "Advanced Settings")
        self.tabs.addTab(self.tab4, "Running jobs")
        self.tabs.addTab(self.tab5, "About")
        self.setCentralWidget(self.tabs)
        self.show()


    def tab_changed(self, index):
        if self.tabs.tabText(index) == "Edit workflow":

            def recurse_children(parent):  # not "self.recurse_children"
                children = parent.children()
                for child in children:
                    if hasattr(child, 'parameter'):
                        if child.parameter == 'profile':
                            child.change_stack()
                        elif hasattr(child, 'parallel_option') and 'parallel' in child.parameter:
                            child.parallel_option()
                    else:
                        recurse_children(child)

            recurse_children(self.tab2)
        elif self.tabs.tabText(index) == "Running jobs":

            def recurse_children(parent):  # not "self.recurse_children"
                children = parent.children()
                for child in children:
                    if hasattr(child, 'update'):
                        child.update()
                    else:
                        recurse_children(child)

            recurse_children(self.tab4)

    """This is for loading and saving state of child widgets"""
    def closeEvent(self, event):
        self.settings_obj.setValue("windowGeometry", self.saveGeometry())
        self.settings_obj.setValue("State_main", self.saveState())
        children = self.children()
        self.widget_counter = 0  # Reset
        for child in children:
            self.recurse_children(child)
        # Clean exit
        exit_code = int(self.pipe_parser.get('exit_code'))
        if exit_code == 0:  # This means that it had been modified during runtime --> run button has been pressed
            pass
        else:
            self.pipe_parser.write('exit_code', '1', isString=False)

    def recurse_children(self, parent, save=True):  # THIS DO NOT CREATE STACK SMASHING
        children = parent.children()
        if children == []:
            return
        for child in children:
            self.child_settings(child, save=save)
            self.recurse_children(child, save=save)  # WE HAVE TO GO DEEPER!

    def child_settings(self, child, save=True):
        state_name = ''   # This is so you can have multiple of same type of widget
        if hasattr(child, 'type'):
            state_name += "_" + str(child.type)
        if hasattr(child, 'id'):
            state_name += "_" + str(child.id)
        if hasattr(child, 'parameter'):
            state_name += "_" + str(child.parameter)
        if hasattr(child, 'process'):
            state_name += "_" + str(child.process)
        if hasattr(child, 'argument'):
            state_name += "_" + str(child.argument)
        child_name = f"State_{child.__class__.__name__}" + state_name

        """
        Some modules inherit QLineEdit even though they are something else (ex QDoubleSpinBox)
        This prevents the inherited module from getting registered and overwriting input.
        Prevent any module from registering without proper registration
        """
        if state_name == '' and child.__class__.__name__ == "QLineEdit":
            return

        if isinstance(child, QPushButton):
            pass
        elif isinstance(child, QTextEdit):
            if save:
                self.settings_obj.setValue(child_name,
                                           child.toPlainText())
            else:
                if self.settings_obj.value(child_name) is None:
                    return
                else:
                    child.setPlainText(self.settings_obj.value(child_name))
        elif isinstance(child, QLineEdit):
            if save:
                self.settings_obj.setValue(child_name, child.text())
            else:
                if self.settings_obj.value(child_name) is None:
                    return
                else:
                    child.setText(self.settings_obj.value(child_name))
        elif isinstance(child, QComboBox):
            if save:
                self.settings_obj.setValue(child_name, child.currentText())
            else:
                if self.settings_obj.value(child_name) is None:
                    return
                else:
                    child.setCurrentText(self.settings_obj.value(child_name))
        elif isinstance(child, QDoubleSpinBox) or isinstance(child, QSpinBox):
            if save:
                self.settings_obj.setValue(child_name, child.value())
            else:
                if self.settings_obj.value(child_name) is None:
                    return
                else:
                    child.setValue(float(self.settings_obj.value(child_name)))
        # I want running jobs to depend on jobs.txt, not ui saving
        elif isinstance(child, QTableWidget) and child.__class__.__name__ != "running_jobs":
            if save:
                full_table = []
                for row in range(child.rowCount()):
                    for column in range(child.columnCount()):
                        full_table.append(child.item(row, column).text())
                        if not column == child.columnCount() - 1:
                            full_table.append(',')
                    full_table.append(';')
                full_table = ''.join(full_table)
                self.settings_obj.setValue(child_name,
                                           full_table)
            else:
                if self.settings_obj.value(child_name) is None:  # quick check for errors
                    return
                full_table = self.settings_obj.value(child_name)
                full_table = full_table.split(';')
                amount_of_rows = len(full_table) - 1
                amount_of_columns = len(full_table[0].split(','))
                child.setRowCount(amount_of_rows)
                child.setColumnCount(amount_of_columns)
                child.blockSignals(True)
                for row in range(amount_of_rows):
                    row_contents = full_table[row].split(',')
                    for column in range(amount_of_columns):
                        if child.item(row, column) is None:
                            item = QTableWidgetItem()
                            item.setText('')
                            child.setItem(row, column, item)
                        child.item(row, column).setText(row_contents[column])
                if hasattr(child, 'update'):
                    child.update()
                child.blockSignals(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())  # Set dark style
    ex = Main() # Stack smashing happens BEFORE we reach here
    sys.exit(app.exec_())
