import os
import sys
from PySide2.QtWidgets import QPushButton, QTableWidget, QLineEdit, QMessageBox
from PySide2.QtCore import QCoreApplication
import subprocess
from shutil import copyfile
import time
from colorama import Fore, Back, Style
import secrets
import re

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser
from utils import ERROR

class run_button(QPushButton):

    def __init__(self, nf_settings_path, sh_script_path, pipe_path):
        super(run_button,self).__init__(parent = None)
        self.setText('RUN')
        self.nf_settings_path = nf_settings_path
        self.sh_script_path = sh_script_path
        self.pipe_path = pipe_path
        #self.setStyleSheet("background-color:grey")  # Change color depending on if you can run or not
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
        if not os.path.isdir(output_path):
            ERROR('Not a valid output path')
            return 1

        self.sh_parser.write("OUTPUT_PATH", output_path)  # In sh
        self.nf_settings_parser.write("params.output_path", output_path)  # In sh

        # Check if label has been set
        label = self.sh_parser.get('OUTPUT_PATH_LABEL')
        if label != '':
            label = re.sub("_*", '', label)  # Remove previous indexing
            index = 0
            while True:
                if os.path.isdir(output_path + label + "_" + str(index)):
                    index += 1
                else:
                    label = label + "_" + str(index)
                    self.nf_settings_parser.write("params.output_label", label)
                    self.sh_parser.write('OUTPUT_PATH_LABEL', label)
                    break

        # Fix batch_file
        child = parent.findChildren(QTableWidget)[0]
        full_table = []
        for row in range(child.rowCount()):
            if not child.item(row, 0).text() == '':
                if not os.path.isfile(child.item(row, 0).text()):
                    ERROR(f"File in row {row} does not exist")
                    return 1
                elif self.nf_settings_parser.get('params.workflow') == "MSconvert" and child.item(row, 1).text() == '':
                    label = 'A'  # Add junk labeling
                elif child.item(row, 1).text() == '' and self.nf_settings_parser.get('params.workflow') == "Full":
                    ERROR(f"File in row {row} is missing a label (Full workflow enabled)")
                    return 1
                elif child.item(row, 1).text() != '':
                    label = child.item(row, 1).text()
                input_string = child.item(row, 0).text() + '\t' + label + '\n'
                full_table.append(input_string)

        if full_table == []:
            ERROR('No files choosen')
            return 1

        with open(f"{output_path}/file_list.txt", 'w') as file:
            for line in full_table:
                file.write(line)
        batch_file_path = f"{output_path}/file_list.txt"
        self.nf_settings_parser.write("params.batch_file", batch_file_path)

        # Fix database file
        children = parent.findChildren(QLineEdit)
        for child in children:  # This is so I can have whatever order in widgets I want
            if child.type == 'file':
                break  # Will keep child
        database_path = child.text()
        self.nf_settings_parser.write("params.db", database_path)
        workflow = self.nf_settings_parser.get("params.workflow")
        if workflow == "Full" and not os.path.isfile(database_path):
            ERROR("You must choose an database if you are running the full pipeline")
            return 1

        # Custom mounts
        custom_mounts = self.pipe_parser.get('custom_mounts').replace('\r', '').replace('\n', '')
        self.nf_settings_parser.write('params.custom_mounts', custom_mounts)

        # Generate random hash for nextflow
        random_hash = secrets.token_urlsafe(16)
        self.nf_settings_parser.write('params.random_hash', random_hash)

        # Set pipe to launch nextflow pipeline
        self.pipe_parser.write('exit_code', '0', isString=False)
        self.window().close()
