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
               1*60 + 19,  # CALC OR FIND
               1*60 + 16,
               2*60 + 41]
times_ralstonia_core = [90
                        78,
                        1,
                        712.5]
# Ralstonia
times_ralstonia = [3*60 + 23,
                   3*60 + 21,  # CALC OR FIND
                   3*60 + 52,
                   8*60 + 11]
times_ralstonia_core = [246,
                        204,
                        1,
                        1]

# Titles
titles =  ['Cyanobacteria', 'Ralstonia']

data = {'Time': {'Data': [times_cyano, times_ralstonia],
                 'ylabel': 'Minutes',
                 'file': 'times.png',
                 'titles': ['cyano', 'ralstonia']},
        'Time core hours':  {'Data': [times_cyano_core, times_ralstonia_core],
                              'ylabel': 'Minutes',
                              'file': 'times_core.png',
                              'titles': ['cyano', 'ralstonia']}}

# Labels
programs = ['Quandenser pipeline\n(parallel)', 'Quandenser pipeline\n(non-parallel)', 'OpenMS', 'MaxQuant']
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
        barplot_fig = sns.barplot(x=' ', y=key, data=d, order=programs, palette=colors)
        plt.ylabel(data[key]['ylabel'])
        for item in barplot_fig.get_xticklabels():
            item.set_rotation(20)
        for p in barplot_fig.patches:
            barplot_fig.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
    plt.savefig(data[key]['file'])
    plt.close()
