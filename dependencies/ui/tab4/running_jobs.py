import os
from PySide2.QtWidgets import QTextBrowser, QTableWidget, QHeaderView, QTableWidgetItem, QPushButton
import subprocess
from PySide2.QtGui import QColor
from PySide2.QtCore import QTimer

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser
from .kill_button import kill_button

class running_jobs(QTableWidget):

    def __init__(self, jobs_path):
        super(running_jobs,self).__init__(parent = None)
        self.jobs_path = jobs_path

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
        self.header = self.horizontalHeader()
        self.header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.setHorizontalHeaderLabels(["Pid", "Output path", "Started", "Running", "Kill"])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10000)  # Update every 10 seconds

    def keyPressEvent(self, event):
        """Add functionallity to keyboard"""
        if event.key() == 16777221 or event.key() == 16777220:  # *.221 is right enter
            if len(self.selectedIndexes()) == 0:  # Quick check if anything is selected
                pass
            else:
                index = self.selectedIndexes()[0]  # Take last
                self.setCurrentCell(index.row() + 1, index.column())
        super().keyPressEvent(event)  # Propagate to built in methods

    def update(self):
        processes = []
        jobs = []
        for line in open(self.jobs_path, 'r'):
            job = line.split('\t')  # First is pid
            jobs.append(job)
            process = subprocess.Popen([f"ps aux | grep {job[0]}"],
                                        stdout=subprocess.PIPE,
                                        shell=True)
            processes.append(process)

        # If more jobs than rows
        if len(jobs) >= self.rowCount():
            self.setRowCount(len(jobs))
            for row in range(self.rowCount()):
                for column in range(self.columnCount()):
                    item = QTableWidgetItem()
                    item.setText('')
                    self.setItem(row, column, item)    # Note: new rowcount here

        row = 0
        for job, process in zip(jobs, processes):
            out, err = process.communicate()  # Wait for process to terminate
            out = out.decode("utf-8")
            out = out.split('\t')
            for column in range(self.columnCount()):
                item = self.item(row, column)
                if column == self.columnCount() - 2:
                    if any("run_quandenser.sh" in line for line in out):
                        item.setForeground(QColor('red'))
                        item.setText("RUNNING")
                    else:
                        item.setForeground(QColor('green'))
                        item.setText("COMPLETED")
                elif column == self.columnCount() - 1:  # last columnt
                    if self.item(row, column - 1).text() == "RUNNING":
                        button = kill_button(job[0])  # job[0] = pid
                        self.setCellWidget(row, column, button)
                else:
                    item.setText(job[column].replace('\n', ''))

            row += 1
