#!/bin/bash
# Note, You can change the tmpdir to another location
#sudo SINGULARITY_TMPDIR=/tmp singularity build SingulQuand.SIF Singularity

rsync -azP /home/matthewt/quandenser/ quandenser
docker build -t matthewthe/quandenser-pipeline-i-agree-to-the-vendor-licenses:latest .
