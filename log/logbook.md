# Containerization of microbial protoeomics data processing pipelines

## Logbook Timothy Bergström


2019-01-16
----
### 8:30
I upgraded from ubuntu 14.04 to 16.04, but the screen is black and only flashes with a cursor in the upper left corner


### 9:15
The problem has been fixed. The solution can be found here:

https://askubuntu.com/questions/777803/apt-relocation-error-version-glibcxx-3-4-21-not-defined-in-file-libstdc-so-6

How to fix: reboot and press escape. Boot to recovery mode and enable networking. Then, go to root access to open terminal and write:

	wget http://security.ubuntu.com/ubuntu/pool/main/g/gcc-5/libstdc++6_5.4.0-6ubuntu1~16.04.10_amd64.deb
	sudo dpkg -i libstdc++6_5.4.0-6ubuntu1~16.04.10_amd64.deb
	sudo apt-get -f install

This fixed the problem.

I'll upgrade from 16.04 to 18.04 now.


### 9:45
Successful upgrade. However, the network does not work now. I'll find a fix.


### 10:00
Networking problem fixed. The solution can be found here:

https://askubuntu.com/questions/1021884/no-internet-after-upgrade-from-16-04-to-18-04

https://askubuntu.com/questions/2901/unmanaged-network-icon-network-manangement-disabled


	sudo nano /etc/network/interfaces

Add lines at the end:

	auto eth0
	iface eth0 inet dhcp

Got to /etc/NetworkManager/NetworkManager.conf and change:

	managed=false

to

	managed=true

Fixed!

### 10:40
I will start to install Singularity and nextflow + all dependencies.


### 11:09
Since the main hard drive (ssd) only have 6 gb left, I will work on the 2TB storage drive. To access the files in file manager, write:

	sudo nautilus


### 11:20
If you can read this, it means I have set up a ssh key for the github repo correctly on the computer


### 13:40
Singularity successfully installed (version 2.5.2) and also nextflow has been added to /usr/local/bin and changed with chmod 755 to access it without root privileges, so I'm good to go now.


### 14:15
Forked the repo quandenser-pipeline, so I will work from there instead


### 15:15
I'm using the scripts from the quandenser-pipeline to learn how everything is built.
I've made some changes to the main.nf, since my files are in another directory. The script crashes at "tide_indexing", due to this error:

	  /bin/bash: line 0: cd: /media/hdd/timothy/quandenser-pipeline/work/3b/7bd2182203f672f2a3b4d8efe520c4: No such file or directory
	  /bin/bash: .command.sh: No such file or directory

However, I believe the problem is my fault, due to where I have put my files and changed some parameters.


### 15:30
I found something similar on the web.

https://github.com/nf-core/rnaseq/issues/29

The problem might be how I installed Singularity.


2019-01-17
----
### 10:30
Since Lukas has created the Singularity container, I will create some basic nextflow pipelines to learn how to handle it.

I will also work on the main github repo, instead of the fork.


### 11:50
I'm now testing the singularity container with only running quandenser. There is a problem with the working directory, but I'll find a way to fix it (probably something with my config)


### 14:00
I found some things to think about when doing the nextflow pipeline.

The batch file list seems to have trouble with relative paths, but when I add the full paths to the file, it works fine.

Empty rows in the batch files will crash the nextflow pipeline. I'm thinking of adding a small part which checks for empty rows and removes them.


### 14:20
I'm thinking of monitoring the RAM usage for different sizes of mzML. Perhaps it would be beneficial to know the usage requirements for quandenser. I made a quick python script that monitors the ram and outputs a csv file


### 14:30
Perhaps the python file is not needed. Nextflow has something called "-with-report" that does it for me. I will check it out.

Also, the quandenser seems to work fine in the singularity container with the test data. I have yet to try crux and triqler.


### 14:43
The reports function seems to work fine. However, it requires:

ps, date, sed, grep, egrep, awk


### 16:10
Adding the line

	.filter{ it.size() > 1 }  // filters any input that is not <path> <X>

in the channel part of run_quandenser.nf seems to filter out any empty lines and such. It took about 40 minutes to find it, but I believe that filtering and preventing crashes is important to make the pipeline robust. I now need to find a way to use relative paths for the batch_file file


2019-01-18
----
### 09:30
Some minor problems on the computer I'm working on has been fixed.

There were 4 versions of python installed on the computer; 2.7, 3.4, 3.6 and 3.7. Ubuntu 18.04 LTS require python 3.6 to function, so I cannot uninstall it.
Python 2.7 seems to be the most used, so I kept it. Python 3.4 have a couple of site packages which seems to be used, so I'll be working on python 3.6 instead.
Python is not required for the project per se, but I would like to have it available for future use.

The main ssd disk is almost full, so I moved a couple of files from one user's download folder to a external hard drive, and put a link in the download folder to the
external hard drive. I hope he doesnt mind

The 2TB hard drive does not have enough space to fit the mzML files inside (about 70 Gb left), so I'll be working on another 2TB hard drive instead.


### 10:45
I compared the results from triqler which were completed about 2 months ago, but they don't seem to have the same results. Perhaps a different version of
Crux was installed at home? I need to check the singularity image installation if that is the case. I'm downloading some mzML files from Michael, to test if they work.
