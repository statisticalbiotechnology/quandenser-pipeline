import sys
from PySide2.QtWidgets import QLineEdit
from colorama import Fore
import re

# Custom parser for both sh files and nf configs
from custom_config_parser import custom_config_parser
from utils import ERROR

class set_time(QLineEdit):
    def __init__(self, process, nf_settings_path):
        super(set_time,self).__init__(parent = None)
        self.nf_settings_path = nf_settings_path
        self.nf_settings_parser = custom_config_parser()
        self.nf_settings_parser.load(self.nf_settings_path)
        self.process = process
        self.default()
        self.textChanged.connect(self.check_text)

    def check_text(self):
        self.blockSignals(True)
        time  = self.text()  # Copy, dont use
        nftime = self.time_to_nftime(time)
        additional_information = self.process.split('_')[0]  # Very hacky way of doing it, but it should be fine
        self.nf_settings_parser.write("time", nftime, additional_information=additional_information)  # Multiple time
        self.blockSignals(False)

    def time_to_nftime(self, time):
        parameters = time.split(':')  # Days, hours, minutes, seconds
        if len(parameters) >= 5:
            ERROR(f"too many values for time at {self.process}")
            return
        suffix = ['d', 'h', 'm', 's']
        suffix = suffix[-len(parameters):]
        nftime = ''
        for suffix, parameter in zip(suffix, parameters):
            try:
                nftime+=f"{int(parameter)}{suffix}"
            except:
                pass
        return nftime

    def nftime_to_time(self, nftime):
        suffix = ['d', 'h', 'm', 's']
        time_list = re.split('(\d+)', nftime)
        time_list.pop(0)  # First value is empty
        # [20, m, 10, s] ex
        time_values = ['00', '00', '00', '00']
        for group in zip(time_list[::2], time_list[1::2]):  # Group every other together
            index = suffix.index(group[1])
            value = group[0]
            if len(group[0]) == 1:
                value = '0' + value
            time_values[index] = value

        time = f"{time_values[0]}:{time_values[1]}:{time_values[2]}:{time_values[3]}"
        return time

    def default(self):
        additional_information = self.process.split('_')[0]  # Very hacky way of doing it, but it should be fine
        nftime = self.nf_settings_parser.get("time", additional_information=additional_information)  # Multiple time
        time = self.nftime_to_time(nftime)
        self.setText(time)
