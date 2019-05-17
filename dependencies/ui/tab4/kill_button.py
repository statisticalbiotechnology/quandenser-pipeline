import os
from PySide2.QtWidgets import QPushButton
import subprocess
from colorama import Fore, Back, Style
import psutil

class kill_button(QPushButton):

    def __init__(self, pid, jobs_path, job):
        super(kill_button,self).__init__(parent = None)
        self.setText('KILL')
        self.pid = pid  # will use pid as ppid
        self.jobs_path = jobs_path
        self.job = job
        self.setStyleSheet("background-color:red")  # Change color depending on if you can run or not
        self.clicked.connect(self.kill)

    def kill(self):
        # pgid = os.getpgid(int(self.pid))  # Can sometimes kill gui, not good enough
        p = psutil.Process(int(self.pid))
        children = p.children(recursive=True)
        for child in children:
            child.kill()
        print(Fore.RED + f"Killed process with pid {self.pid} and its children" + Fore.RESET)
        self.update_job_file(self.job, 'KILLED')
        parent = self.parentWidget()
        children = parent.children()
        for child in children:
            if hasattr(child, 'update'):
                child.update()
                break
        return 0

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
