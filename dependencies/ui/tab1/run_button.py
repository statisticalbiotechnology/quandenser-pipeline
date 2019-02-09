import os
import sys
from PySide2.QtWidgets import QPushButton, QTableWidget, QLineEdit, QMessageBox
from PySide2.QtCore import QCoreApplication
import subprocess
from shutil import copyfile
import time


# Custom parser for both sh files and nf configs
from ..custom_config_parser import custom_config_parser


class run_button(QPushButton):

    def __init__(self, nf_settings_path, sh_script_path, pipe_path):
        super(run_button,self).__init__(parent = None)
        self.setText('RUN')
        self.nf_settings_path = nf_settings_path
        self.sh_script_path = sh_script_path
        self.pipe_path = pipe_path
        self.setStyleSheet("background-color:grey")  # Change color depending on if you can run or not
        self.clicked.connect(self.run)

    def run(self):
        # Load settings
        self.pipe_parser = custom_config_parser()
        self.pipe_parser.load(self.pipe_path)
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.sh_parser = custom_config_parser()
        self.sh_parser.load(self.sh_script_path)

        # Read parent
        parent = self.parentWidget()

        # output directory
        children = parent.findChildren(QLineEdit)
        for child in children:  # This is so I can have whatever order in widgets I want
            if child.type == 'directory':
                break  # Will keep child

        # Change output parameters
        output_path = child.text()
        self.sh_parser.write("OUTPUT_PATH", output_path)  # In sh
        self.nf_settings_parser.write("params.output_path", output_path)  # In sh

        # Fix batch_file
        child = parent.findChildren(QTableWidget)[0]
        full_table = []
        for row in range(child.rowCount()):
            if not child.item(row, 0).text() == '' and not child.item(row, 1).text() == '':
                input_string = child.item(row, 0).text() + '\t' + child.item(row, 1).text() + '\n'
                full_table.append(input_string)
        with open(f"{output_path}/file_list.txt", 'w') as file:
            for line in full_table:
                file.write(line)
        batch_file_path = os.path.abspath("file_list.txt")
        self.nf_settings_parser.write("params.batch_file", batch_file_path)

        # Fix database file
        children = parent.findChildren(QLineEdit)
        for child in children:  # This is so I can have whatever order in widgets I want
            if child.type == 'file':
                break  # Will keep child
        database_path = child.text()
        self.nf_settings_parser.write("params.db", database_path)

        # Set pipe to launch nextflow pipeline
        self.pipe_parser.write('exit_code', '0', isString=False)
        QCoreApplication.quit()
