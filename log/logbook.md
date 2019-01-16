# Containerization of microbial protoeomics data processing pipelines
## logbook Timothy Bergström


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




