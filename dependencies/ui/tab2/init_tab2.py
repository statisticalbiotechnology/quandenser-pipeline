from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel

from tab2.workflow import workflow
from tab2.choose_option import choose_option
from tab2.cluster_arguments import cluster_arguments
from tab2.set_time import set_time
from tab2.set_cpus import set_cpus

from custom_config_parser import custom_config_parser
from tooltip_label import tooltip_label

def init_tab2(paths):
    tab2 = QWidget()
    tab2_layout = QHBoxLayout()
    tab2.setLayout(tab2_layout)

    # Left box
    tab2_leftbox = QWidget()
    tab2_leftbox_layout = QVBoxLayout()
    tab2_leftbox.setLayout(tab2_leftbox_layout)

    # Top
    tab2_leftbox_top = QWidget()
    tab2_leftbox_top_layout = QFormLayout()
    tab2_leftbox_top.setLayout(tab2_leftbox_top_layout)

    tab2_choose_option_workflow = choose_option(paths['nf'], 'workflow')
    tab2_choose_option_parallell_msconvert = choose_option(paths['nf'], 'parallell_msconvert')
    tab2_choose_option_profile = choose_option(paths['sh'], 'profile')

    # Always visible
    tab2_leftbox_top_layout.addRow(QLabel('Choose pipeline'), tab2_choose_option_workflow)
    tab2_leftbox_top_layout.addRow(QLabel('Enable parallell MSconvert'), tab2_choose_option_parallell_msconvert)
    tab2_leftbox_top_layout.addRow(QLabel('Profile'), tab2_choose_option_profile)
    tab2_leftbox_layout.addWidget(tab2_leftbox_top)

    # Bottom, these will be hidden or shown depending on profile option
    tab2_hidden = QWidget()
    tab2_hidden.hidden_object = True
    tab2_hidden_layout = QFormLayout()
    tab2_hidden.setLayout(tab2_hidden_layout)

    tab2_cluster_arguments = cluster_arguments("process.clusterOptions", paths['nf'])
    tab2_cluster_queue = cluster_arguments("process.queue", paths['nf'])
    tab2_parameter_msconvert_cpus = set_cpus("msconvert_cpus", paths['nf'])
    tab2_parameter_msconvert_time = set_time("msconvert_time", paths['nf'])
    tab2_parameter_quandenser_cpus = set_cpus("quandenser_cpus", paths['nf'])
    tab2_parameter_quandenser_time = set_time("quandenser_time", paths['nf'])
    tab2_parameter_tide_search_cpus = set_cpus("tide_search_cpus", paths['nf'])
    tab2_parameter_tide_search_time = set_time("tide_search_time", paths['nf'])
    tab2_parameter_triqler_cpus = set_cpus("triqler_cpus", paths['nf'])
    tab2_parameter_triqler_time = set_time("triqler_time", paths['nf'])

    # Hidden depending on setting
    tab2_hidden_layout.addRow(QLabel('Cluster arguments'), tab2_cluster_arguments)
    tab2_hidden_layout.addRow(QLabel('Cluster queue'), tab2_cluster_queue)
    tab2_hidden_layout.addRow(QLabel('MSconvert cpus'), tab2_parameter_msconvert_cpus)
    tab2_hidden_layout.addRow(QLabel('MSconvert time'), tab2_parameter_msconvert_time)
    tab2_hidden_layout.addRow(QLabel('Quandenser cpus'), tab2_parameter_quandenser_cpus)
    tab2_hidden_layout.addRow(QLabel('Quandenser time'), tab2_parameter_quandenser_time)
    tab2_hidden_layout.addRow(QLabel('Tide search cpus'), tab2_parameter_tide_search_cpus)
    tab2_hidden_layout.addRow(QLabel('Tide search time'), tab2_parameter_tide_search_time)
    tab2_hidden_layout.addRow(QLabel('Triqler cpus'), tab2_parameter_triqler_cpus)
    tab2_hidden_layout.addRow(QLabel('Triqler time'), tab2_parameter_triqler_time)
    tab2_leftbox_layout.addWidget(tab2_hidden)

    # Right box
    tab2_rightbox = QWidget()
    tab2_rightbox_layout = QHBoxLayout()
    tab2_rightbox.setLayout(tab2_rightbox_layout)

    pipe_parser = custom_config_parser()
    pipe_parser.load(paths['pipe'])
    if pipe_parser.get('disable-opengl') in ['false', '']:
        tab2_workflow = workflow()
        tab2_rightbox_layout.addWidget(tab2_workflow)
    else:
        tab2_workflow = tooltip_label("OpenGL disabled", "OpenGL disabled", style=True)

    tab2_rightbox_layout.addWidget(tab2_workflow)
    tab2_layout.addWidget(tab2_rightbox)

    # Combine
    tab2_layout.addWidget(tab2_leftbox)
    tab2_layout.addWidget(tab2_rightbox)
    return tab2
