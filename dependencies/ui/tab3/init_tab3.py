from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel

from tab3.additional_arguments import additional_arguments
from tab3.parameter_setter import parameter_setter_double, parameter_setter_single
from tab3.reset_button import reset_button

from custom_config_parser import custom_config_parser

def init_tab3(paths):
    tab3 = QWidget()
    tab3_layout = QFormLayout()
    tab3.setLayout(tab3_layout)

    tab3_msconvert_arguments = additional_arguments(paths['nf'], type='msconvert_additional_arguments')
    tab3_parameter_max_missing = parameter_setter_single("max_missing", paths['nf'])  # Quandenser
    tab3_quandenser_arguments = additional_arguments(paths['nf'], type='quandenser_additional_arguments')
    tab3_parameter_missed_clevages = parameter_setter_single("missed_clevages", paths['nf'])  # Crux
    tab3_parameter_precursor_window = parameter_setter_double("precursor_window", paths['nf'])  # Crux
    tab3_crux_arguments = additional_arguments(paths['nf'], type='crux_index_additional_arguments')
    tab3_crux_index_arguments = additional_arguments(paths['nf'], type='crux_index_additional_arguments')
    tab3_crux_search_arguments = additional_arguments(paths['nf'], type='crux_search_additional_arguments')
    tab3_crux_percolator_arguments = additional_arguments(paths['nf'], type='crux_percolator_additional_arguments')
    tab3_parameter_fold_change_eval = parameter_setter_double("fold_change_eval", paths['nf'])  # Triqler
    tab3_triqler_arguments = additional_arguments(paths['nf'], type='triqler_additional_arguments')
    tab3_reset_button = reset_button(paths['config'])

    tab3_layout.addRow(QLabel('<b>MSconvert'), QLabel())
    tab3_layout.addRow(QLabel('MSconvert additional arguments'), tab3_msconvert_arguments)
    tab3_layout.addRow(QLabel('<b>Quandenser'), QLabel())
    tab3_layout.addRow(QLabel('Max missing'), tab3_parameter_max_missing)
    tab3_layout.addRow(QLabel('Quandenser additional arguments'), tab3_quandenser_arguments)
    tab3_layout.addRow(QLabel('<b>Crux'), QLabel())
    tab3_layout.addRow(QLabel('Missed clevages'), tab3_parameter_missed_clevages)
    tab3_layout.addRow(QLabel('Precursor window'), tab3_parameter_precursor_window)
    tab3_layout.addRow(QLabel('Crux indexing additional arguments'), tab3_crux_index_arguments)
    tab3_layout.addRow(QLabel('Crux search additional arguments'), tab3_crux_search_arguments)
    tab3_layout.addRow(QLabel('Crux percolator additional arguments'), tab3_crux_percolator_arguments)
    tab3_layout.addRow(QLabel('<b>Triqler'), QLabel())
    tab3_layout.addRow(QLabel('Fold change evaluation'), tab3_parameter_fold_change_eval)
    tab3_layout.addRow(QLabel('Triqler additional arguments'), tab3_triqler_arguments)
    tab3_layout.addWidget(tab3_reset_button)
    return tab3
