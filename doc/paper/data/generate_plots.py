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

def string2time(time_str):
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

with open('data.csv', 'r') as f:
    for idx, line in enumerate(f):
        if idx == 0 or idx == 17 or idx == 16:
            continue
        line = line.split(';')
        data_set = line[0]
        run = line[1]
        replicates = int(line[2])
        values = line[3:3+replicates]
        for value in values:
            if idx < 17:
                value = string2time(value)
                data_list.append([run, data_set, int(value)])
            else:
                value = value.replace(',', '.')
                value = float(value)
                data_cores_list.append([run, data_set, value])
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
                    fontsize=12, color='black', ha='right', va='bottom')

    plt.tight_layout()
    plt.savefig(file)
    plt.close()
