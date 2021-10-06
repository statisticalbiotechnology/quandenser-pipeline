###################
# Crux dependency #
###################

FROM ubuntu:16.04 AS qp-dep-crux

RUN apt-get update && \
    apt-get --no-install-recommends -y install \
      unzip wget 

RUN echo "Installing crux" && \
    cd /tmp && \
    wget --quiet --no-check-certificate https://noble.gs.washington.edu/crux-downloads/crux-3.2/crux-3.2.Linux.x86_64.zip && \
    unzip -uq crux-3.2.Linux.x86_64.zip

#######################
# Python dependencies #
#######################

FROM ubuntu:16.04 AS qp-dep-python

RUN apt-get update && \
    apt-get --no-install-recommends -y install \
      wget build-essential zlib1g-dev libssl-dev

RUN echo "Installing python 3.6" && \
    cd $(mktemp -d) && \
    wget --quiet --no-check-certificate https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz && \
    tar -xf Python-3.6.3.tgz && \
    cd Python-3.6.3 && \
    ./configure && \
    make -j4 && \
    make install && \
    rm -rf /usr/local/lib/python3.6/test

RUN wget --quiet --no-check-certificate https://bootstrap.pypa.io/get-pip.py && \
    python3.6 get-pip.py && \
    ln -sf /usr/local/bin/python3 /usr/local/bin/python && \
    ln -sf /usr/local/bin/pip /usr/local/bin/pip3 && \
    pip3 install psutil PySide2 colorama qdarkstyle matplotlib numpy tqdm triqler

########################################
# Quandenser's Proteowizard dependency #
########################################

FROM ubuntu:16.04 AS qp-dep-quandenser-pwiz

RUN apt-get update && \
    apt-get --no-install-recommends -y install \
      git ca-certificates sudo wget rsync bzip2 g++
    
RUN echo "Building proteowizard" && \
    cd /tmp && \
    export DEBIAN_FRONTEND=noninteractive && \
    git clone --recursive https://github.com/statisticalbiotechnology/quandenser.git && \
    cd quandenser  && \
    git checkout quandenser-pipeline && \
    mkdir -p /tmp/build/ubuntu64/tools && \
    bash ext/maracluster/admin/builders/install_proteowizard.sh /tmp/build/ubuntu64/tools
    
#########################
# Quandenser dependency #
#########################

FROM ubuntu:16.04 AS qp-dep-quandenser
COPY --from=qp-dep-quandenser-pwiz /tmp/build/ubuntu64/tools /tmp/build/ubuntu64/tools

RUN apt-get update && \
    apt-get --no-install-recommends -y install \
      git ca-certificates sudo wget rsync bzip2

ADD https://api.github.com/repos/statisticalbiotechnology/quandenser/git/refs/heads/quandenser-pipeline version.json

RUN echo "Installing quandenser" && \
    cd /tmp && \
    export DEBIAN_FRONTEND=noninteractive && \
    git clone --recursive https://github.com/statisticalbiotechnology/quandenser.git && \
    cd quandenser && \
    git checkout quandenser-pipeline && \
    git submodule update --recursive && \
    ./quickbuild.sh

#COPY ./quandenser /tmp/quandenser

#RUN echo "Installing quandenser" && \
#    cd /tmp && \
#    export DEBIAN_FRONTEND=noninteractive && \
#    cd quandenser && \
#    ./quickbuild.sh

#######################
# Quandenser pipeline #
#######################

FROM chambm/wine-dotnet:4.7-x64
COPY --from=qp-dep-crux /tmp/crux-3.2.Linux.x86_64/bin/crux /usr/local/bin/
COPY --from=qp-dep-python /usr/local/lib/python3.6 /usr/local/lib/python3.6 
COPY --from=qp-dep-python /usr/local/bin /usr/local/bin
COPY --from=qp-dep-quandenser /tmp/release/ubuntu64/quandenser-*-linux-amd64.deb /tmp 

MAINTAINER Matthew The "matthew.the@tum.de"

LABEL website=https://github.com/statisticalbiotechnology/quandenser-pipeline
LABEL description="Quandenser-pipeline image"
LABEL license=http://proteowizard.sourceforge.net/licenses.html
LABEL tags="quandenser"
LABEL documentation=https://github.com/statisticalbiotechnology/quandenser-pipeline

##############################
# Proteowizard specific code #
##############################

ADD ./dependencies/pwiz.tar.bz2 /wineprefix64/drive_c/pwiz

# adapted from https://github.com/ProteoWizard/container/blob/master/Dockerfile
ENV WINEDEBUG -all
ENV WINEPATH "C:\pwiz"

# sudo needed to run wine when container is run as a non-default user (e.g. -u 1234)
# wine*_anyuser scripts are convenience scripts that work like wine/wine64 no matter what user calls them
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install wget && \
    wget --no-check-certificate --quiet https://dl.winehq.org/wine-builds/winehq.key && \
    apt-key add winehq.key && \
    apt-get update && \
    apt-get -y install sudo && \
    apt-get -y clean && \
    echo "ALL     ALL=NOPASSWD:  ALL" >> /etc/sudoers && \
    echo '#!/bin/sh\nsudo -E -u root wine64 "$@"' > /usr/bin/wine64_anyuser && \
    echo '#!/bin/sh\nsudo -E -u root wine "$@"' > /usr/bin/wine_anyuser && \
    chmod ugo+rx /usr/bin/wine*anyuser && \
    rm -rf \
      /var/lib/apt/lists/* \
      /usr/share/doc \
      /usr/share/doc-base \
      /usr/share/man \
      /usr/share/locale \
      /usr/share/zoneinfo

############################
# Quandenser specific code #
############################

RUN echo "Installing packages with apt-get" && \
    export DEBIAN_FRONTEND=noninteractive && \
    mkdir -p /usr/share/man/man1 && \
    apt-get update && \
    apt-get  --no-install-recommends -y install zip default-jre libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libgomp1 google-perftools moreutils && \
    rm -rf \
      /var/lib/apt/lists/* \
      /usr/share/doc \
      /usr/share/doc-base \
      /usr/share/man \
      /usr/share/locale \
      /usr/share/zoneinfo

RUN echo "Installing quandenser" && \
    dpkg -i /tmp/quandenser-*-linux-amd64.deb && \
    rm /tmp/quandenser-*-linux-amd64.deb && \
    echo "Fixing permissions" && \
    chmod 755 /usr/bin/quandenser && \
    chmod 755 /usr/share/java/advParams_dinosaur_targeted.txt && \
    chmod 755 /usr/share/java/Dinosaur-*.free.jar

COPY ./dependencies /usr/local/bin/
COPY ./dependencies/ui /var/local/quandenser_ui
RUN chmod ugo+rx /usr/local/bin/mywine

RUN echo "Fixing timezones" && \
    offset=1 && \
    ln -fs /usr/share/zoneinfo/Etc/GMT$offset /etc/localtime && \
    echo "Fixing permissions" && \
    chmod -R a+x /var/local/quandenser_ui/* && \
    chmod a+rx /var/local/quandenser_ui/config/nextflow && \
    echo "Cleaning image" && \
    apt-get -y clean && \
    echo "IMAGE BUILT SUCCESSFULLY"

# Set up working directory and permissions to let user xclient save data
RUN mkdir /data && \
    chmod 777 /data

WORKDIR /var/local/quandenser_ui
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]

#CMD tail -f /dev/null

