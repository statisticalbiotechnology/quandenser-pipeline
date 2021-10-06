from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QLineEdit

from tab3.additional_arguments import additional_arguments
from tab3.parameter_setter import parameter_setter_double, parameter_setter_single
from tab3.reset_button import reset_button
from tab3.label_writer import label_writer
from tab3.resume_chooser import resume_chooser
from tab3.resume_folder_viewer import resume_folder_viewer
from tab3.choose_option import choose_option
from tab3.publish_checkbox import publish_checkbox

from custom_config_parser import custom_config_parser
from tooltip_label import tooltip_label
from utils import get_tooltip

def init_tab3(paths):
    tab3 = QWidget()
    tab3_layout = QHBoxLayout()
    tab3.setLayout(tab3_layout)

    # Left box
    tab3_leftbox = QWidget()
    tab3_leftbox_layout = QFormLayout()
    tab3_leftbox.setLayout(tab3_leftbox_layout)

    tab3_msconvert_arguments = additional_arguments('params.msconvert_additional_arguments', paths['nf'])  # msconvert
    tab3_msconvert_publish = publish_checkbox('params.publish_msconvert', paths['nf'])  # msconvert
    tab3_boxcar_convert_arguments = additional_arguments('params.boxcar_convert_additional_arguments', paths['nf']) # boxcar convert
    tab3_boxcar_convert_publish = publish_checkbox('params.publish_boxcar_convert', paths['nf'])  # boxcar convert
    tab3_quandenser_arguments = additional_arguments('params.quandenser_additional_arguments', paths['nf'])  # quandenser
    tab3_quandenser_publish = publish_checkbox('params.publish_quandenser', paths['nf'])  # quandenser
    tab3_parameter_missed_cleavages = parameter_setter_single("params.missed_cleavages", paths['nf'])  # Crux
    tab3_parameter_precursor_window = parameter_setter_double("params.precursor_window", paths['nf'])  # Crux
    tab3_parameter_mods_spec = additional_arguments('params.mods_spec', paths['nf'])  # Crux
    tab3_crux_arguments = additional_arguments('params.crux_index_additional_arguments', paths['nf'])  # Crux
    tab3_crux_index_arguments = additional_arguments('params.crux_index_additional_arguments', paths['nf'])  # Crux
    tab3_crux_search_arguments = additional_arguments('params.crux_search_additional_arguments', paths['nf'])  # Crux
    tab3_crux_percolator_arguments = additional_arguments('params.crux_percolator_additional_arguments', paths['nf'])  # Crux
    tab3_crux_publish = publish_checkbox('params.publish_crux', paths['nf'])  # Crux
    tab3_parameter_fold_change_eval = parameter_setter_double("params.fold_change_eval", paths['nf'])  # Triqler
    #tab3_raw_intensities_output = choose_option("params.raw_intensities", paths['nf'])
    #tab3_returnDistributions_output = choose_option("params.returnDistributions", paths['nf'])
    tab3_triqler_arguments = additional_arguments('params.triqler_additional_arguments', paths['nf'])  # Triqler
    tab3_triqler_publish = publish_checkbox('params.publish_triqler', paths['nf'])  # Crux
    tab3_reset_button = reset_button(paths['config'])

    tab3_leftbox_layout.addRow(QLabel('<b>MSconvert'), QLabel())
    tab3_leftbox_layout.addRow(QLabel('MSconvert additional arguments'), tab3_msconvert_arguments)
    tab3_leftbox_layout.addRow(QLabel('Publish MSconvert files'), tab3_msconvert_publish)
    tab3_leftbox_layout.addRow(QLabel('<b>Boxcar convert'), QLabel())
    tab3_leftbox_layout.addRow(QLabel('Boxcar convert additional arguments'), tab3_boxcar_convert_arguments)
    tab3_leftbox_layout.addRow(QLabel('Publish Boxcar convert files'), tab3_boxcar_convert_publish)
    tab3_leftbox_layout.addRow(QLabel('<b>Quandenser'), QLabel())
    tab3_leftbox_layout.addRow(QLabel('Quandenser additional arguments'), tab3_quandenser_arguments)
    tab3_leftbox_layout.addRow(QLabel('Publish Quandenser files'), tab3_quandenser_publish)
    tab3_leftbox_layout.addRow(QLabel('<b>Crux'), QLabel())
    tab3_leftbox_layout.addRow(QLabel('Missed cleavages'), tab3_parameter_missed_cleavages)
    tab3_leftbox_layout.addRow(QLabel('Precursor window'), tab3_parameter_precursor_window)
    tab3_leftbox_layout.addRow(QLabel('Mods spec'), tab3_parameter_mods_spec)
    tab3_leftbox_layout.addRow(QLabel('Crux indexing additional arguments'), tab3_crux_index_arguments)
    tab3_leftbox_layout.addRow(QLabel('Crux search additional arguments'), tab3_crux_search_arguments)
    tab3_leftbox_layout.addRow(QLabel('Crux percolator additional arguments'), tab3_crux_percolator_arguments)
    tab3_leftbox_layout.addRow(QLabel('Publish Crux files'), tab3_crux_publish)
    tab3_leftbox_layout.addRow(QLabel('<b>Triqler'), QLabel())
    tab3_leftbox_layout.addRow(QLabel('Fold change evaluation'), tab3_parameter_fold_change_eval)
    #tab3_leftbox_layout.addRow(QLabel('Output raw intensities'), tab3_raw_intensities_output)
    #tab3_leftbox_layout.addRow(QLabel('Output distributions'), tab3_returnDistributions_output)
    tab3_leftbox_layout.addRow(QLabel('Triqler additional arguments'), tab3_triqler_arguments)
    tab3_leftbox_layout.addRow(QLabel('Publish Triqler files'), tab3_triqler_publish)
    tab3_leftbox_layout.addRow(tab3_reset_button)

    # Right box
    tab3_rightbox = QWidget()
    tab3_rightbox_layout = QFormLayout()
    tab3_rightbox.setLayout(tab3_rightbox_layout)

    tab3_rightbox_layout.addRow(QLabel('<b>Quandenser-pipeline'), QLabel())
    tab3_output_dir_label = label_writer(paths['sh'])
    tooltip_label_dir_label = get_tooltip('dir-label')
    tooltip_email_username = get_tooltip('email-username')
    tooltip_email_password = get_tooltip('email-password')
    tab3_email_username = additional_arguments("params.email", paths['nf'])
    tab3_email_password = additional_arguments("smtp.password", paths['nf'])
    tab3_email_send_files = choose_option("params.sendfiles", paths['nf'])

    tab3_resume_button = resume_chooser(paths['pipe'])
    tab3_resume_folder_viewer = resume_folder_viewer(paths['nf'])

    tab3_rightbox_layout.addRow(tooltip_label_dir_label, tab3_output_dir_label)
    tab3_rightbox_layout.addRow(tab3_resume_button, tab3_resume_folder_viewer)
    tab3_rightbox_layout.addRow(QLabel('<b>Email notifications'), QLabel())
    tab3_rightbox_layout.addRow(tooltip_email_username, tab3_email_username)
    tab3_rightbox_layout.addRow(tooltip_email_password, tab3_email_password)
    tab3_rightbox_layout.addRow(QLabel("Send files"), tab3_email_send_files)

    tab3_layout.addWidget(tab3_leftbox)
    tab3_layout.addWidget(tab3_rightbox)

    return tab3
