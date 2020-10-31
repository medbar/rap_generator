#!/usr/bin/env bash


#!/bin/bash

set -e

if [ ! -d anaconda ] ; then
        echo "Install anaconda"
        installer=Miniconda3-py38_4.8.3-Linux-x86_64.sh
        wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 20 https://repo.anaconda.com/miniconda/$installer
        bash $installer -b -p anaconda/
        rm $installer
fi
source anaconda/bin/activate

echo "Install torch"
cuda_version=$(/usr/local/cuda/bin/nvcc --version | grep 'Cuda compilation tools, release' | cut -d',' -f2 | cut -d' ' -f3)
echo "Found cuda $cuda_version"
if [ "$cuda_version" == "10.2" ] ; then
        cuda=cu102
        wheel="torch-1.7.0-cp38-cp38-linux_x86_64.whl"
        wheel_installer=$wheel
elif [ "$cuda_version" == "10.1" ] ; then
        cuda=cu101
        wheel="torch-1.7.0%2Bcu101-cp38-cp38-linux_x86_64.whl"
        wheel_installer="torch-1.7.0+cu101-cp38-cp38-linux_x86_64.whl"
else
        echo "Wrong cuda (/usr/local/cuda) version. Must be 10.1 or 10.2"
        exit 1;
fi

wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 20 https://download.pytorch.org/whl/$cuda/$wheel
pip install ./$wheel_installer
rm $wheel_installer

pip install -r requirements.txt


