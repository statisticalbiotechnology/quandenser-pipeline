# System
import sys
import os
import shutil

# PySide2 imports
from PySide2.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTabWidget
from PySide2.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout, QApplication
from PySide2.QtWidgets import QLabel, QMainWindow, QComboBox, QTextEdit, QTableWidget, QMessageBox
#from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PySide2.QtGui import QIcon
from PySide2 import QtCore

# Widgets
from ui.tab1.file_chooser import file_chooser
from ui.tab1.file_viewer import file_viewer
from ui.tab1.batch_file_viewer import batch_file_viewer
from ui.tab1.run_button import run_button
#from ui.tab2.workflow import workflow
from ui.tab2.choose_option import choose_option
from ui.tab3.msconvert_arguments import msconvert_arguments
from ui.tab5.about import about

# Custom parser
from ui.custom_config_parser import custom_config_parser

def check_corrupt(user):
    # Check for corrupt files
    if not os.path.isdir(f"/var/tmp/quandenser_pipeline_{user}"):
        print("""Missing config directory in /var/tmp. Initalizing directory""")
        os.makedirs(f"/var/tmp/quandenser_pipeline_{user}")
        print(f"/var/tmp/quandenser_pipeline_{user} created")
    if not os.path.isfile(f"/var/tmp/quandenser_pipeline_{user}/ui.config"):
        print("Missing UI config. Creating file")
        shutil.copyfile("config/ui.config", f"/var/tmp/quandenser_pipeline_{user}/ui.config")
    if not os.path.isfile(f"/var/tmp/quandenser_pipeline_{user}/nf.config"):
        print("Missing NF config. Creating file")
        shutil.copyfile("config/nf.config", f"/var/tmp/quandenser_pipeline_{user}/nf.config")
    if not os.path.isfile(f"/var/tmp/quandenser_pipeline_{user}/PIPE"):
        print("Missing PIPE. Creating file")
        shutil.copyfile("config/PIPE", f"/var/tmp/quandenser_pipeline_{user}/PIPE")
    if not os.path.isfile(f"/var/tmp/quandenser_pipeline_{user}/jobs.txt"):
        print("Missing running jobs file. Adding file")
        job_file = open(f"/var/tmp/quandenser_pipeline_{user}/jobs.txt", 'w')
        job_file.close()
    if not os.path.isfile(f"/var/tmp/quandenser_pipeline_{user}/run_quandenser.sh"):
        print("Missing run script. Adding file")
        shutil.copyfile("config/run_quandenser.sh", f"/var/tmp/quandenser_pipeline_{user}/run_quandenser.sh")
    if not os.path.isfile(f"/var/tmp/quandenser_pipeline_{user}/run_quandenser.nf"):
        print("Missing NF pipeline. Adding file")
        shutil.copyfile("config/run_quandenser.nf", f"/var/tmp/quandenser_pipeline_{user}/run_quandenser.nf")

def check_running(user, exit_code):
    pipe_parser = custom_config_parser()
    pipe_parser.load(f"/var/tmp/quandenser_pipeline_{user}/PIPE")
    pid = pipe_parser.get("pid")
    if exit_code != 0:  # If not started process
        return
    if pid != "":
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Critical fail")
        msg.setText("Unable to start quandenser. Check console output for more information")
        msg.exec_()
    else:
        with open(f"/var/tmp/quandenser_pipeline_{user}/jobs.txt", 'a') as job_file:
            job_file.write(pid)
        pipe_parser.write('pid', '', isString=False)  # Reset pid
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Successful start")
        msg.setText("Quandenser successfully started")
        msg.setDetailedText(f"PID of the process is: {pid}")
        msg.exec_()

