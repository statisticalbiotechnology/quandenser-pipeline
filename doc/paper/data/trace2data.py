import os
import sys
import math

def str2min(s):
    total_time = 0
    array = s.split(' ')
    for idx, value in enumerate(reversed(array)):
        if value[-2:] == 'ms':
            continue
        if value == '-':  # Empty time
            continue
        last = value[-1]
        value = int(float(value[:-1]))  # Sometimes 23.1 s
        if last == 's':  # s
            total_time += value/60  # skip last
        elif last == 'm':  # m
            total_time += value
        elif last == 'h':  # h
            total_time += value*60
        elif last == 'd':  # d
            total_time += value*1440
    return total_time

def submit2min(s):
    total_time = 0
    array = s.split(':')
    for idx, value in enumerate(reversed(array)):
        value = float(value)
        if idx == 0:  # s
            total_time += value/60  # skip last
        elif idx == 1:  # m
            total_time += value
        elif idx == 2:  # m
            total_time += value*60
        elif idx == 3:  # m
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
quandenser_parallel_3_groups = []
quandenser_parallel_3_times = []
with open(droppedFile, 'r') as f:
    for idx, line in enumerate(f):
        if idx == 0:
            continue
        line = line.split('\t')
        name = line[3].split(' ')[0]
        time = line[8]
        time = str2min(time)
        if name == 'msconvert':
            msconvert_times.append(time)
        elif 'quandenser_parallel_1' == name:
            quandenser_parallel_1_times.append(time)
        elif 'quandenser_parallel_3' == name:
            submit_time = line[6]
            submit_time = submit_time.split(' ')[-1]
            submit_time = submit2min(submit_time)
            print(submit_time)
            print(quandenser_parallel_3_groups)
            if quandenser_parallel_3_groups == []:
                quandenser_parallel_3_groups.append(submit_time)
                quandenser_parallel_3_times.append(time)
            elif abs(quandenser_parallel_3_groups[0] - submit_time) > 0.5:  # Submit within 0.5 min
                total_time += max(quandenser_parallel_3_times)
                quandenser_parallel_3_groups = [submit_time]
                quandenser_parallel_3_times = [time]
            else:
                quandenser_parallel_3_groups.append(submit_time)
                quandenser_parallel_3_times.append(time)
        else:
            total_time += time

total_time += max(msconvert_times)
if quandenser_parallel_1_times != []:
    total_time += max(quandenser_parallel_1_times)
if quandenser_parallel_3_times != []:
    total_time += max(quandenser_parallel_3_times)
print(total_time)
print(min2str(total_time))
print(droppedFile)
input('Enter when done')
