import os
from PySide2.QtWidgets import QTextBrowser, QTableWidget, QHeaderView, QTableWidgetItem, QPushButton, QApplication
import subprocess
from PySide2.QtGui import QColor
from PySide2.QtCore import QTimer, QThread, Signal
import time
import pdb

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser
from .kill_button import kill_button

class running_jobs(QTableWidget):

    def __init__(self, jobs_path):
        super(running_jobs,self).__init__(parent = None)
        self.jobs_path = jobs_path
        self.options = ['COMPLETED', 'FAILED', 'MISSING', 'KILLED']
        jobs = []
        for line in open(self.jobs_path, 'r'):
            job = line.split('\t')  # First is pid
            jobs.append(job)

        self.setRowCount(len(jobs))
        self.setColumnCount(5)
        # Fill all places so there are no "None" types in the table
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item = QTableWidgetItem()
                item.setText('')
                self.setItem(row, column, item)

        self.fix_header()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.worker = fetch_running()
        self.worker.job_done.connect(self.on_job_done)
        self.timer.start(10000)  # Update every 10 seconds

    def fix_header(self):
        self.header = self.horizontalHeader()
        self.setHorizontalHeaderLabels(["Pid", "Output path", "Started", "Running", "Kill"])
        self.header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def keyPressEvent(self, event):
        """Add functionallity to keyboard"""
        if event.key() == 16777221 or event.key() == 16777220:  # *.221 is right enter
            if len(self.selectedIndexes()) == 0:  # Quick check if anything is selected
                pass
            else:
                index = self.selectedIndexes()[0]  # Take last
                self.setCurrentCell(index.row() + 1, index.column())
        super().keyPressEvent(event)  # Propagate to built in methods

    def on_job_done(self, done_processes):
        self.clear()
        self.fix_header()
        # If more jobs than rows
        if len(self.jobs) >= self.rowCount():
            self.setRowCount(len(self.jobs))
            for row in range(self.rowCount()):
                for column in range(self.columnCount()):
                    item = QTableWidgetItem()
                    item.setText('')
                    self.setItem(row, column, item)    # Note: new rowcount here

        jobs_check_rows = []
        row = 0
        for job in self.jobs:
            if job in self.jobs_check:
                jobs_check_rows.append(row)
            job = [i.replace('\n', '') for i in job]
            for column in range(self.columnCount() - 1):
                item = self.item(row, column)
                if len(job) - 1 >= column:
                    if job[column] == 'COMPLETED':
                        item.setForeground(QColor(0,255,150))
                    elif job[column] in self.options:
                        item.setForeground(QColor(255,0,0))
                    else:
                        pass
                    item.setText(job[column])
            row += 1

        for job, out, row in zip(self.jobs_check, done_processes, jobs_check_rows):
            out = out.split('\t')
            second_last_item = self.item(row, self.columnCount() - 2)
            last_item = self.item(row, self.columnCount() - 1)
            if any("run_quandenser.sh" in line for line in out):
                second_last_item.setForeground(QColor('red'))
                second_last_item.setText("RUNNING")
            else:
                # Check stdout file
                label = check_stdout(job[1] + '/' + 'stdout.txt')
                if label == 'COMPLETED':
                    second_last_item.setForeground(QColor(0,255,150))
                else:
                    second_last_item.setForeground(QColor(255,0,0))
                second_last_item.setText(label)
                self.update_job_file(job, label)
            if second_last_item.text() == "RUNNING":
                button = kill_button(job[0], self.jobs_path, job)  # job[0] = pid
                self.setCellWidget(row,  self.columnCount() - 1, button)

    def update_job_file(self, job_done, label):
        with open(self.jobs_path, 'r') as jobfile:
            all_jobs = jobfile.readlines()

        for index, job in enumerate(all_jobs):
            if job == '\t'.join(job_done):
                job_done = '\t'.join(job_done).replace('\n', '')
                all_jobs[index] = job_done + '\t' + label + '\n'

        with open(self.jobs_path, 'w') as jobfile:
            for job in all_jobs:
                jobfile.write(job)

    def update(self):
        jobs = []
        jobs_check = []
        for line in reversed(list(open(self.jobs_path, 'r'))):
            job = line.split('\t')  # First is pid
            jobs.append(job)
            if job[-1].replace('\n', '') not in self.options:
                jobs_check.append(job)
        self.worker.jobs = jobs_check
        self.jobs = jobs
        self.jobs_check = jobs_check
        self.worker.start()

class fetch_running(QThread):

    job_done = Signal(list)

    def __init__(self):
        super(fetch_running,self).__init__(parent = None)
        self.jobs = []
        self.running = False

    def do_work(self):
        self.running = True
        processes = []
        for job in self.jobs:
            process = subprocess.Popen([f"ps ux | grep {job[0]}"],
                                        stdout=subprocess.PIPE,
                                        shell=True)
            processes.append(process)
        outputs = []
        for p in processes:
            out, err = p.communicate()  # Wait for process to terminate
            out = out.decode("utf-8")
            outputs.append(out)
        self.job_done.emit(outputs)
        self.running = False

    def run(self):
        self.do_work()

def check_stdout(stdout_file):
    try:
        with open(stdout_file, 'r') as f:
            all_lines = f.readlines()
    except Exception as e:
        return 'MISSING'
    error_substring = "Error executing process >"
    done_substring = "QUANDENSER PIPELINE COMPLETED"
    crashed = False
    completed = False
    for line in all_lines:
        if error_substring in line:
            crashed = True
        if done_substring in line:
            completed = True

    if crashed:
        return 'FAILED'
    elif completed:
        return 'COMPLETED'
    else:
        return "FAILED"
