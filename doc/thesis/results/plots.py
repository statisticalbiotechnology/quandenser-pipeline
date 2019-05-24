import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import datetime
sns.set_color_codes("dark")
sns.set_style("white")
sns.set_context("talk")

# Cyano
times_cyano = [1*60 + 12,
               1*60 + 19,
               1*60 + 16,
               2*60 + 41]
times_cyano_core = [369,  # Rerun this
                    258,  # Should be correct
                    195,  # 1:13, 278% cpu
                    712.5]
# Ralstonia
times_ralstonia = [3*60 + 23,
                   3*60 + 21,
                   3*60 + 52,
                   8*60 + 11]
times_ralstonia_core = [833,  # Rerun this with time
                        599,  # Should be correct
                        602,
                        2371]  # 8:15, 483% cpu

# Titles
titles =  ['Cyanobacteria', 'Ralstonia']

data = {'Time': {'Data': [times_cyano, times_ralstonia],
                 'ylabel': 'Minutes',
                 'file': 'times.png',
                 'titles': ['cyano', 'ralstonia']},
        'Time core hours':  {'Data': [times_cyano_core, times_ralstonia_core],
                              'ylabel': 'Core minutes',
                              'file': 'times_core.png',
                              'titles': ['cyano', 'ralstonia']}}

# Labels
programs = ['QP \n(parallel)', 'QP \n(non-parallel)', 'OpenMS', 'MaxQuant']
colors = [(45,55,65,0), (45,55,65,0), (255,160,0,0), (0,40,160,0)]
colors = [(r/255, g/255, b/255, a) for (r,g,b,a) in colors]

for key in data.keys():
    fig, axes = plt.subplots(nrows=1, ncols=2,figsize=(15,7))
    if 'Time' in key:
        plt.subplots_adjust(wspace=0.2)
    for index, d in enumerate(data[key]['Data']):
        d = pd.DataFrame({' ': programs, key: d})
        plt.subplot(1,2,index+1)
        #plt.title(titles[index]  + ' ' + key)
        barplot_fig = sns.barplot(x=' ', y=key, data=d, order=programs, palette=colors, )
        plt.ylabel(data[key]['ylabel'])
        for item in barplot_fig.get_xticklabels():
            item.set_rotation(0)
        for p in barplot_fig.patches:
            barplot_fig.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
    #plt.tight_layout()
    plt.savefig(data[key]['file'], bbox_inches = "tight")
    plt.close()
