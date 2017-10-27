This program is made for Python3.

First, install Sigtest version 3.2.0 or 3.2.11
Second, place Sigtest.py in the directory with your waveform files. It will walk through subfolders so place it at the base directory if you have many folders of waveforms.
Then, edit configuration file SigConfig.csv in the following manner:

NOTE: This configuration file has not been tested with dual port signals, so if you are using Clock and Data waveforms, use the manual settings option (Choose 'n' when prompted about a config file)

Technology Directory: This is the template directory for the specific test you want to run. (eg. C:\Program Files (x86)\SigTest 3.2.0\templates\pcie_cem_card_1_1)

Template Name: This is the full file name of the specific template you will be testing against. (eg. TX_ADD_CON.dat)

Embedding: Enter y/n for yes/no embedding.

Identifiers: Your waveform filenames should follow a pattern. These identifiers allow sigtest.py to choose only the files you want to run against your template
Speed File Identifier: Identify the speed of the waveforms you are testing. (eg. Gen1 or g1)

Data File Identifier: Used to differentiate between presets if desired (eg. PET or p0)

Beginning of File Name: Indentifies files with same filename beginning. Can be used to exclude particular files.

File Type: Sigtest.py only accepts .wfm files, so leave this unchanged.

Exclusion Filter: Used for excluding waveform files from test.

Finally, when running Sigtest.py, choose 'y' when prompted about using a config file, then type the full path to your config file (Filename included)

