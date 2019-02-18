from colorama import Fore, Back, Style
from PySide2.QtWidgets import QFileDialog, QApplication
import os
import sys

#print(Style.BRIGHT, end='\r')

def message(message, color):
    print(color + f"{message}" + Fore.RESET)

def mean(l):
    if len(l) == 0:
        return 0
    mean_val = sum(l) / float(len(l))
    return mean_val

def run():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    qfd = QFileDialog(options=options)
    path='../../Quandenser_installer/RUNS/1vs2'
    files, _ = QFileDialog.getOpenFileNames(qfd,
                                            'Files',
                                            path,
                                            options=options)
    num_of_peptides = []
    num_of_proteins = []
    num_of_peptides_no_decoy = []
    num_of_proteins_no_decoy = []
    prots_qthreshold_1_no_decoy = []  # 0.05
    prots_qthreshold_2_no_decoy = []  # 0.01
    for file in files:
        with open(file, 'r') as f_ptr:
            lines = f_ptr.readlines()

        pep = 0
        pep_no_decoy = 0
        prot = 0
        prot_no_decoy = 0
        for i, line in enumerate(lines):
            if i == 0:
                continue
            pep += int(line.split('\t')[3])
            prot += 1
            if not "decoy" in line:
                pep_no_decoy += int(line.split('\t')[3])
                prot_no_decoy += 1

        num_of_peptides.append(pep)
        num_of_proteins.append(prot)
        num_of_peptides_no_decoy.append(pep_no_decoy)
        num_of_proteins_no_decoy.append(prot_no_decoy)

        q_index = 0
        fdr1 = True
        fdr2 = True
        for i, line in enumerate(lines):
            if i == 0:
                continue
            if "decoy" in line:
                continue
            if float(line.split('\t')[0]) > 0.05 and fdr1:
                prots_qthreshold_1_no_decoy.append(q_index)
                fdr1 = False
            if float(line.split('\t')[0]) > 0.01 and fdr2:
                prots_qthreshold_2_no_decoy.append(q_index)
                fdr2 = False
            else:
                q_index += 1

    mean_pep = mean(num_of_peptides)
    mean_prot = mean(num_of_proteins)
    mean_pep_no_decoy = mean(num_of_peptides_no_decoy)
    mean_prot_no_decoy = mean(num_of_proteins_no_decoy)
    mean_qval_1_prots_no_decoy = mean(prots_qthreshold_1_no_decoy)
    mean_qval_2_prots_no_decoy = mean(prots_qthreshold_2_no_decoy)

    print(round(mean_pep, 2), "mean peptides with decoys")
    print(round(mean_prot, 2), "mean proteins with decoys")
    print(round(mean_pep_no_decoy, 2), "mean peptides with NO decoys")
    print(round(mean_prot_no_decoy, 2), "mean proteins with NO decoys")
    print(round(mean_qval_1_prots_no_decoy, 2), "proteins up to qval threshold of 0.05, no decoys counted")
    print(round(mean_qval_2_prots_no_decoy, 2), "proteins up to qval threshold of 0.01, no decoys counted")


    sys.exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = run() # Stack smashing happens BEFORE we reach here
    sys.exit(app.exec_())
