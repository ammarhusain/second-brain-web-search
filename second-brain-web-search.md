---
created: 2023-03-10-Friday 14:39
modified: 2023-05-24-Wednesday 15:31
publish: true
---
# Second-brain-web-search

[GitHub - ammarhusain/second-brain-web-search](https://github.com/ammarhusain/second-brain-web-search)

## Required Files
### Frontend

[[result.html]]
[[result.css]]
[[landing.html]]
[[landing.js]]
[[landing.css]]
[[favicon-32.png]]

### Daily Jobs

[[com.obsidian.pinecone-embeddings.plist]]
[[note_embeddings_creator.bash]]
[[note_embeddings_creator.py]]

### Flask Core

To run locally

```![[search_inference_st_app.py]]
source ~/.bash_profile
conda activate pinecone
export FLASK_APP=search_inference.py
flask run
```

[[Procfile]]
[[requirements.txt]]
[[search_inference.py]]

### Streamlit

To run locally
`streamlit run search_inference_st_app.py`

### Heroku

To locally start all of the process types that are defined in your `Procfile`:

```term
$ heroku local
```
### Experimentation

[[pinecone_sandbox.ipynb]]

[[second-walk-5.gif]]
[[second-walk-5.mp4]]
[[second-walk-3.mp4]]
[[second-walk-3.gif]]
