import os
from PySide2.QtWidgets import QPushButton, QTableWidget, QLineEdit, QMessageBox
import subprocess
from shutil import copyfile
import time

class run_button(QPushButton):

    def __init__(self, nf_settings_path, sh_script_path):
        super(run_button,self).__init__(parent = None)
        self.setText('RUN')
        self.nf_settings_path = nf_settings_path
        self.sh_script_path = sh_script_path
        self.setStyleSheet("background-color:blue")  # Change color depending on if you can run or not
        self.clicked.connect(self.run)

    def run(self):
        # Load settings
        setting_contents = []
        for line in open(self.nf_settings_path, 'r'):
            setting_contents.append(line)

        # Load sh file
        sh_contents = []
        for line in open(self.sh_script_path, 'r'):
            sh_contents.append(line)

        # Read parent
        parent = self.parentWidget()

        # batch_file
        child = parent.findChildren(QTableWidget)[0]
        full_table = []
        for row in range(child.rowCount()):
            if not child.item(row, 0).text() == '' and not child.item(row, 1).text() == '':
                input_string = child.item(row, 0).text() + '\t' + child.item(row, 1).text() + '\n'
                full_table.append(input_string)

        with open("file_list.txt", 'w') as file:
            for line in full_table:
                file.write(line)

        index = [setting_contents.index(i) for i in setting_contents if i.startswith("params.batch_file")][0]
        batch_file_path = os.path.abspath("file_list.txt")
        setting_contents[index] = f'params.batch_file = "{batch_file_path}"\n'  # Need \n

        # database file
        children = parent.findChildren(QLineEdit)
        for child in children:  # This is so I can have whatever order in widgets I want
            if child.type == 'file':
                break  # Will keep child
        database_path = child.text()
        index = [setting_contents.index(i) for i in setting_contents if i.startswith("params.db")][0]
        setting_contents[index] = f'params.db = "{database_path}"\n'  # Need to add \n here

        # output directory
        children = parent.findChildren(QLineEdit)
        for child in children:  # This is so I can have whatever order in widgets I want
            if child.type == 'directory':
                break  # Will keep child
        output_path = child.text()

        # Change sh
        index = [sh_contents.index(i) for i in sh_contents if i.startswith("OUTPUT_PATH")][0]
        sh_contents[index] = f'OUTPUT_PATH="{output_path}"\n'  # Need to add \n here

        # Change .config
        index = [setting_contents.index(i) for i in setting_contents if i.startswith("params.output_path")][0]
        setting_contents[index] = f'params.output_path = "{output_path}"\n'  # Need to add \n here

        # Rewrite settings
        with open(self.nf_settings_path, 'w') as file:
            for line in setting_contents:
                file.write(line)

        # Rewrite sh file
        with open(self.sh_script_path, 'w') as file:
            for line in sh_contents:
                file.write(line)

        # Run quandenser
        """
        process = subprocess.Popen(['./run_quandenser.sh & echo "PID is $!"'],
                                    stdout=subprocess.PIPE,
                                    shell=True)
        line_counter = 0
        while True:
          line = process.stdout.readline()
          print(line)
          if b"PID" in line:
              pid = line.decode("utf-8") .replace('\n', '')
              break
          else:
            line_counter += 1
            if line_counter > 20:
                pid = "ERROR"
                break
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Successful start")
        msg.setText("Started Quandenser")
        msg.setInformativeText("You can close the GUI, the process will continue in the background")
        msg.setDetailedText(f"PID of the process is: {pid}")
        msg.exec_()
