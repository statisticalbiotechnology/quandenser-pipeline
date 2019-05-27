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
sns.set_style("whitegrid")
sns.set_context("talk")

def main(directory, fasta):
    proteins, data = unique_and_diff(directory)
    generate_plot(directory, proteins)
    protein_search(proteins, fasta, data)

def unique_and_diff(directory):
    files = glob.glob(directory)
    data = {}
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
            pep = float(line[4])
            if qval < threshold:
                protein = line[header.index('protein')]
                protein = protein.split('|')[-1]
                proteins.append(protein)
                diff += 1
                if protein not in data.keys():
                    data[protein] = {}
                    data[protein] = {'qval': qval, 'pep': pep}
                else:
                    if data[protein]['qval'] > qval:
                        data[protein]['qval'] = qval
    print("DIFF:", diff)
    print("UNIQUE:", len(list(set(proteins))))
    return list(set(proteins)), data

def protein_search(diff_proteins, fasta, data):
    with open(fasta, 'r') as f:
        all_proteins = f.read().split('>')
        all_proteins = [i.split('\n')[0] for i in all_proteins]
        accessions = [i.split(' ')[0] for i in all_proteins]
        all_info = [' '.join(i.split(' ')[1:]) for i in all_proteins]
    with open('proteins.txt', 'w') as f:
        text = f"Protein & Function & PEP & q-value \\\\  \\midrule\n"
        f.write(text)
    with open('proteins.txt', 'a') as f:
        for i, protein in enumerate(accessions):
            protein = protein.split('|')[-1]
            if protein == '':
                continue
            if protein in diff_proteins:
                info = all_info[i].split('OS=')[0]
                info = info.split('(')[0]
                text = f"{protein} & {info} & {data[protein]['pep']} & {data[protein]['qval']} \\\\ [0.5ex]\n"
                f.write(text)

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
                #summed = [average(l) for l in sliced]
                if protein not in data.keys():
                    data[protein] = {}
                    data[protein] = sliced
        create_plot(data, groups)
        return data

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

        xinput = []
        yinput = []
        for i, y in enumerate(ydata):
            xinput.extend(groups[i]*len(y))
            yinput.extend(y)
        plotted = sns.lineplot(x=xinput,
                               y=yinput,
                               label=protein,
                               err_style='band')
        plt.ylabel('Relative protein expression of the same protein', fontsize=12)
        plt.legend(fontsize='x-small', title_fontsize='10', loc='upper right')
    fig.savefig('combined.png')
    plt.show()

def average(l):
    avg = sum(l)/len(l)
    return avg

if __name__ == "__main__":
    directory = "data/FA_QP/*"
    if 'FA' in directory:
        fasta = "/media/storage/timothy/MSfiles/fasta/ralstonia/UP000008210_381666_UNIPROT_20190107_CRAP.fasta"
    if 'cyano' in directory:
        fasta = "/media/storage/timothy/MSfiles/fasta/synechocystis/Synechocystis_PCC6803_crap_NO_DECOY.fasta"
    main(directory, fasta)
