from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel

from tab5.about import about

from custom_config_parser import custom_config_parser

def init_tab5(paths):
    tab5 = QWidget()
    tab5_layout = QVBoxLayout()
    tab5.setLayout(tab5_layout)

    pipe_parser = custom_config_parser()
    pipe_parser.load(paths['pipe'])
    if pipe_parser.get('disable-opengl') in ['false', '']:
        tab5_about = about()
    else:
        tab5_about = tooltip_label("OpenGL disabled", "OpenGL disabled", style=True)
    tab5_layout.addWidget(tab5_about)
    return tab5
