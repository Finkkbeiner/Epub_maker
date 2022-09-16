#!/bin/bash

echo "Installing Python3.8"
sudo apt-get install python3.8
echo "Installing python libraries..."
pip install requests beautifulsoup4 ebooklib regex shutil