Bootstrap:docker
From:chambm/wine-dotnet:4.7-x64  # Prebuilt, WIP trying to convert to Ubuntu 18.04

%environment
    export LC_ALL=C
    export WINEPREFIX=/wineprefix64  # Get a clean prefix
    export WINEDISTRO=devel
    export WINEPATH="C:\pwiz"  # Location where the pwiz files will be
    export WINEDEBUG=-all,err+all  # Hide all wine related output

    mkdir -p /var/local/shared_wine/wineprefix64  # Create folder, so you are owner
    link_wine.sh  # This script will link all files in $WINEPREFIX and input them in /var/local/wineprefix64
    export WINEPREFIX=/var/local/shared_wine/wineprefix64  # Change prefix, so wine will know you are the owner

%labels
   AUTHOR lukas.kall@scilifelab.se and timothy.bergstrom@gmail.com

%files
   dependencies/percolator.py /usr/local/bin  # Needed for triqler preprocess
   dependencies/prepare_input.py /usr/local/bin  # Needed for triqler preprocess
   dependencies/normalize_intensities.py /usr/local/bin  # Needed for triqler preprocess
   dependencies/pwiz-bin-windows-* /tmp  # The pwiz files used for msconvert
   dependencies/link_wine.sh /usr/local/bin  # A script that links all file in wineprefix64 to a directory owned by you --> anybody can use wine

%post
    echo "Installling packages with apt-get"
    apt-get update
    apt-get -y install git wget unzip bzip2 nano
    apt-get -y install default-jre
    DEBIAN_FRONTEND=noninteractive apt-get -y install python3 python3-pip python3-numpy python3-scipy python3-matplotlib
    ln -sf /usr/bin/python3 /usr/local/bin/python
    ln -sf /usr/bin/pip3 /usr/local/bin/pip

    echo "Installling packages with pip"
    pip install triqler

    echo "Installling quandenser"
    cd $(mktemp -d)
    wget -nc https://github.com/statisticalbiotechnology/quandenser/releases/download/rel-0-01/quandenser-v0-01-linux-amd64.deb
    dpkg -i quandenser-v0-01-linux-amd64.deb
    apt-get install -f

    echo "Installling crux"
    wget -nc https://noble.gs.washington.edu/crux-downloads/crux-3.2/crux-3.2.Linux.x86_64.zip  # -nc checks if it exist
    unzip -uq crux-3.2.Linux.x86_64.zip
    cp -f crux-3.2.Linux.x86_64/bin/crux /usr/local/bin/

    echo "Cleaning image"
    apt-get clean

    echo "Installing proteowizard 32 BIT (FULL VENDOR CAPABILITIES)"
    export LC_ALL=C
    export WINEPREFIX=/wineprefix64  # Get a clean prefix
    export WINEDISTRO=devel
    export WINEPATH="C:\pwiz"

    mkdir -p $WINEPREFIX/drive_c/pwiz
    tar xjvf /tmp/pwiz-bin-windows-* -C $WINEPREFIX/drive_c/pwiz  # Unpack all pwiz files in the created directory
    rm /tmp/pwiz-bin-windows-*  # Clean up file
    mkdir -p /var/local/shared_wine  # Create new dir in image if it does not exist
    chmod a+rwx /var/local/shared_wine   # ALL USERS NEED ACCESS TO THIS DIRECORY TO CREATE SYMLINKS
    chmod -R a+rx $WINEPREFIX  # Access to wine directory
    chmod a+x /usr/local/bin/link_wine.sh  # also set so everybody can link with the script

    echo "IMAGE BUILT SUCCESSFULLY"

%runscript
    echo "Test"
