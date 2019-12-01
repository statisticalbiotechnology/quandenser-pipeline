import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import datetime
import pdb
sns.set_color_codes("dark")
sns.set_style("white")
sns.set_context("talk")

def s2m(time_str):
    """Get minutes from time."""
    h, m, s = time_str.split(':')
    return int(h) * 60 + int(m) + int(s)/60

data_list = []
data_cores_list = []

data_sets =  ['Geyer (118 files)',
              'Bracht (27 files)',
              'Latosinska (8 files)']
run_types =  ['QP (parallel)',
              'QP (non-parallel)',
              'QP HPC (parallel)',
              'QP HPC (non-parallel)',
              'MaxQuant mbr']

for data_set in data_sets:
    for run_type in run_types:
        time_values = data_times[data_set][run_type]
        core_values = data_cores[data_set][run_type]
        for time_value, core_value in zip(time_values, core_values):
            data_list.append([run_type, data_set, time_value])
            data_cores_list.append([run_type, data_set, core_value])
print(data_list)

for d, y, f in zip([data_list, data_cores_list], ['Minutes', 'Core hours'], ['times.png', 'cores.png']):
    y = y
    file = f
    columns = ['run', 'data_set', 'time']
    pd_data = pd.DataFrame(d, columns = columns)
    print(pd_data)
    plt.figure(figsize=(20,7))
    for idx, d in enumerate(data_sets):
        plt.subplot(1,len(data_sets), idx+1)
        ax = sns.barplot(x='data_set',
                         y='time',
                         hue='run',
                         data=pd_data[pd_data.data_set == d])

        # Remove uneccessary titles
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles[0:],
                  labels=labels[0:],
                  fontsize='12')
        ax.set_xlabel('')
        plt.ylabel(y)

        # Set values on each bar
        if y == 'Minutes':
            display = '%d'
        else:
            display = '%.1f'
        for p in ax.patches:
            ax.text(p.get_x() + p.get_width()/2., p.get_height(), display % round(p.get_height(),2),
                    fontsize=12, color='black', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(file)
    plt.close()
