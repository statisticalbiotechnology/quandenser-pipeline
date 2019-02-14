import os
from PySide2.QtWidgets import QPushButton
import subprocess
from colorama import Fore, Back, Style

class kill_button(QPushButton):

    def __init__(self, pid):
        super(kill_button,self).__init__(parent = None)
        self.setText('KILL')
        self.ppid = pid  # will use pid as ppid
        self.setStyleSheet("background-color:red")  # Change color depending on if you can run or not
        self.clicked.connect(self.kill)

    def kill(self):
        process = subprocess.Popen([f"pkill -15 -P {self.ppid}"],
                                    stdout=subprocess.PIPE,
                                    shell=True)
        print(Fore.RED + f"Killed process with pid {self.ppid} and its children" + Fore.RESET)
        parent = self.parentWidget()
        children = parent.children()
        for child in children:
            if hasattr(child, 'update'):
                child.update()
                break
        return 0
