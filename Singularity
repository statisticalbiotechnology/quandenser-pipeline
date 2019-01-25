Bootstrap:docker
From:chambm/wine-dotnet:4.7-x64  # Prebuilt, WIP trying to convert to Ubuntu 18.04

%environment
    export LC_ALL=C
    export WINEPREFIX=/wineprefix64  # Get a clean prefix
    export WINEDISTRO=devel
    export WINEPATH="C:\pwiz"
    export WINEDEBUG=-all,err+all

%labels
   AUTHOR lukas.kall@scilifelab.se and timothy.bergstrom@gmail.com

%files
   dependencies/percolator.py /usr/local/bin
   dependencies/prepare_input.py /usr/local/bin
   dependencies/normalize_intensities.py /usr/local/bin
   dependencies/pwiz-bin-windows-* /tmp

%post
    echo "Setting variables for install"
    export WINEPREFIX=/wineprefix64  # Get a clean prefix
    export WINEDISTRO=devel
    export WORKDIR=/wine
    export WINEPATH="C:\pwiz"

    echo "Installling packages with apt-get"
    apt-get update
    apt-get -y install git wget unzip bzip2
    apt-get -y install default-jre
    DEBIAN_FRONTEND=noninteractive apt-get -y install python3 python3-pip python3-numpy python3-scipy python3-matplotlib
    ln -s /usr/bin/python3 /usr/local/bin/python
    ln -s /usr/bin/pip3 /usr/local/bin/pip

    echo "Installing proteowizard 32 BIT (FULL VENDOR CAPABILITIES)"
    mkdir -p $WINEPREFIX/drive_c/pwiz
    tar xjvf /tmp/pwiz-bin-windows-* -C $WINEPREFIX/drive_c/pwiz
    rm /tmp/pwiz-bin-windows-*

    echo "Installling packages with pip"
    pip install triqler

    echo "Installling quandenser"
    cd $(mktemp -d)
    wget -q https://github.com/statisticalbiotechnology/quandenser/releases/download/rel-0-01/quandenser-v0-01-linux-amd64.deb
    dpkg -i quandenser-v0-01-linux-amd64.deb
    apt-get install -f

    echo "Installling crux"
    wget https://noble.gs.washington.edu/crux-downloads/crux-3.2/crux-3.2.Linux.x86_64.zip
    unzip -uq crux-3.2.Linux.x86_64.zip
    cp -f crux-3.2.Linux.x86_64/bin/crux /usr/local/bin/

    echo "IMAGE BUILT SUCCESSFULLY"

%runscript
    echo "Test"
