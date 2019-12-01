import os
import sys
import math

def str2min(s):
    total_time = 0
    array = s.split(' ')
    for idx, value in enumerate(reversed(array)):
        last = value[-1]
        value = int(value[:-1])
        if last == 's':  # s
            total_time += value/60  # skip last
        elif last == 'm':  # m
            total_time += value
        elif last == 'h':  # h
            total_time += value*60
        elif last == 'd':  # d
            total_time += value*1440
    return total_time

def min2str(time):
    h = math.floor(time/60)
    m = math.floor(time%60)
    s = int((time%60*60)%60)
    return f"{h}:{m}:{s}"

if len(sys.argv) == 1:
    droppedFile = input('Path:')
else:
    droppedFile = sys.argv[1]
if "non-parallel" in droppedFile:
    print("non-parallel")
elif "parallel" in droppedFile:
    print("parallel")

total_time = 0  # min
msconvert_times = []
quandenser_parallel_1_times = []
with open(droppedFile, 'r') as f:
    for idx, line in enumerate(f):
        if idx == 0:
            continue
        line = line.split('\t')
        name = line[3].split(' ')[0]
        time = line[8]
        if name == 'msconvert':
            time = str2min(time)
            msconvert_times.append(time)
        elif 'quandenser_parallel_1' == name:
            time = str2min(time)
            quandenser_parallel_1_times.append(time)
        elif 'quandenser_parallel_3' == name:
            print("!!")
        else:
            total_time += str2min(time)
        print(name)
        print(line[8])
        print(str2min(line[8]))

total_time += max(msconvert_times)
if quandenser_parallel_1_times != []:
    total_time += max(quandenser_parallel_1_times)
print(total_time)
print(min2str(total_time))
print(droppedFile)
input('Enter when done')
