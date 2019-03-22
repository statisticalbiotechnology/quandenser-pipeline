from colorama import Fore, Back, Style
import datetime
import time
import os
import shutil
import filecmp
from PySide2.QtWidgets import QMessageBox

# Custom parser
from custom_config_parser import custom_config_parser

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
    installed_parser = custom_config_parser()
    packed_parser = custom_config_parser()

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
    for file in files:
        corrupted = False
        if not os.path.isfile(f"{config_path}/{file}"):
            WARNING(f"Missing file {file}. Installing file")
            shutil.copyfile(f"config/{file}", f"{config_path}/{file}")
            os.chmod(f"{config_path}/{file}", 0o700)  # Only user will get access
        else:  # check corrupt/old versions of config
            if (file.split('.')[-1] in ['config', 'sh'] or file == 'PIPE') and file != 'ui.config':
                installed_parser.load(f"{config_path}/{file}")
                installed_parameters = installed_parser.get_params()
                packed_parser.load(f"config/{file}")
                packed_parameters = packed_parser.get_params()
                if not installed_parameters == packed_parameters:
                    corrupted = True
            elif file == "nf.config":  # Check for old versions
                lines = open(f"{config_path}/{file}", 'r').readlines()
                if not any("slurm_cluster" in line for line in lines):  # Very specific
                    corrupted=True
            else:
                if not filecmp.cmp(f"{config_path}/{file}", f"config/{file}") and file not in ['ui.config', 'jobs.txt']:  # check if files are the same
                    corrupted = True

        if corrupted:
            WARNING(f"Detected old or corrupt version of {file}. Replacing file")
            os.remove(f"{config_path}/{file}")
            shutil.copyfile(f"config/{file}", f"{config_path}/{file}")
            os.chmod(f"{config_path}/{file}", 0o700)  # Only user will get access

def check_running(config_path):
    pipe_parser = custom_config_parser()
    pipe_parser.load(f"{config_path}/PIPE")
    sh_parser = custom_config_parser()
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
            crash = False
            time.sleep(2)  # Wait 2 seconds for initalizing
            try:
                with open(output_path + '/' + 'stdout.txt', 'r') as stdout_file:
                    all_lines = stdout_file.readlines()
                    for line in all_lines:
                        if "Error executing process" in line:
                            crash = True
                    if len(all_lines) == 0:  # File doesn't exist/not started
                        crash = True
            except Exception as e:
                print(e)
                crash = True

            msg = QMessageBox()
            if not crash:
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Started")
                msg.setText("Quandenser started")
                msg.setDetailedText(f"PID of the process is: {pid}")
            else:
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Nextflow crash")
                msg.setText(f"Something went wrong after nextflow was started. Please look in stdout.txt at \n{output_path}")
            msg.exec_()
