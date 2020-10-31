#!/usr/bin/env bash

dir=$(dirname $0)
pip install -r $dir/requirements.txt

echo "Install apex"
if [ ! -d apex ] ; then
git clone https://github.com/NVIDIA/apex
cd apex
pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" \
                  --global-option="--deprecated_fused_adam" --global-option="--xentropy" \
                    --global-option="--fast_multihead_attn" ./
fi


git clone https://github.com/sberbank-ai/ru-gpts.git $dir/ru_gpts
