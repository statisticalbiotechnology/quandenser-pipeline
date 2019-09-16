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
'QP\n(parallel)': [10*60 + 46, 60 + 13, 56],
'QP\n(non-parallel)': [0, 60 + 35, 60 + 12],
'QP HPC\n(parallel)': [0, 60 + 17, 60 + 21],
'QP HPC\n(non-parallel)': [0, 2*60 + 29, 60 + 54],
'MaxQuant\nmbr': [28*60 + 44, 4*60 + 17, 60 + 45]
}
data_cores = {
'QP\n(parallel)': [1,2,3],
'QP\n(non-parallel)': [1,2,3],
'QP HPC\n(parallel)': [1,2,3],
'QP HPC\n(non-parallel)': [1,2,3],
'MaxQuant\nmbr': [1,2,3]
}

# Restructure
data_sets =  ['Weightloss (180 files)', 'Bariatric surgery (27 files)', 'Bladder cancer (8 files)']
data_list = []
for key in data.keys():
    values = data[key]
    for index,value in enumerate(values):
        data_list.append([key, data_sets[index], value])

y = 'Minutes'
file = 'times.png'
columns = ['run', 'data_set', 'time']
pd_data = pd.DataFrame(data_list, columns = columns)
print(pd_data)
plt.figure(figsize=(15,7))
ax=sns.barplot(x='run',
               y='time',
               hue='data_set',
               data=pd_data)
plt.ylabel(y)
#plt.tight_layout()
plt.savefig(file)
plt.close()
