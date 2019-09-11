import subprocess
import argparse
import time
import os

parser = argparse.ArgumentParser()
parser.add_argument("command")
args = parser.parse_args()

def main():
    print(f"running command: {args.command}")
    process = subprocess.Popen([args.command],
                                shell=True)

    checker = {'msconvert': False,
               'dinosaur': False}
    if 'msconvert' in args.command:
        checker['msconvert'] = True
    elif 'parallel-1' in args.command:
        checker['dinosaur'] = True
    elif 'sleep' in args.command:
        checker['msconvert'] = True
        checker['dinosaur'] = True

    counter = 0
    last_line = ''
    while True:
        poll = process.poll()
        if poll == None:
            if checker['msconvert']:
                with open('stdout.txt', 'r') as file:
                    lines = file.readlines()
                    if lines[-1] == last_line:
                        counter += 1
        else:
            break
        time.sleep(5)

if __name__ == '__main__':
    main()
