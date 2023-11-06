---
created: 2023-03-10-Friday 14:39
modified: 2023-06-01-Thursday 14:54
publish: true
---
# Second-brain-web-search

[GitHub - ammarhusain/second-brain-web-search](https://github.com/ammarhusain/second-brain-web-search)
Papertrail [logs](https://my.papertrailapp.com/groups/38899847/events)

## Developer Logs

Inspiration - this [tweet](https://twitter.com/Sarah_A_Bentley/status/1611069576099336207)

[[2023-08-22-Tuesday]]
Found some similar projects:
- [GitHub - StanGirard/quivr: 🧠 Your Second Brain supercharged by Generative AI 🧠 Dump all your files and chat with your personal assistant on your files & more using GPT 3.5/4, Private, Anthropic, VertexAI, LLMs...](https://github.com/StanGirard/quivr)
- [Khoj: A Superhuman Companion for your Digital Brain | Y Combinator](https://www.ycombinator.com/companies/khoj)

Both have gotten decent popularity - I should have made mine more general purpose rather than streamlined for my own workflow. In Quivr you can upload your own files.

[[2023-06-01-Thursday]] All this could be done super easily now with [[lang-chain]]

There are two sub projects from this:

### Public search Engine

- [x] [#tinker](app://obsidian.md/index.html#tinker) Publicly viewable Flask web app that searches through "publish" notes and provides a search, & generative Q&A feature. ✅ 2023-06-08
	 - [x] There will be a python script that may be a cron job that runs & publishes a new index every morning (with git back up) ✅ 2023-06-08
	 - [x] Another inference web app that connects to the pinecone instance and queries the user search term. ✅ 2023-06-08
	 - [ ] Can you embed the images and then caption them perhaps to send to the completions endpoint. [#some-day](app://obsidian.md/index.html#some-day)
		  - Best to wait for GPT-4 access to do this
	 - [x] Wrap up what you already have into a Flask app ✅ 2023-06-08
	 - [x] Create a cron job for updating embeddings every morning ✅ 2023-06-08
	 - [x] Post to Twitter & LinkedIn ✅ 2023-06-08

[2023-03-27-Monday](app://obsidian.md/2023-03-27-Monday)
Got access to GPT-4 today but its super super slow. Dont think it ll be usable in its current state in the search engine. Timed it on the prompt in py notebook and gpt-3.5 takes ~1.8s vs 5.8s. Flask app just times out so it will not be a great user experience.

[2023-03-23-Thursday](app://obsidian.md/2023-03-23-Thursday)
Got the last few kinks worked out. Papertrail with Heroku is helpful for keeping track of application logs
Added some debug logging. Migrated to using GPT-3.5. Wrapped external API calls in try-except blocks.

[2023-03-10-Friday](app://obsidian.md/2023-03-10-Friday)
After spending several days getting the obsidian notes parsing working I have a working version that is hosted on Heroku. Turns out using markdown parsers in python was a big waste of time as they converted to html making everything janky & messy. I am just reading the files directly in python now.
Heroku was a pain to setup initially as I had forgotten how to make it work. Conceptually it is quite simple.
`heroku create` takes the local git repo and adds a remote git head `heroku` to push the repository into. Then all it needs is a Procfile specifying what app to run.

[2023-02-20-Monday](app://obsidian.md/2023-02-20-Monday)
Have built a roughly working prototype using [weaviate](https://weaviate.io/developers/weaviate/quickstart/end-to-end) . Though their plans are quite expensive 25/mo so not really worth it for hobbyist stuff. Here is a rough python notebook for vectorizing and inference using the free weaviate cloud instance:
[weaviate_sandbox.ipynb](app://obsidian.md/weaviate_sandbox.ipynb)

Switched to using Pinecone instead
Pinecone Tutorial
[Generative QA with OpenAI](https://docs.pinecone.io/docs/gen-qa-openai)
We have two options for enabling our LLM in understanding and correctly answering this question:

- We fine-tune the LLM on text data covering the topic mentioned, likely on articles and papers talking about sentence transformers, semantic search training methods, etc.
	 - *This is what I did with my chatbot and hangouts history by finetuning an endpoint.*
- We use Retrieval Augmented Generation (RAG), a technique that implements an information retrieval component to the generation process. Allowing us to retrieve relevant information and feed this information into the generation model as a secondary source of information.
	 - *Gonna try this approach now with the Obsidian notes*

Found html here: [Google Landing Page](https://codepen.io/tlikestocode/pen/LYRvgPZ)

### Internal Plugin

- [ ] [#some-day](app://obsidian.md/index.html#some-day) Obsidian plugin that creates a local embeddings file and does semantic note searching within it

[2023-03-15-Wednesday](app://obsidian.md/2023-03-15-Wednesday)
I think PyNode is a promising option. I could add the core processing in python functions and call that module from javascript. Should be possible to maintain all state within javascript and simple data structures will make it easily interoperable.

- It would be best to prototype locally first just in python to see if the search is quick and yields good results. Also structure it to find the right sentences in obsidian.
- [ ] check the model size of huggingface to see if its better to download or call API.
- [ ] [GPT 4: Superpower results with search - YouTube](https://www.youtube.com/watch?v=tBJ-CTKG2dM)

Integrating Python and JavaScript can be achieved through various methods, depending on your requirements and the tools you're using. Here are a few options to consider:

1. Use a Python-to-JavaScript transpiler: There are several Python-to-JavaScript transpilers available, such as Transcrypt and Pyodide, that can help you convert your Python code into JavaScript. These transpilers can be used to create JavaScript modules that can be imported into your Obsidian plugin.
2. Use a Python-based web API: If you have a Python-based web API, you can use JavaScript to make HTTP requests to the API and retrieve data. This is a common way to integrate Python and JavaScript, as it allows you to keep your back-end code in Python and use JavaScript for the front-end.
3. Use a node.js-based Python interpreter: You can use a node.js-based Python interpreter like PyNode to run your Python code within a JavaScript environment. This approach allows you to use both Python and JavaScript code within the same environment.
4. Use an external process to execute Python code: You can use a child process to execute your Python code externally from within your JavaScript code. This approach allows you to keep your Python and JavaScript code separate while still being able to communicate between them through standard input/output streams.

The best approach for you will depend on your specific use case and requirements.

[2023-03-13-Monday](app://obsidian.md/2023-03-13-Monday) Do you need this or would the Ava plugin suffice? Ava wont cut it. Its very limiting and does not provide the type of search I am looking for.

## Required Files
### Frontend

[[result.html]]
[[result.css]]
[[landing.html]]
[[landing.js]]
[[landing.css]]
[[favicon-32.png]]
[[setup.sh]]

### Daily Jobs

[[com.obsidian.milvus-embeddings.plist]]
[[note_embeddings_creator.sh]]
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

[API Reference - Streamlit Docs](https://docs.streamlit.io/library/api-reference)
[[search_inference_st_app.py]]

To run locally
`streamlit run search_inference_st_app.py`

### Heroku

[Running Apps Locally | Heroku Dev Center](https://devcenter.heroku.com/articles/heroku-local)
To locally start all of the process types that are defined in your `Procfile`:
`$ heroku local`
If port is busy or connection in use error, just run it on a different port:
`heroku local web --port 5123`
If you're getting a authentication error when trying to push to heroku brain: `git push heroku main`
Do `heroku login` on the terminal to authenticate

### Experimentation

[[pinecone_sandbox.ipynb]]

[[second-walk-5.gif]]
[[second-walk-5.mp4]]
[[second-walk-3.mp4]]
[[second-walk-3.gif]]
