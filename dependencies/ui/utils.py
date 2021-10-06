from colorama import Fore, Back, Style
import datetime
import time
import os
import shutil
import filecmp
from PySide2.QtWidgets import QMessageBox
import json

# Custom parser
import custom_config_parser as custom_config_parser
from tooltip_label import tooltip_label

def ERROR(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("ERROR")
    msg.setText(message)
    msg.exec_()

def WARNING(message):
    print(Fore.YELLOW + f"WARNING: {message}" + Fore.RESET)

def check_corrupt(config_path):
    # Check for corrupt files/old/missing
    installed_parser = custom_config_parser.custom_config_parser()
    packed_parser = custom_config_parser.custom_config_parser()

    if not os.path.isdir(f"{config_path}"):
        WARNING(f"Missing config directory {config_path}. Initalizing directory")
        os.makedirs(config_path)

    files = ["ui.config",
             "nf.config",
             "PIPE",
             "jobs.txt",
             "run_quandenser.nf",
             "run_quandenser.sh",
             "nextflow"]
    for f in files:
        corrupted = False
        if not os.path.isfile(f"{config_path}/{f}"):
            WARNING(f"Missing file {f}. Installing file")
            shutil.copyfile(f"config/{f}", f"{config_path}/{f}")
            os.chmod(f"{config_path}/{f}", 0o700)  # Only user will get access
            if f == "run_quandenser.sh":
                # CONFIG DIRECTORY #
                sh_parser = custom_config_parser.custom_config_parser()
                sh_parser.load(f"{config_path}/{f}")
                sh_parser.write("CONFIG_LOCATION", f"{config_path}")  # In sh
        else:  # check corrupt/old versions of config
            if (f.split('.')[-1] in ['config', 'sh'] or f == 'PIPE') and f != 'ui.config':
                installed_parser.load(f"{config_path}/{f}")
                installed_parameters = installed_parser.get_params()
                packed_parser.load(f"config/{f}")
                packed_parameters = packed_parser.get_params()
                if not installed_parameters == packed_parameters:
                    corrupted = True
            elif f == "nf.config":  # Check for old versions
                lines = open(f"{config_path}/{f}", 'r').readlines()
                if not any("slurm_cluster" in line for line in lines):  # Very specific
                    corrupted=True
            else:
                if not filecmp.cmp(f"{config_path}/{f}", f"config/{f}") and f not in ['ui.config', 'jobs.txt']:  # check if files are the same
                    corrupted = True

        if corrupted:
            WARNING(f"Detected old or corrupt version of {f}. Replacing file")
            os.remove(f"{config_path}/{f}")
            shutil.copyfile(f"config/{f}", f"{config_path}/{f}")
            os.chmod(f"{config_path}/{f}", 0o700)  # Only user will get access

def check_running(config_path):
    pipe_parser = custom_config_parser.custom_config_parser()
    pipe_parser.load(f"{config_path}/PIPE")
    sh_parser = custom_config_parser.custom_config_parser()
    sh_parser.load(f"{config_path}/run_quandenser.sh")

    exit_code = int(pipe_parser.get("exit_code"))
    if pipe_parser.get("started") == "true":
        pipe_parser.write("started", "")  # Reset
        pid = pipe_parser.get("pid")
        output_path = sh_parser.get("OUTPUT_PATH")
        output_label = sh_parser.get("OUTPUT_PATH_LABEL")
        output_path = output_path + output_label
        if pid == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Critical fail")
            msg.setText(f"Unable to start nextflow. Check console output or stdout.txt at \n{output_path}\nfor more information")
            msg.exec_()
        else:
            now = datetime.datetime.now()
            with open(f"{config_path}/jobs.txt", 'a') as job_file:
                job_file.write(pid + '\t' + output_path + '\t' + now.strftime("%Y-%m-%d %H:%M") + ' ' + time.localtime().tm_zone + '\n')
            pipe_parser.write('pid', '', isString=False)  # Reset pid
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Started")
            msg.setText("Quandenser started")
            msg.setDetailedText(f"PID of the process is: {pid}")
            msg.exec_()

def get_tooltip(key):
    with open('tooltips.json') as infile:
        tooltip_dict = json.load(infile)
    text, tooltip = tooltip_dict[key][0], tooltip_dict[key][1]
    return tooltip_label(text, tooltip)

def dump_tooltip(key, text, tooltip):
    with open('tooltips.json') as infile:
        tooltip_dict = json.load(infile)
    tooltip_dict[key] = [text, tooltip]
    with open('tooltips.json', 'w') as outfile:
        json.dump(tooltip_dict, outfile)
