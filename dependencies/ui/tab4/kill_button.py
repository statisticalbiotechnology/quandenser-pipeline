import os
from PySide2.QtWidgets import QPushButton
import subprocess
from colorama import Fore, Back, Style

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
        # Get pgid
        pgid = os.getpgid(int(self.pid))
        process = subprocess.Popen([f"kill -15 -{pgid} && echo KILLED PROCESS"],  # Will kill all with pgid aka whole tree
                                    stdout=subprocess.PIPE,
                                    shell=True)
        out, err = process.communicate()  # Wait for process to terminate
        out = out.decode("utf-8")
        out = out.split('\t')
        killed = False
        for line in out:
            if "KILLED PROCESS" in line:
                killed = True
        if killed:
            print(Fore.RED + f"Killed process with pid {self.pid} and its children" + Fore.RESET)
            self.update_job_file(self.job, 'KILLED')
        else:
            print(Fore.RED + f"FAILED to kill process with pid {self.pid} and its children. Are you on the same login node?" + Fore.RESET)
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
