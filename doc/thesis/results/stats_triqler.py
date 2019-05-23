import numpy as np
import itertools
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import warnings
import scipy
import glob
import os
import re
from itertools import islice
import pdb
matplotlib.rc('font', family='Ubuntu Mono 13')
warnings.filterwarnings("ignore")
sns.set_color_codes("dark")
sns.set_style("white")
sns.set_context("talk")

def main(directory, fasta):
    proteins = unique_and_diff(directory)
    try:
        protein_search(proteins, fasta)
    except Exception as e:
        print(e)
    #generate_heatmap(directory, proteins)
    generate_plot(directory, proteins)

def unique_and_diff(directory):
    files = glob.glob(directory)
    proteins = []
    threshold = 0.05
    diff = 0
    for file in files:
        with open(file, 'r') as f:
            all_lines = f.readlines()
        for i, line in enumerate(all_lines):
            if i == 0:
                header = line.replace('\n','').split('\t')
                continue
            line = line.replace('\n','').split('\t')
            qval = float(line[0])
            if qval < threshold:
                protein = line[header.index('protein')]
                protein = protein.split('|')[-1]
                proteins.append(protein)
                diff += 1
    print("DIFF:", diff)
    print("UNIQUE:", len(list(set(proteins))))
    return list(set(proteins))

def protein_search(diff_proteins, fasta):
    with open(fasta, 'r') as f:
        all_proteins = f.read().split('>')
        all_proteins = [i.split('\n')[0] for i in all_proteins]
        accessions = [i.split(' ')[0] for i in all_proteins]
        all_info = [' '.join(i.split(' ')[1:]) for i in all_proteins]
    with open('proteins.txt', 'w') as f:
        for i, protein in enumerate(accessions):
            protein = protein.split('|')[-1]
            if protein == '':
                continue
            if protein in diff_proteins:
                info = all_info[i].split('OS=')[0]
                info = info.split('(')[0]
                text = f"{protein} & {info} \\\\"
                f.write(text + '\n')

def generate_plot(directory, proteins):
    files = glob.glob(directory)
    data = {}
    for file in files:
        with open(file, 'r') as f:
            all_lines = f.readlines()
        for i, line in enumerate(all_lines):
            line = line.replace('\n','').split('\t')
            protein = line[2]
            if i == 0:
                header = line
                start_index = [i for i, h in enumerate(header) if "diff_exp_prob" in h][0] + 1
                end_index = line.index('peptides')
                groups = []
                slices = []
                slice = 0
                prev_label = ""
                for i, run in enumerate(header[start_index:end_index]):
                    label = run.split(':')[1]
                    groups.append(label)
                    if prev_label == label or prev_label == "":
                        slice += 1
                    else:
                        slices.append(slice)
                        slice = 1
                    prev_label = label
                slices.append(slice)
                groups = sorted(list(set(groups)))
                continue
            if protein in proteins:
                abundances = line[start_index:end_index]
                abundances = [float(i) for i in abundances]
                it = iter(abundances)
                sliced = [list(islice(it, 0, i)) for i in slices]
                summed = [average(l) for l in sliced]
                if protein not in data.keys():
                    data[protein] = {}
                    data[protein] = summed
        create_plot(data, groups)
        return

def create_plot(data, groups):
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(10,10))
    fig.subplots_adjust(hspace=0.3)
    df = pd.DataFrame(data=data)
    for num_prot, protein in enumerate(data.keys()):
        ydata = data[protein]
        if ydata[0] > ydata[2]:
            plt.subplot(2,1,1)
        else:
            plt.subplot(2,1,2)
        plotted = sns.lineplot(x=groups,
                               y=data[protein],
                               label=protein)

    fig.savefig('combined.png')
    plt.show()

def average(l):
    avg = sum(l)/len(l)
    return avg

