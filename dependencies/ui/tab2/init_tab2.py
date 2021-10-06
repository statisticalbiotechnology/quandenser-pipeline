from PySide2 import QtCore
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QGridLayout, QSizePolicy
from PySide2.QtWidgets import QStackedLayout

from tab2.workflow import workflow
from tab2.choose_option import choose_option
from tab2.cluster_arguments import cluster_arguments
from tab2.set_time import set_time
from tab2.set_cpus import set_cpus
from tab2.parameter_setter import parameter_setter_single

from custom_config_parser import custom_config_parser
from tooltip_label import tooltip_label
from utils import get_tooltip

def init_tab2(paths):
    tab2 = QWidget()
    tab2_layout = QHBoxLayout()
    tab2.setLayout(tab2_layout)
    filler = QLabel('')
    filler.setFixedWidth(1)

    # Left box
    tab2_leftbox = QWidget()
    tab2_leftbox_layout = QVBoxLayout()
    tab2_leftbox.setLayout(tab2_leftbox_layout)

    # Top
    tab2_leftbox_top = QWidget()
    tab2_leftbox_top_layout = QFormLayout()
    tab2_leftbox_top.setLayout(tab2_leftbox_top_layout)

    tab2_choose_option_workflow = choose_option('workflow', paths['nf'])
    tab2_choose_option_boxcar_convert = choose_option('boxcar_convert', paths['nf'])
    tab2_choose_option_profile = choose_option('profile', paths['sh'])
    tab2_choose_option_parallel_quandenser = choose_option('parallel_quandenser', paths['nf'])
    tab2_max_forks_quandenser = parameter_setter_single('parallel_quandenser_max_forks', paths['nf'])
    tab2_max_forks_msconvert = parameter_setter_single('parallel_msconvert_max_forks', paths['nf'])
    tab2_max_forks_boxcar = parameter_setter_single('parallel_boxcar_max_forks', paths['nf'])

    # Always visible
    tab2_leftbox_top_layout.addRow(QLabel('Choose workflow'), tab2_choose_option_workflow)
    tab2_leftbox_top_layout.addRow(QLabel('Profile'), tab2_choose_option_profile)
    tab2_leftbox_top_layout.addRow(QLabel('Enable boxcar conversion'), tab2_choose_option_boxcar_convert)
    tab2_leftbox_top_layout.addRow(QLabel('Enable parallel quandenser'), tab2_choose_option_parallel_quandenser)
    tab2_leftbox_top_layout.addRow(QLabel('Max forks msconvert convert'), tab2_max_forks_msconvert)
    tab2_leftbox_top_layout.addRow(QLabel('Max forks boxcar'), tab2_max_forks_boxcar)
    tab2_leftbox_top_layout.addRow(QLabel('Max forks quandenser'), tab2_max_forks_quandenser)
    tab2_leftbox_top_layout.addRow(filler, filler)  # Empty space
    tab2_leftbox_layout.addWidget(tab2_leftbox_top)

    # Bottom, these will be hidden or shown depending on profile option
    tab2_hidden = QWidget()
    tab2_hidden.hidden_object = True
    tab2_hidden_layout = QStackedLayout()
    tab2_hidden.setLayout(tab2_hidden_layout)

    # Stack 1: Empty layout. Cluster disabled
    tab2_hidden_stack_1 = QWidget()
    tab2_hidden_stack_1_layout = QFormLayout()
    tab2_hidden_stack_1.setLayout(tab2_hidden_stack_1_layout)

    # Stack 2: Regular quandenser, cluster enabled
    tab2_hidden_stack_2 = QWidget()
    tab2_hidden_stack_2_layout = QFormLayout()
    tab2_hidden_stack_2_layout.setVerticalSpacing(0)
    tab2_hidden_stack_2.setLayout(tab2_hidden_stack_2_layout)

    stack_2_widgets = []
    stack_2_widgets.append(get_tooltip('cluster-type'))
    stack_2_widgets.append(choose_option("process.executor", paths['nf']))
    stack_2_widgets.append(filler)
    stack_2_widgets.append(get_tooltip('cluster-arguments'))
    stack_2_widgets.append(cluster_arguments("process.clusterOptions", paths['nf']))
    stack_2_widgets.append(filler)
    stack_2_widgets.append(get_tooltip('cluster-queue'))
    stack_2_widgets.append(cluster_arguments("process.queue", paths['nf']))
    stack_2_widgets.append(filler)
    stack_2_widgets.append(QLabel('MSconvert cpus + time'))
    stack_2_widgets.append(set_cpus("msconvert_cpus", paths['nf']))
    stack_2_widgets.append(set_time("msconvert_time", paths['nf']))
    stack_2_widgets.append(QLabel('Boxcar convert cpus + time'))
    stack_2_widgets.append(set_cpus("boxcar_convert_cpus", paths['nf']))
    stack_2_widgets.append(set_time("boxcar_convert_time", paths['nf']))
    stack_2_widgets.append(QLabel('Quandenser cpus + time'))
    stack_2_widgets.append(set_cpus("quandenser_cpus", paths['nf']))
    stack_2_widgets.append(set_time("quandenser_time", paths['nf']))
    stack_2_widgets.append(QLabel('Tide cpus + time'))
    stack_2_widgets.append(set_cpus("tide_search_cpus", paths['nf']))
    stack_2_widgets.append(set_time("tide_search_time", paths['nf']))
    stack_2_widgets.append(QLabel('Triqler cpus + time'))
    stack_2_widgets.append(set_cpus("triqler_cpus", paths['nf']))
    stack_2_widgets.append(set_time("triqler_time", paths['nf']))

    list_itr = iter(stack_2_widgets)
    for label in list_itr:
        combine_widget = QWidget()
        combine_widget_layout = QFormLayout()
        combine_widget.setLayout(combine_widget_layout)
        widget1, widget2 = next(list_itr), next(list_itr)
        combine_widget_layout.addRow(widget1, widget2)
        tab2_hidden_stack_2_layout.addRow(label, combine_widget)

    # Stack 3: Parallel quandenser, cluster enabled
    tab2_hidden_stack_3 = QWidget()
    tab2_hidden_stack_3_layout = QFormLayout()
    tab2_hidden_stack_3_layout.setVerticalSpacing(0)
    tab2_hidden_stack_3.setLayout(tab2_hidden_stack_3_layout)

    stack_3_widgets = []
    stack_3_widgets.append(get_tooltip('cluster-type'))
    stack_3_widgets.append(choose_option("process.executor", paths['nf']))
    stack_3_widgets.append(filler)
    stack_3_widgets.append(get_tooltip('cluster-arguments'))
    stack_3_widgets.append(cluster_arguments("process.clusterOptions", paths['nf']))
    stack_3_widgets.append(filler)
    stack_3_widgets.append(get_tooltip('cluster-queue'))
    stack_3_widgets.append(cluster_arguments("process.queue", paths['nf']))
    stack_3_widgets.append(filler)
    stack_3_widgets.append(QLabel('MSconvert cpus + time'))
    stack_3_widgets.append(set_cpus("msconvert_cpus", paths['nf']))
    stack_3_widgets.append(set_time("msconvert_time", paths['nf']))
    stack_3_widgets.append(QLabel('Boxcar convert cpus + time'))
    stack_3_widgets.append(set_cpus("boxcar_convert_cpus", paths['nf']))
    stack_3_widgets.append(set_time("boxcar_convert_time", paths['nf']))
    stack_3_widgets.append(QLabel('Quandenser p1 cpus + time'))
    stack_3_widgets.append(set_cpus("quandenser_parallel_1_dinosaur_cpus", paths['nf']))
    stack_3_widgets.append(set_time("quandenser_parallel_1_dinosaur_time", paths['nf']))
    stack_3_widgets.append(QLabel('Quandenser p2 cpus + time'))
    stack_3_widgets.append(set_cpus("quandenser_parallel_2_maracluster_cpus", paths['nf']))
    stack_3_widgets.append(set_time("quandenser_parallel_2_maracluster_time", paths['nf']))
    stack_3_widgets.append(QLabel('Quandenser p3 cpus + time'))
    stack_3_widgets.append(set_cpus("quandenser_parallel_3_match_features_cpus", paths['nf']))
    stack_3_widgets.append(set_time("quandenser_parallel_3_match_features_time", paths['nf']))
    stack_3_widgets.append(QLabel('Quandenser p4 cpus + time'))
    stack_3_widgets.append(set_cpus("quandenser_parallel_4_consensus_cpus", paths['nf']))
    stack_3_widgets.append(set_time("quandenser_parallel_4_consensus_time", paths['nf']))
    stack_3_widgets.append(QLabel('Tide cpus + time'))
    stack_3_widgets.append(set_cpus("tide_search_cpus", paths['nf']))
    stack_3_widgets.append(set_time("tide_search_time", paths['nf']))
    stack_3_widgets.append(QLabel('Triqler cpus + time'))
    stack_3_widgets.append(set_cpus("triqler_cpus", paths['nf']))
    stack_3_widgets.append(set_time("triqler_time", paths['nf']))
    stack_3_widgets.extend([filler, filler, filler])  # Empty space

    list_itr = iter(stack_3_widgets)
    for label in list_itr:
        combine_widget = QWidget()
        combine_widget_layout = QFormLayout()
        combine_widget.setLayout(combine_widget_layout)
        widget1, widget2 = next(list_itr), next(list_itr)
        combine_widget_layout.addRow(widget1, widget2)
        tab2_hidden_stack_3_layout.addRow(label, combine_widget)
    
    # Stack 4: Parallel quandenser, parallel maracluster, cluster enabled
    tab2_hidden_stack_4 = QWidget()
    tab2_hidden_stack_4_layout = QFormLayout()
    tab2_hidden_stack_4_layout.setVerticalSpacing(0)
    tab2_hidden_stack_4.setLayout(tab2_hidden_stack_4_layout)

    stack_4_widgets = []
    stack_4_widgets.append(get_tooltip('cluster-type'))
    stack_4_widgets.append(choose_option("process.executor", paths['nf']))
    stack_4_widgets.append(filler)
    stack_4_widgets.append(get_tooltip('cluster-arguments'))
    stack_4_widgets.append(cluster_arguments("process.clusterOptions", paths['nf']))
    stack_4_widgets.append(filler)
    stack_4_widgets.append(get_tooltip('cluster-queue'))
    stack_4_widgets.append(cluster_arguments("process.queue", paths['nf']))
    stack_4_widgets.append(filler)
    stack_4_widgets.append(QLabel('MSconvert cpus + time'))
    stack_4_widgets.append(set_cpus("msconvert_cpus", paths['nf']))
    stack_4_widgets.append(set_time("msconvert_time", paths['nf']))
    stack_4_widgets.append(QLabel('Boxcar convert cpus + time'))
    stack_4_widgets.append(set_cpus("boxcar_convert_cpus", paths['nf']))
    stack_4_widgets.append(set_time("boxcar_convert_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p1 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_1_dinosaur_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_1_dinosaur_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p2.1 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_2_maracluster_parallel_1_index_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_2_maracluster_parallel_1_index_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p2.2 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_2_maracluster_parallel_2_pvalue_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_2_maracluster_parallel_2_pvalue_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p2.3 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_2_maracluster_parallel_3_overlap_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_2_maracluster_parallel_3_overlap_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p2.4 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_2_maracluster_parallel_4_cluster_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_2_maracluster_parallel_4_cluster_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p3 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_3_match_features_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_3_match_features_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p4.1 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_4_consensus_parallel_1_index_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_4_consensus_parallel_1_index_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p4.2 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_4_consensus_parallel_2_pvalue_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_4_consensus_parallel_2_pvalue_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p4.3 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_4_consensus_parallel_3_overlap_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_4_consensus_parallel_3_overlap_time", paths['nf']))
    stack_4_widgets.append(QLabel('Quandenser p4.4 cpus + time'))
    stack_4_widgets.append(set_cpus("quandenser_parallel_4_consensus_parallel_4_cluster_cpus", paths['nf']))
    stack_4_widgets.append(set_time("quandenser_parallel_4_consensus_parallel_4_cluster_time", paths['nf']))
    stack_4_widgets.append(QLabel('Tide cpus + time'))
    stack_4_widgets.append(set_cpus("tide_search_cpus", paths['nf']))
    stack_4_widgets.append(set_time("tide_search_time", paths['nf']))
    stack_4_widgets.append(QLabel('Triqler cpus + time'))
    stack_4_widgets.append(set_cpus("triqler_cpus", paths['nf']))
    stack_4_widgets.append(set_time("triqler_time", paths['nf']))
    stack_4_widgets.extend([filler, filler, filler])  # Empty space

    list_itr = iter(stack_4_widgets)
    for label in list_itr:
        combine_widget = QWidget()
        combine_widget_layout = QFormLayout()
        combine_widget.setLayout(combine_widget_layout)
        widget1, widget2 = next(list_itr), next(list_itr)
        combine_widget_layout.addRow(widget1, widget2)
        tab2_hidden_stack_4_layout.addRow(label, combine_widget)
    
    # Add stacks
    tab2_hidden_layout.addWidget(tab2_hidden_stack_1)
    tab2_hidden_layout.addWidget(tab2_hidden_stack_2)
    tab2_hidden_layout.addWidget(tab2_hidden_stack_3)
    tab2_hidden_layout.addWidget(tab2_hidden_stack_4)

    # Add hidden stacked layout
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
