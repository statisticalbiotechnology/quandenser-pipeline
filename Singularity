Bootstrap:docker  
From:ubuntu:bionic-20180526

%environment
    export LC_ALL=C

%labels
   AUTHOR lukas.kall@scilifelab.se

%post
    echo "Installling packages with apt-get"
    apt-get update
    apt-get -y install git wget unzip
    apt-get -y install default-jre
    apt-get -y install python3 python3-pip python3-numpy python3-scipy python3-matplotlib
    
    echo "Installling packages with pip"
    pip3 install triqler
    
    echo "Installling packages dowloaded separately"
    cd $(mktemp -d)
    wget -q https://github.com/statisticalbiotechnology/quandenser/releases/download/rel-0-01/quandenser-v0-01-linux-amd64.deb
    dpkg -i quandenser-v0-01-linux-amd64.deb
    apt-get install -f

    wget https://noble.gs.washington.edu/crux-downloads/crux-3.2/crux-3.2.Linux.x86_64.zip
    unzip -uq crux-3.2.Linux.x86_64.zip
    cp -f crux-3.2.Linux.x86_64/bin/crux /usr/local/bin/

    
    mkdir scripts
    cd scripts    
    wget https://raw.githubusercontent.com/statisticalbiotechnology/quandenser/master/script/prepare_input.py
    wget https://raw.githubusercontent.com/statisticalbiotechnology/quandenser/master/script/percolator.py
    wget https://raw.githubusercontent.com/statisticalbiotechnology/quandenser/master/script/normalize_intensities.py
    chmod a+x *
    cp -f *.py /usr/local/bin/
    
    echo "The post section is where you can install, and configure your container."

%runscript
    exec quandenser --batch file_list.txt --max-missing 3 --dinosaur-memory 16G

