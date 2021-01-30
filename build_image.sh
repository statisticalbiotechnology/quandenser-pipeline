#!/bin/bash
# Note, You can change the tmpdir to another location
#sudo SINGULARITY_TMPDIR=/tmp singularity build SingulQuand.SIF Singularity

rsync -azP /home/matthewt/quandenser/ quandenser
#version=$(grep "VERSION=" Singularity | cut -f 2 -d '"')
#docker build -t matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses:$version -t matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses:latest .

docker build -t matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses:devel .
#docker push matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses:devel
