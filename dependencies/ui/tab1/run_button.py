import os
from PySide2.QtWidgets import QPushButton, QTableWidget, QLineEdit, QMessageBox
import subprocess
from shutil import copyfile
import time


# Custom parser for both sh files and nf configs
from ..custom_config_parser import custom_config_parser


class run_button(QPushButton):

    def __init__(self, nf_settings_path, sh_script_path):
        super(run_button,self).__init__(parent = None)
        self.setText('RUN')
        self.nf_settings_path = nf_settings_path
        self.sh_script_path = sh_script_path
        self.setStyleSheet("background-color:grey")  # Change color depending on if you can run or not
        self.clicked.connect(self.run)

    def run(self):
        # Load settings
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)

        self.sh_parser = custom_config_parser()
        self.sh_parser.load(self.sh_script_path)

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

        batch_file_path = os.path.abspath("file_list.txt")
        self.nf_settings_parser.write("params.batch_file", batch_file_path)

        # database file
        children = parent.findChildren(QLineEdit)
        for child in children:  # This is so I can have whatever order in widgets I want
            if child.type == 'file':
                break  # Will keep child

        database_path = child.text()
        self.nf_settings_parser.write("params.db", database_path)

        # output directory
        children = parent.findChildren(QLineEdit)
        for child in children:  # This is so I can have whatever order in widgets I want
            if child.type == 'directory':
                break  # Will keep child

        # Change output parameters
        output_path = child.text()
        self.sh_parser.write("OUTPUT_PATH", output_path)  # In sh
        self.nf_settings_parser.write("params.output_path", output_path)  # In sh

        # Run quandenser
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

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Successful start")
        msg.setText("Started Quandenser")
        msg.setInformativeText("You can close the GUI, the process will continue in the background")
        msg.setDetailedText(f"PID of the process is: {pid}")
        msg.exec_()
