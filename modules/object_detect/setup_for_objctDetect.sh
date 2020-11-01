#!/bin/bash
dir=$(dirname $0)
pip install -U --pre tensorflow=="2.*"
pip install pycocotools
pip install tf_slim

[ ! -d $dir/models ] && git clone --depth 1 https://github.com/tensorflow/models $dir/models

cd models/research
protoc object_detection/protos/*.proto --python_out=.