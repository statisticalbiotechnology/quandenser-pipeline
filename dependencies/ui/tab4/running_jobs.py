import os
from PySide2.QtWidgets import QTextBrowser
import subprocess
from PySide2.QtGui import QColor


# Custom parser for both sh files and nf configs
from ..custom_config_parser import custom_config_parser

class running_jobs(QTextBrowser):

    def __init__(self, jobs_path):
        super(running_jobs,self).__init__(parent = None)
        self.jobs_path = jobs_path

    def update(self):
        self.clear()
        processes = []
        jobs = []
        for line in open(self.jobs_path, 'r'):
            job = line.split('\t')  # First is pid
            jobs.append(job)
            process = subprocess.Popen([f"ps aux | grep {job[0]}"],
                                        stdout=subprocess.PIPE,
                                        shell=True)
            processes.append(process)

        for job, process in zip(jobs, processes):
            out, err = process.communicate()  # Wait for process to terminate
            out = out.decode("utf-8")
            out = out.split('\t')
            if any("run_quandenser.sh" in line for line in out):
                self.setTextColor(QColor("red"))
                self.append(f"{job[0]} RUNNING {job[1]} {job[2]}")
            else:
                self.setTextColor(QColor("green"))
                self.append(f"{job[0]} COMPLETED {job[1]} {job[2]}")