class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Quandenser-pipeline'
        self.setWindowIcon(QIcon('ui/quandenser_icon.jpg'))
        self.left = 10
        self.top = 10
        self.WIDTH = 600
        self.HEIGHT = 400

        # Read user
        self.user = os.environ.get('USER')

        # Check file integrety
        check_corrupt(self.user)
        self.ui_settings_path = f"/var/tmp/quandenser_pipeline_{self.user}/ui.config"
        self.nf_settings_path = f"/var/tmp/quandenser_pipeline_{self.user}/nf.config"
        self.sh_script_path = f"/var/tmp/quandenser_pipeline_{self.user}/run_quandenser.sh"
        self.pipe_path = f"/var/tmp/quandenser_pipeline_{self.user}/PIPE"

        # Open pipe and read
        self.pipe_parser = custom_config_parser()
        self.pipe_parser.load(self.pipe_path)
        self.exit_code = int(self.pipe_parser.get('exit_code'))
        self.pipe_parser.write('exit_code', '2', isString=False)  # Add error code 2. If we manage to load, change to 1
        check_running(self.user, self.exit_code)

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

        self.inittab1()  # Init tab1
        self.inittab2()  # Tab 2
        self.inittab3()  # Tab 3
        self.inittab4()  # Tab 4
        self.inittab5()  # Tab 5

        # Add the tabs
        self.tabs.addTab(self.tab1, "MS files")
        self.tabs.addTab(self.tab2, "Edit workflow")
        self.tabs.addTab(self.tab3, "Advanced Settings")
        self.tabs.addTab(self.tab4, "MSconvert")
        self.tabs.addTab(self.tab5, "About")
        self.setCentralWidget(self.tabs)
        self.show()

    def inittab1(self):
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)

        # Widgets in leftbox
        self.fasta_chooser = file_chooser(type='fasta')
        self.database_viewer = file_viewer(type='file')
        self.ms_chooser = file_chooser(type='ms')
        self.batch_file_viewer = batch_file_viewer()
        self.output_chooser = file_chooser(type='directory')
        self.output_viewer = file_viewer(type='directory')
        self.run_button = run_button(self.nf_settings_path, self.sh_script_path, self.pipe_path)

        self.tab1_layout.addWidget(self.fasta_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.database_viewer)
        self.tab1_layout.addWidget(self.ms_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.batch_file_viewer)
        self.tab1_layout.addWidget(self.output_chooser, 0, QtCore.Qt.AlignCenter)
        self.tab1_layout.addWidget(self.output_viewer)
        self.tab1_layout.addWidget(self.run_button)

    def inittab2(self):
        self.tab2 = QWidget()
        self.tab2_layout = QHBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        # Left box
        self.leftbox = QWidget()
        self.leftbox_layout = QFormLayout()
        self.leftbox.setLayout(self.leftbox_layout)
        self.choose_option_workflow = choose_option(self.nf_settings_path, 'workflow')
        self.choose_option_parallell_msconvert = choose_option(self.nf_settings_path, 'parallell_msconvert')

        self.leftbox_layout.addRow(QLabel('Choose pipeline'), self.choose_option_workflow)
        self.leftbox_layout.addRow(QLabel('Enable parallell MSconvert'), self.choose_option_parallell_msconvert)

        # Right box
        self.rightbox = QWidget()
        self.rightbox_layout = QHBoxLayout()
        self.rightbox.setLayout(self.rightbox_layout)

        self.workflow = workflow()
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

        # Clean exit
        exit_code = int(self.pipe_parser.get('exit_code'))
        if exit_code == 0:  # This means that it had been modified during runtime --> run button has been pressed
            pass
        else:
            self.pipe_parser.write('exit_code', '1', isString=False)


    """This is for loading and saving state of child widgets"""

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
            state_name = ''   # This is so you can have multiple of same type of widget
            if hasattr(child, 'type'):
                state_name += "_" + str(child.type)
            if hasattr(child, 'id'):
                state_name += "_" + str(child.id)
            child_name = f"State_{child.__class__.__name__}" + state_name
            if save:
                self.settings_obj.setValue(child_name, child.text())
            else:
                if self.settings_obj.value(child_name) is None:
                    return
                else:
                    child.setText(self.settings_obj.value(child_name))
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
