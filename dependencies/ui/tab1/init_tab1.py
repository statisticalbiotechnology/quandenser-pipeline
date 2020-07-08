from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QVBoxLayout

from tab1.file_chooser import file_chooser
from tab1.file_viewer import file_viewer
from tab1.batch_file_viewer import batch_file_viewer
from tab1.run_button import run_button

def init_tab1(paths):
    tab1 = QWidget()
    tab1_layout = QVBoxLayout()
    tab1.setLayout(tab1_layout)

    # Widgets in leftbox
    tab1_fasta_chooser = file_chooser(paths['pipe'], type='fasta')
    tab1_database_viewer = file_viewer(type='file')
    tab1_ms_chooser = file_chooser(paths['pipe'], type='ms')
    tab1_batch_file_viewer = batch_file_viewer(paths['nf'])
    tab1_output_chooser = file_chooser(paths['pipe'], type='directory')
    tab1_output_viewer = file_viewer(type='directory')
    tab1_run_button = run_button(paths['nf'], paths['sh'], paths['pipe'], paths['config'])

    tab1_layout.addWidget(tab1_fasta_chooser, 0, QtCore.Qt.AlignCenter)
    tab1_layout.addWidget(tab1_database_viewer)
    tab1_layout.addWidget(tab1_ms_chooser, 0, QtCore.Qt.AlignCenter)
    tab1_layout.addWidget(tab1_batch_file_viewer)
    tab1_layout.addWidget(tab1_output_chooser, 0, QtCore.Qt.AlignCenter)
    tab1_layout.addWidget(tab1_output_viewer)
    tab1_layout.addWidget(tab1_run_button)
    return tab1
