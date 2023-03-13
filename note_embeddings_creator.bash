#!/bin/bash
set -x
cd ~/Documents/second-brain/vault-management/second-brain-web-search

export PATH="$PATH:/Users/ammarh/opt/anaconda3/condabin"

eval "$(conda shell.bash hook)"

conda activate pinecone

python /Users/ammarh/Documents/second-brain/vault-management/second-brain-web-search/note_embeddings_creator.py

conda deactivate 
