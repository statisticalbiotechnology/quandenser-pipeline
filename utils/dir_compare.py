size_threshold = 0.5
root_dir = '../WIP'

from tkinter import filedialog
from tkinter import *
import os
import platform
import subprocess
script_dir = os.path.dirname(os.path.realpath(__file__))

root = Tk()
root.withdraw()
dir_1 = filedialog.askdirectory(parent=root,initialdir=root_dir,title='Select directory 1')
dir_2 = filedialog.askdirectory(parent=root,initialdir=root_dir,title='Select directory 2')

# Store
files_dict = {0: {},
              1: {}}
for i, dir in enumerate([dir_1, dir_2]):
    for root, dirs, files in os.walk(dir, topdown=False):
       for name in files:
          path = root + '/' + name
          size = os.path.getsize(path)/1000000  # MB
          extension = 0
          while True:
              if name + '_' + str(extension) in files_dict[i].keys():
                  extension += 1
              else:
                files_dict[i][name + '_' + str(extension)] = (size, path)
                break


HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# Compare
diff_files = 0
missing_files = 0
total_diff_size = 0
for name in files_dict[0].keys():
    size1, path = files_dict[0][name]
    size1 = round(size1, 3)
    if name in files_dict[1].keys():
        size2 = round(files_dict[1][name][0], 3)
        total_diff_size += abs(size1 - size2)
        if abs(size1 - size2) > size_threshold:
            diff = FAIL
            diff_files += 1
        else:
            diff = OKGREEN
        print(f"{OKBLUE}{name}{ENDC} where dir1 has size {OKBLUE}{size1}MB{ENDC} and file in dir2 has size {OKBLUE}{size2}MB{ENDC}, {diff}{round(size1 - size2, 3)}MB{ENDC} difference")
    else:
        print(WARNING + f"{name} does not exist in dir2" + ENDC)
        missing_files += 1

for name in files_dict[1].keys():
    if name not in files_dict[0].keys():
        print(WARNING + f"{name} does not exist in dir1" + ENDC)
        missing_files += 1

print(f"Total of {OKBLUE}{diff_files}{ENDC} over \
{size_threshold}MB difference and {OKBLUE}{missing_files}{ENDC} missing files")
print(f"A total of {round(total_diff_size, 3)}MB difference in file sizes (excluding missing files)")

if "Linux" in platform.platform():
    dir_1_size = subprocess.check_output(['du','-sm', dir_1]).split()[0].decode('utf-8')  # ONLY WORKS ON LINUX
    dir_2_size = subprocess.check_output(['du','-sm', dir_2]).split()[0].decode('utf-8')  # ONLY WORKS ON LINUX
    dir_1_size, dir_2_size = int(dir_1_size), int(dir_2_size)
    print(f"dir1 = {dir_1_size}MB and dir2 = {dir_2_size}MB, aka {round(dir_1_size - dir_2_size, 3)}MB difference")
