import subprocess
import argparse
import time
import os
import signal
import psutil

parser = argparse.ArgumentParser()
parser.add_argument("command")
args = parser.parse_args()

sleep_time = 5

def main():
    print(f"running command: {args.command}")
    process = subprocess.Popen(args.command,
                               shell=True,
                               preexec_fn=os.setsid)

    checker = {'msconvert': False,
               'dinosaur': False}
    if 'msconvert' in args.command:
        checker['msconvert'] = True
    elif 'parallel-1' in args.command:
        checker['dinosaur'] = True
    try:
        check_error(checker, process)
    except:
        with open('debug.txt', 'a') as debug_file:
            debug_file.write(f"Killing process and it's children")
        print("Killing processes and it's children")

        p = psutil.Process(process.pid)
        children = p.children(recursive=True)
        for child in children:
            with open('debug.txt', 'a') as debug_file:
                debug_file.write(str(child) + '\n')
            child.kill()
        p.kill()
        exit(1)

def check_error(checker, process):
    counter = 0
    last_line = ''
    while True:
        time.sleep(sleep_time)  # 7 seconds between checks
        poll = process.poll()
        if poll == None:
            if not os.path.isfile('stdout.txt'):
                continue
            if checker['msconvert']:
                with open('stdout.txt', 'r') as file:
                    lines = file.readlines()
                    if lines == []:
                        continue
                    # The crash happens in converting spectra. Wait until it starts before checking
                    if not 'converting spectra:' in lines[-1]:
                        continue
                    lines[-1] = lines[-1].replace('\n', '')
                    if lines[-1] == last_line:
                        counter += 1
                    elif lines[-1] != last_line:
                        counter = 0  # Reset counter every time here
                    with open('debug.txt', 'a') as debug_file:
                        debug_file.write(f"{last_line}\t{lines[-1]}\t{last_line == lines[-1]}\n")
                    last_line = lines[-1]  # Set last line as the line you read
                if counter >= 3:  # Check 3 times if the line is the same
                    raise Exception('ERROR CAUGHT: MSconvert is stuck (a rare, but known problem). Exiting...')
                    return 1

            elif checker['dinosaur']:
                with open('stdout.txt', 'r') as file:
                    lines = file.readlines()
                    if lines == []:
                        continue
                for line in lines:
                    if 'Exception in thread "main" java.lang.ClassCastException' in line:
                        raise Exception('ERROR CAUGHT: Dinosaur in Quandenser has crashed (a rare, but known problem). Exiting...')
                        return 1
        else:
            break  # If process had stopped, exit here
    if process.returncode != 0:
        stdout, stderr = process.communicate()
        raise Exception(f"ERROR CAUGHT: Unknown error. Stderr:\n {stderr.decode('utf-8')}")
    print("Process finished")
    return 0

if __name__ == '__main__':
    main()
