import os
import re

def main():
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk('.'):
        for file in f:
            if '.txt' in file:
                files.append(os.path.join(r, file))
    for file in files:
        print("File:", file)
        if 'parallel' in file:
            parallel = True
        else:
            parallel = False
        cpu_minutes = 0
        with open(file, 'r') as trace:
            all_lines = trace.readlines()
        for i, line in enumerate(all_lines):
            line = line.split('\t')
            if i == 0:
                header = line
                continue
            cpu = cpu_to_int(line[header.index('%cpu')], parallel=parallel)
            if cpu is None:
                continue
            minutes = time_to_min(line[header.index('realtime')])
            cpu_minutes += minutes*cpu
        print("Core minutes:", round(cpu_minutes))

def time_to_min(time_string):
    time = time_string.split(' ')
    time = [re.sub("\D", "", i) for i in time]
    minutes = 0
    for i, t in enumerate(reversed(time)):
        t = float(t)
        if i == 0:
            minutes += t/60
        elif i == 1:
            minutes += t
        elif i == 2:
            minutes += t*60
    return minutes

def cpu_to_int(cpu_string, parallel=False):
    if cpu_string == "-":
        return None
    cpu = cpu_string.replace('%', '')
    cpu = float(cpu)/100
    if parallel:
        cpu = cpu/2
    return cpu

if __name__ == "__main__":
    main()
