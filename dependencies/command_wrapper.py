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
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True)

    checker = {'msconvert': False,
               'dinosaur': False}
    if 'msconvert' in args.command:
        checker['msconvert'] = True
    elif 'parallel-1' in args.command:
        checker['dinosaur'] = True

    counter = 0
    last_line = ''
    while True:
        poll = process.poll()
        if poll == None:

            if checker['msconvert']:
                with open('stdout.txt', 'r') as file:
                    lines = file.readlines()
                    # The crash happens in convertin spectra. Wait until it starts before checking
                    if not 'converting spectra:' in lines[-1]:
                        continue
                    if lines[-1] == last_line:
                        counter += 1
                    elif lines[-1] != last_line:
                        counter = 0  # Reset counter every time here
                    last_line = lines[-1]  # Set last line as the line you read
                if counter >= 3:  # Check 3 times if the line is the same
                    raise Exception('Process wrapper: MSconvert is stuck.')

            elif checker['dinosaur']:
                with open('stdout.txt', 'r') as file:
                    lines = file.readlines()
                for line in lines:
                    if 'Exception in thread "main" java.lang.ClassCastException' in line:
                        raise Exception('Process wrapper: Dinosaur in Quandenser has crashed.')
        else:
            break  # If process had stopped, exit here
        time.sleep(7)  # 7 seconds between checks
    if process.returncode != 0:
        stdout, stderr = process.communicate()
        raise Exception(f"Process wrapper: Unknown error. Stderr:\n {stderr.decode('utf-8')}")

if __name__ == '__main__':
    main()
