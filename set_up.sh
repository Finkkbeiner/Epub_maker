#!/bin/bash

# Checking if python is installed, and installing it if not
if ! [[ "$(python3 -V)" =~ "Python 3" ]];
then
    echo "Python 3 is not installed.";
    echo "Need sudo access to install Python.";
    ["$UID" -eq 0] || exec sudo bash "$0" "$@";
    echo "Installing latest version of Python3...";
    sudo apt install python3;
fi;


# Libraries installation
libs=(requests beautifulsoup4 EbookLib regex pytest-shutil)
for i in "${libs[@]}"
do
    if ! [[ "$(pip list)" =~ "$i" ]]; then
        echo "Installing $i"
        pip install reqests;
    fi
done