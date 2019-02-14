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
from PySide2.QtGui import QIcon
from PySide2 import QtCore

# Widgets
from tab1.file_chooser import file_chooser
from tab1.file_viewer import file_viewer
from tab1.batch_file_viewer import batch_file_viewer
from tab1.run_button import run_button
from tab2.workflow import workflow
from tab2.choose_option import choose_option
from tab2.cluster_arguments import cluster_arguments
from tab2.set_time import set_time
from tab2.set_cpus import set_cpus
from tab3.msconvert_arguments import msconvert_arguments
from tab3.parameter_setter import parameter_setter_double, parameter_setter_single
from tab3.reset_button import reset_button
from tab4.running_jobs import running_jobs
from tab5.about import about

# Custom parser
from custom_config_parser import custom_config_parser

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
        self.setWindowIcon(QIcon('logo.png'))
        self.resize(1000, 800)

        # Check file integrety
        check_corrupt(config_path)
        self.ui_settings_path = f"{config_path}/ui.config"
        self.nf_settings_path = f"{config_path}/nf.config"
        self.sh_script_path = f"{config_path}/run_quandenser.sh"
        self.pipe_path = f"{config_path}/PIPE"

        # Open pipe and read
        self.pipe_parser = custom_config_parser()
        self.pipe_parser.load(self.pipe_path)
        check_running(config_path)
        self.pipe_parser.write('exit_code', '2', isString=False)  # Add error code 2. If we manage to load, change to 1

        # To restore settings of window
        self.settings_obj = QtCore.QSettings(self.ui_settings_path, QtCore.QSettings.IniFormat)
        # Restore window's previous geometry from file
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        self.initUI()
        if os.path.exists(self.ui_settings_path):
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
        self.inittab1()  # Tab 1
        self.inittab2()  # Tab 2
        self.inittab3()  # Tab 3
        self.inittab4()  # Tab 4
        self.inittab5()  # Tab 5

        # Add the tabs
        self.tabs.addTab(self.tab1, "MS files")
        self.tabs.addTab(self.tab2, "Edit workflow")
        self.tabs.addTab(self.tab3, "Advanced Settings")
        self.tabs.addTab(self.tab4, "Running jobs")
        self.tabs.addTab(self.tab5, "About")
        self.setCentralWidget(self.tabs)

        self.show()

    def inittab1(self):
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        # Widgets in leftbox
        self.tab1_fasta_chooser = file_chooser(type='fasta')
        self.tab1_database_viewer = file_viewer(type='file')
        self.tab1_ms_chooser = file_chooser(type='ms')
        self.tab1_batch_file_viewer = batch_file_viewer(self.nf_settings_path)
        self.tab1_output_chooser = file_chooser(type='directory')
        self.tab1_output_viewer = file_viewer(type='directory')
        self.tab1_run_button = run_button(self.nf_settings_path, self.sh_script_path, self.pipe_path)

        self.tab1_layout.addWidget(self.tab1_fasta_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.tab1_database_viewer)
        self.tab1_layout.addWidget(self.tab1_ms_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.tab1_batch_file_viewer)
        self.tab1_layout.addWidget(self.tab1_output_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.tab1_output_viewer)
        self.tab1_layout.addWidget(self.tab1_run_button)

    def inittab2(self):
        self.tab2 = QWidget()
        self.tab2_layout = QHBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        # Left box
        self.tab2_leftbox = QWidget()
        self.tab2_leftbox_layout = QVBoxLayout()
        self.tab2_leftbox.setLayout(self.tab2_leftbox_layout)

        # Top
        self.tab2_leftbox_top = QWidget()
        self.tab2_leftbox_top_layout = QFormLayout()
        self.tab2_leftbox_top.setLayout(self.tab2_leftbox_top_layout)

        self.tab2_choose_option_workflow = choose_option(self.nf_settings_path, 'workflow')
        self.tab2_choose_option_parallell_msconvert = choose_option(self.nf_settings_path, 'parallell_msconvert')
        self.tab2_choose_option_profile = choose_option(self.sh_script_path, 'profile')

        # Always visible
        self.tab2_leftbox_top_layout.addRow(QLabel('Choose pipeline'), self.tab2_choose_option_workflow)
        self.tab2_leftbox_top_layout.addRow(QLabel('Enable parallell MSconvert'), self.tab2_choose_option_parallell_msconvert)
        self.tab2_leftbox_top_layout.addRow(QLabel('Profile'), self.tab2_choose_option_profile)
        self.tab2_leftbox_layout.addWidget(self.tab2_leftbox_top)

        # Bottom, these will be hidden or shown depending on profile option
        self.tab2_hidden = QWidget()
        self.tab2_hidden.hidden_object = True
        self.tab2_hidden_layout = QFormLayout()
        self.tab2_hidden.setLayout(self.tab2_hidden_layout)

        self.tab2_cluster_arguments = cluster_arguments("process.clusterOptions", self.nf_settings_path)
        self.tab2_cluster_queue = cluster_arguments("process.queue", self.nf_settings_path)
        self.tab2_parameter_msconvert_cpus = set_cpus("msconvert_cpus", self.nf_settings_path)
        self.tab2_parameter_msconvert_time = set_time("msconvert_time", self.nf_settings_path)
        self.tab2_parameter_quandenser_cpus = set_cpus("quandenser_cpus", self.nf_settings_path)
        self.tab2_parameter_quandenser_time = set_time("quandenser_time", self.nf_settings_path)
        self.tab2_parameter_tide_search_cpus = set_cpus("tide_search_cpus", self.nf_settings_path)
        self.tab2_parameter_tide_search_time = set_time("tide_search_time", self.nf_settings_path)
        self.tab2_parameter_triqler_cpus = set_cpus("triqler_cpus", self.nf_settings_path)
        self.tab2_parameter_triqler_time = set_time("triqler_time", self.nf_settings_path)

        # Hidden depending on setting
        self.tab2_hidden_layout.addRow(QLabel('Cluster arguments'), self.tab2_cluster_arguments)
        self.tab2_hidden_layout.addRow(QLabel('Cluster queue'), self.tab2_cluster_queue)
        self.tab2_hidden_layout.addRow(QLabel('MSconvert cpus'), self.tab2_parameter_msconvert_cpus)
        self.tab2_hidden_layout.addRow(QLabel('MSconvert time'), self.tab2_parameter_msconvert_time)
        self.tab2_hidden_layout.addRow(QLabel('Quandenser cpus'), self.tab2_parameter_quandenser_cpus)
        self.tab2_hidden_layout.addRow(QLabel('Quandenser time'), self.tab2_parameter_quandenser_time)
        self.tab2_hidden_layout.addRow(QLabel('Tide search cpus'), self.tab2_parameter_tide_search_cpus)
        self.tab2_hidden_layout.addRow(QLabel('Tide search time'), self.tab2_parameter_tide_search_time)
        self.tab2_hidden_layout.addRow(QLabel('Triqler cpus'), self.tab2_parameter_triqler_cpus)
        self.tab2_hidden_layout.addRow(QLabel('Triqler time'), self.tab2_parameter_triqler_time)
        self.tab2_leftbox_layout.addWidget(self.tab2_hidden)

        # Right box
        self.tab2_rightbox = QWidget()
        self.tab2_rightbox_layout = QHBoxLayout()
        self.tab2_rightbox.setLayout(self.tab2_rightbox_layout)

        self.tab2_workflow = workflow()
        self.tab2_rightbox_layout.addWidget(self.tab2_workflow)

        self.tab2_layout.addWidget(self.tab2_rightbox)

        # Combine
        self.tab2_layout.addWidget(self.tab2_leftbox)
        self.tab2_layout.addWidget(self.tab2_rightbox)

    def inittab3(self):
        self.tab3 = QWidget()
        self.tab3_layout = QFormLayout()
        self.tab3.setLayout(self.tab3_layout)

        self.tab3_msconvert_arguments = msconvert_arguments(self.nf_settings_path)
        self.tab3_parameter_max_missing = parameter_setter_single("max_missing", self.nf_settings_path)  # Quandenser
        self.tab3_parameter_missed_clevages = parameter_setter_single("missed_clevages", self.nf_settings_path)  # Crux
        self.tab3_parameter_precursor_window = parameter_setter_double("precursor_window", self.nf_settings_path)  # Crux
        self.tab3_parameter_fold_change_eval = parameter_setter_double("fold_change_eval", self.nf_settings_path)  # Triqler
        self.tab3_reset_button = reset_button(config_path)

        self.tab3_layout.addRow(QLabel('<b>MSconvert'), QLabel())
        self.tab3_layout.addRow(QLabel('MSconvert additional arguments'), self.tab3_msconvert_arguments)
        self.tab3_layout.addRow(QLabel('<b>Quandenser'), QLabel())
        self.tab3_layout.addRow(QLabel('Max missing'), self.tab3_parameter_max_missing)
        self.tab3_layout.addRow(QLabel('<b>Crux'), QLabel())
        self.tab3_layout.addRow(QLabel('Missed clevages'), self.tab3_parameter_missed_clevages)
        self.tab3_layout.addRow(QLabel('Precursor window'), self.tab3_parameter_precursor_window)
        self.tab3_layout.addRow(QLabel('<b>Triqler'), QLabel())
        self.tab3_layout.addRow(QLabel('Fold change evaluation'), self.tab3_parameter_fold_change_eval)
        self.tab3_layout.addWidget(self.tab3_reset_button)

    def inittab4(self):
        self.tab4 = QWidget()
        self.tab4_layout = QHBoxLayout()
        self.tab4.setLayout(self.tab4_layout)

        self.tab4_running_jobs = running_jobs(config_path + "/jobs.txt")

        self.tab4_layout.addWidget(self.tab4_running_jobs)

    def inittab5(self):
        self.tab5 = QWidget()
        self.tab5_layout = QVBoxLayout()
        self.tab5.setLayout(self.tab5_layout)
        self.tab5_about = about()
        self.tab5_layout.addWidget(self.tab5_about)

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

    def tab_changed(self, index):
        if self.tabs.tabText(index) == "Edit workflow":
            self.tab2_choose_option_profile.check_hidden()
        if self.tabs.tabText(index) == "Running jobs":
            self.tab4_running_jobs.update()

    """This is for loading and saving state of child widgets"""

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
