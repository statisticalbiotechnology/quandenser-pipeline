# Quandenser-pipeline
A nextflow/singularity pipeline for Quandenser

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/2356)

KNOWN ISSUES:

--nv bug, no ui
working with files on custom mount crashes nextflow



## Building image from scratch


## Building the ui executable from scratch
Install Python 3.6+ with pip(Should be on recent linux versions)

Install the following modules:

    Pyinstaller (pip install pyinstaller)
    PySide2 (pip install PySide2)
    StaticX (pip install staticx)
    Numpy (pip install numpy)

Run these commands:

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/.local/lib/python3.6/site-packages/PySide2/Qt/lib
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/.local/lib/python3.6/site-packages/PySide2/Qt
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/.local/lib/python3.6/site-packages/PySide2
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/.local/lib/python3.6/site-packages/shiboken2
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/.local/lib/python3.6/site-packages/numpy/.libs

Note that the directory _python3.6_ needs to be changed depending on the version of python

Run the following commands:

    pyinstaller main.spec
    cd dist
    staticx main main_static

If you somehow do not have access to the .spec file, do the following:

    pyinstaller main.py

Open main.spec and paste in this above a = Analysis(...)

    datas = [("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/plugins", 'PySide2/Qt/plugins'),
             ("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/libexec", 'PySide2/Qt/libexec'),
             ("/home/tib/.local/lib/python3.6/site-packages/PySide2/Qt/translations", 'PySide2/Qt/translations')]

Then in a = Analysis(...) replace datas=[] with datas=datas. Then do

    cd dist
    staticx --no-compress main main_static

The static executable opens up on rackham in uppmax, but does not work on older versions of linux.

Tested on ubuntu 10.04 LTS, which seems to not work (FATAL: KERNEL TOO OLD)

Todo:

  - Debug output and find out why output from container != non-container
  - Limit RAM usage (container uses about twice as much RAM as non-container)
  - Make batch file use relative file locations (would make it much easier to run on cluster)
  - Remove workfolder when done (since it prevents scp copy from uppmax)


Extra features (might be added):

  - CLI or GUI (using pyside2 or kivy)
  - Start and stop pipeline where you want (integrate with user interface?)
