from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel

from tab4.running_jobs import running_jobs

from custom_config_parser import custom_config_parser

def init_tab4(paths):
    tab4 = QWidget()
    tab4_layout = QHBoxLayout()
    tab4.setLayout(tab4_layout)

    tab4_running_jobs = running_jobs(paths['jobs'])

    tab4_layout.addWidget(tab4_running_jobs)
    return tab4
