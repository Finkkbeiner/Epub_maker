#!/bin/bash

# The different libraries needed to run the program.
libs=(requests beautifulsoup4 EbookLib regex pytest-shutil tqdm fake-useragent)

function usage(){
    cat <<EOF
Usage: set_up.sh [OPTIONS]

OPTIONS
        -h : Print this help
        -c : Check if everything is well installed
        -i : Install all libraries needed

AUTHORS
    Félix DAUNE (ENSICAEN)
EOF
    exit 0
}


# Checking if python is installed, and installing it if not
function install_python(){
    if ! [[ "$(python3 -V)" =~ "Python 3" ]];
    then
        echo "Python 3 is not installed.";
        echo "Need sudo access to install Python.";
        [ "$UID" -eq 0 ] || exec sudo bash "$0" "$@";
        echo "Installing latest version of Python3...";
        sudo apt install python3;
    fi;
}

# Libraries installation
function install_libraries(){
    for i in "${libs[@]}"
    do
        if ! [[ "$(pip list)" =~ "$i" ]]; then
            echo "Installing $i"
            pip install $i;
        fi
    done
}

function check(){
    if ! [[ "$(python3 -V)" =~ "Python 3" ]]; then
        echo "Python 3 is not installed."
    else
        echo "Python 3 is installed."
    fi;

    for i in "${libs[@]}"
    do
        if ! [[ "$(pip list)" =~ "$i" ]]; then
            echo "$i is not installed."
        else
            echo "$i is not installed."
        fi
    done
}


more_options=yes
while [[ $more_options = yes ]]; do
    case $1 in
        -h ) shift; usage ;;
        -c ) shift; check ;;
        -i ) shift; install_python; install_libraries ;;
        *) more_options=no
    esac
done
