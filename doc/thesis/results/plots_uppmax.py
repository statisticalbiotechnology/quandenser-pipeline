import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(color_codes=True)

# Cyano
times_cyano = [3*60 + 35, 255]
# Ralstonia
times_ralstonia = [3*60 + 23, 40]  # MOCKUP

# Titles
titles =  ['Cyanobacteria', 'Ralstonia']

data = {'Time': {'Data': [times_cyano, times_ralstonia],
                 'ylabel': 'Minutes',
                 'file': 'times-uppmax.png'}}
# Labels
programs = ['Quandenser pipeline\n(parallel)', 'Waiting time']
colors = [(45,55,65,0), (160,160,160,0)]
colors = [(r/255, g/255, b/255, a) for (r,g,b,a) in colors]

for key in data.keys():
    fig, axes = plt.subplots(nrows=1, ncols=2,figsize=(15,7))
    plt.subplots_adjust(wspace=0.2)
    for index, d in enumerate(data[key]['Data']):
        d = pd.DataFrame({' ': programs, key: d})
        plt.subplot(1,2,index+1)
        plt.title(titles[index]  + ' ' + key)
        barplot_fig = sns.barplot(x=' ', y=key, data=d, order=programs, palette=colors)
        plt.ylabel(data[key]['ylabel'])
        for item in barplot_fig.get_xticklabels():
            item.set_rotation(20)
    plt.savefig(data[key]['file'])
    plt.close()