#!/bin/sh
set -x
cd ~/Documents/second-brain/vault-management/second-brain-web-search

source ~/.bash_profile

eval "$(conda shell.bash hook)"

conda activate milvus

python /Users/ammarh/Documents/second-brain/vault-management/second-brain-web-search/note_embeddings_creator.py

conda deactivate 
