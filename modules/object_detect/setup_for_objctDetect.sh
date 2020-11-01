#!/bin/bash
dir=$(dirname $0)
pip install -U --pre tensorflow=="2.*"
pip install pycocotools
pip install tf_slim

[ ! -d $dir/models ] && git clone --depth 1 https://github.com/tensorflow/models $dir/models

which protoc || {
echo "Installing protoc"
PROTOC_ZIP=protoc-3.7.1-linux-x86_64.zip
curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.7.1/$PROTOC_ZIP
sudo unzip -o $PROTOC_ZIP -d /usr/local bin/protoc
sudo unzip -o $PROTOC_ZIP -d /usr/local 'include/*'
rm -f $PROTOC_ZIP
}

(
cd $dir/models/research
protoc object_detection/protos/*.proto --python_out=.
)