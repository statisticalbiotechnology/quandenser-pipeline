import os
from PySide2.QtWidgets import QPushButton, QDoubleSpinBox, QSpinBox
import shutil
from colorama import Fore

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser
from utils import ERROR

class reset_button(QPushButton):

    def __init__(self, config_path):
        super(reset_button,self).__init__(parent = None)
        self.setText('Restore settings to default')
        self.config_path = config_path
        #self.setStyleSheet("background-color:grey")  # Change color depending on if you can run or not
        self.clicked.connect(self.reset)

    def reset(self):
        files = ["ui.config",
                 "nf.config",
                 "run_quandenser.sh"]
        for file in files:
            print(Fore.YELLOW + f"Replaced {file}" + Fore.RESET)
            os.remove(f"{self.config_path}/{file}")
            shutil.copyfile(f"config/{file}", f"{self.config_path}/{file}")
            os.chmod(f"{self.config_path}/{file}", 0o700)  # Only user will get access

        nf_parser = custom_config_parser()
        nf_parser.load(self.config_path + "/nf.config")

        # Read parent
        window = self.window()
        self.recurse_children(window)

    def recurse_children(self, parent):
        children = parent.children()
        if children == []:
            return
        for child in children:
            if hasattr(child, 'default'):
                child.default()
            self.recurse_children(child)  # WE HAVE TO GO DEEPER!