"""
def generate_heatmap(file, proteins):
    files = glob.glob(directory)
    data = {}
    for file in files:
        with open(file, 'r') as f:
            all_lines = f.readlines()
        for i, line in enumerate(all_lines):
            if i == 0:
                header = line.replace('\n','').split('\t')
                continue
            line = line.replace('\n','').split('\t')
            protein = line[header.index('protein')].split('|')[-1]
            if protein in proteins:
                fold_change = float(line[header.index('log2_fold_change')])
                comb = os.path.basename(file)
                comb = change_label(comb)
                if protein not in data.keys():
                    data[protein] = {}
                data[protein][comb] = fold_change
    generate_single_heatmap(proteins, data)
    generate_combined_heatmap(proteins, data)

def generate_single_heatmap(proteins, data):
    if not os.path.isdir('proteins'):
        os.mkdir('proteins')
    nrows = int(len(proteins)/2)
    groups = list(data.values())[0].keys()
    for num_prot, protein in enumerate(data.keys()):
        matrix, comb_matrix, xlabel, ylabel = generate_heatmap_layout(list(groups))
        for comb in data[protein].keys():
            for row,x in enumerate(xlabel):
                for column,y in enumerate(ylabel):
                    comb_check = x + 'vs' + y
                    if comb_check == comb:
                        matrix[row][column] = data[protein][comb]
        # Fill in reverse
        for i in range(len(xlabel)):
            for j in range(i, len(ylabel)):
                if matrix[i][j] == 0:
                    matrix[j][i] = None
                else:
                    matrix[j][i] = -matrix[i][j]
        df = pd.DataFrame(data=matrix,
                          columns=xlabel)
        sns.heatmap(df,
                    vmin = -3.0,
                    vmax = 3.0,
                    cmap = "RdBu_r",
                    annot = True,
                    xticklabels=df.columns,
                    yticklabels=df.columns,
                    cbar_kws={'label': 'Log2 Fold change'},
                    annot_kws={"size": 20})
        plt.title(protein, fontsize=26)
        print(f"{num_prot} out of {len(proteins)} done", end='\r')
        plt.savefig(f"proteins/{protein}.png", bbox_inches='tight',pad_inches=0)
        plt.close()

def generate_combined_heatmap(proteins, data):
    nrows = int(len(proteins)/2)
    if len(proteins)%2 != 0:
        nrows+=1
    fig, ax = plt.subplots(nrows=nrows, ncols=2, figsize=(20,30))
    fig.subplots_adjust(hspace=0.3)
    groups = list(data.values())[0].keys()
    for num_prot, protein in enumerate(data.keys()):
        matrix, comb_matrix, xlabel, ylabel = generate_heatmap_layout(list(groups))
        for comb in data[protein].keys():
            for row,x in enumerate(xlabel):
                for column,y in enumerate(ylabel):
                    comb_check = x + 'vs' + y
                    if comb_check == comb:
                        matrix[row][column] = data[protein][comb]

        # Fill in reverse
        for i in range(len(xlabel)):
            for j in range(i, len(ylabel)):
                if matrix[i][j] == 0:
                    matrix[j][i] = None
                else:
                    matrix[j][i] = -matrix[i][j]

        plt.subplot(nrows,2,num_prot+1)
        df = pd.DataFrame(data=matrix,
                          columns=xlabel)
        sns.heatmap(df,
                    vmin = -3.0,
                    vmax = 3.0,
                    cmap = "RdBu_r",
                    annot = True,
                    xticklabels=df.columns,
                    yticklabels=df.columns,
                    cbar_kws={'label': 'Log2 Fold change'},
                    annot_kws={"size": 20})
        plt.title(protein, fontsize=26)
        print(f"{num_prot} out of {len(proteins)} done", end='\r')
    plt.savefig('combined.png', bbox_inches='tight',pad_inches=0)
    plt.close()

def change_label(text):
    c1 = re.search('.([0-9])vs', text).group(1)
    c2 = re.search('vs([0-9]).', text).group(1)
    c1 = int(c1); c2 = int(c2)
    c1 = chr(c1 + 64); c2 = chr(c2 + 64)
    return f"{c1}vs{c2}"

def generate_heatmap_layout(keys):
    size = int(len(keys)/2)
    xlabel = ylabel = [chr(i) for i in range(65, 65 + size)]
    matrix = np.zeros([size, size])
    comb_matrix = np.empty([size, size], dtype=object)
    for row,x in enumerate(xlabel):
        for column,y in enumerate(ylabel):
            comb = x + 'vs' + y
            comb_matrix[row][column] = comb
    return matrix, comb_matrix, xlabel, ylabel
"""

if __name__ == "__main__":
    directory = "data/cyano_QP/*"
    if 'FA' in directory:
        fasta = "/media/storage/timothy/MSfiles/fasta/ralstonia/UP000008210_381666_UNIPROT_20190107_CRAP.fasta"
    if 'cyano' in directory:
        fasta = "/media/storage/timothy/MSfiles/fasta/synechocystis/Synechocystis_PCC6803_crap_NO_DECOY.fasta"
    main(directory, fasta)