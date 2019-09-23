import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import datetime
sns.set_color_codes("dark")
sns.set_style("white")
sns.set_context("talk")
data = {
'QP (parallel)': [10*60 + 46, 60 + 13, 56],
'QP (non-parallel)': [10*60 + 57, 60 + 35, 60 + 12],
'QP HPC (parallel)': [8*60 + 33, 60 + 17, 60 + 21],
'QP HPC (non-parallel)': [14*60 + 4, 2*60 + 29, 60 + 54],
'MaxQuant mbr': [28*60 + 44, 4*60 + 17, 60 + 45]
}
data_cores = {
'QP (parallel)': [29.8, 3.9, 2.4],
'QP (non-parallel)': [16.9, 3.0, 1.8],
'QP HPC (parallel)': [164.0, 23.9, 12.6],
'QP HPC (non-parallel)': [210.9, 29.0, 18.2],
'MaxQuant mbr': [103.7, 15.5, 6.2]
}

# Restructure
data_sets =  ['Geyer (180 files)', 'Bracht (27 files)', 'Latosinska (8 files)']
data_list = []
data_cores_list = []
for key_time, key_cores in zip(data.keys(), data_cores.keys()):
    time_values = data[key_time]
    cpu_values = data_cores[key_cores]
    for index, (time, cpu) in enumerate(zip(time_values, cpu_values)):
        data_list.append([key_time, data_sets[index], time])
        data_cores_list.append([key_cores, data_sets[index], cpu])

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
        ax.legend(handles=handles[0:], labels=labels[0:], fontsize='12')
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
