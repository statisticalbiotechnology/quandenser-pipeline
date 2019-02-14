import sys
from PySide2.QtWidgets import QLineEdit
from colorama import Fore

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser

class set_time(QLineEdit):
    def __init__(self, process, nf_settings_path):
        super(set_time,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.process = process
        if self.process == 'msconvert_time':
            self.setText('0:00:15:00')
        elif self.process == 'quandenser_time':
            self.setText('0:03:00:00')
        elif self.process == 'tide_search_time':
            self.setText('0:00:05:00')
        elif self.process == 'triqler_time':
            self.setText('0:00:10:00')
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        time  = self.text()  # Copy, dont use
        parameters = time.split(':')  # Days, hours, minutes, seconds
        if len(parameters) >= 5:
            print(Fore.RED + f"ERROR, too many values for time at {self.process}" + Fore.RESET)
            return
        suffix = ['d', 'h', 'm', 's']
        suffix = suffix[-len(parameters):]

        nf_time = ''
        for suffix, parameter in zip(suffix, parameters):
            try:
                nf_time+=f"{int(parameter)}{suffix}"
            except:
                pass
        additional_information = self.process.split('_')[0]  # Very hacky way of doing it, but it should be fine
        self.nf_settings_parser.write("time", nf_time, additional_information=additional_information)  # Multiple time
        self.blockSignals(False)
