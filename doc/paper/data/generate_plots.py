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
'QP HPC (parallel)': [0, 60 + 17, 60 + 21],
'QP HPC (non-parallel)': [14*60 + 4, 2*60 + 29, 60 + 54],
'MaxQuant mbr': [28*60 + 44, 4*60 + 17, 60 + 45]
}
data_cores = {
'QP (parallel)': [29.8, 3.9, 2.4],
'QP (non-parallel)': [16.9, 3.0, 1.8],
'QP HPC (parallel)': [1, 23.9, 12.6],
'QP HPC (non-parallel)': [210.9, 29.0, 18.2],
'MaxQuant mbr': [103.7, 15.5, 6.2]
}

# Restructure
data_sets =  ['Geyer (180 files)', 'Bracht (27 files)', 'Latosinska (8 files)']
data_list = []
data_cores_list = []
for key_time, key_cores in zip(data.keys(), data_cores):
    time_values = data[key_time]
    cpu_values = data[key_cores]
    for index, (time, cpu) in enumerate(zip(time_values, cpu_values)):
        data_list.append([key_time, data_sets[index], time])
        data_cores_list.append([key_cores, data_sets[index], cpu])

y = 'Minutes'
file = 'times.png'
columns = ['run', 'data_set', 'time']
pd_data = pd.DataFrame(data_list, columns = columns)
print(pd_data)
plt.figure(figsize=(15,7))
ax = sns.barplot(x='data_set',
                 y='time',
                 hue='run',
                 data=pd_data)

# Remove uneccessary titles
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[0:], labels=labels[0:])
ax.set_xlabel('')

# Set values on each bar
for p in ax.patches:
    ax.text(p.get_x() + p.get_width()/2., p.get_height(), '%d' % int(p.get_height()),
            fontsize=12, color='black', ha='center', va='bottom')

plt.ylabel(y)
plt.tight_layout()
plt.savefig(file)
plt.close()
