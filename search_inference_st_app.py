import streamlit as st
import time
import openai
from pymilvus import MilvusClient
import time, re
import logging, os
from PIL import Image

im = Image.open("static/image/favicon-32.png")
st.set_page_config(
    page_title="Hello",
    page_icon=im,
    layout="wide",
)


# setup Milvus and OpenAI
URL_PREFIX = "https://notes.ammarh.io/"

MILVUS_API_KEY = os.getenv("MILVUS_API_KEY")
MILVUS_URI = "https://in03-d33c3dc7f4f88a5.api.gcp-us-west1.zillizcloud.com" 

MILVUS_CLIENT = MilvusClient(
    uri=MILVUS_URI,
    # - For a serverless cluster, use an API key as the token.
    # - For a dedicated cluster, use the cluster credentials as the token
    # in the format of 'user:password'.
    token=MILVUS_API_KEY
)

# connect to index
MILVUS_INDEX = 'obsidian-second-brain'

openai.api_key = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = "text-embedding-ada-002"
CONTEXT_LENGTH = 10000

# Completion functions
def complete(prompt):
    # query text-davinci-003
    res = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return res['choices'][0]['text'].strip()

def complete_gpt_3_5(prompt):
    res = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant that elaborates on the users query primarily using only the context they provide."},
            {"role": "user", "content": prompt}
        ]
    )
    return res['choices'][0]['message']['content']

def complete_gpt_4(prompt):
    res = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
            {"role": "system", "content": "You are a helpful assistant that elaborates on the users query using only the context they provide. If the context does not provide sufficient details for you to formulate an answer you politely let them know."},
            {"role": "user", "content": prompt}
        ]
    )
    return res['choices'][0]['message']['content']

# Main app
st.write("# Search through Ammar's digital-brain 🧠")
with st.sidebar:
    st.write("**[About Me](https://www.ammarh.io/)**")
    st.write("[Notes](https://notes.ammarh.io) 📝")
    st.write("[Chat](https://ammarh-ai-playground.herokuapp.com/) 💬")
    st.write("[Mail](mailto:self@ammarh.io) 📨")
    st.write("[Resume](https://notes.ammarh.io/resume) 📜")

    #   <li><a href="mailto:self@ammarh.io?subject = Second Brain Search">email</a></li>

form = st.form("search_form")
searchtext = form.text_input('Query', 'What is reinforcement learning?')
confidence = form.slider("Confidence", min_value=0.65, max_value=0.90, value=0.75)
generate_ans = form.checkbox('Summarize')
# Now add a submit button to the form:
submit = form.form_submit_button("Submit")

if submit:
    with st.spinner('Wait for it...'):
        start_time = time.time()
        session_variables = {}
        session_variables['searchtext'] = searchtext
        session_variables['confidence'] = confidence
        session_variables['generate_ans'] = generate_ans

        logging.error(f"session : {session_variables}")
        try:
            search_embedding = openai.Embedding.create(
            input=session_variables['searchtext'],
            engine=EMBED_MODEL
            )['data'][0]['embedding']
        except Exception as e:
            msg = f"OpenAI embedding call failed with exception - {e}"
            logging.error(msg)
            st.error(msg)
            st.stop()
        
        embed_time = time.time() - start_time

        try:
            # 'client' is a MilvusClient instance.
            res = MILVUS_CLIENT.search(
                collection_name="obsidian_second_brain",
                data=[search_embedding],
                limit=20,
                output_fields=["note", "file", "uuid"]
            )

        except:
            msg = "Milvus retrieval call failed"
            logging.error(msg)
            st.error(msg)
            st.stop()

        query_time = time.time() - embed_time

        results = []

        for match in res[0]:
            if match['distance'] < session_variables['confidence']:
                continue
            path_list = match['entity']['file'].split('/')
            file = path_list[-1] + ' :: ' + '/'.join(path_list[5:-1])
            link = (URL_PREFIX + '/'.join(path_list[6:])).replace(" ", "+")
            filtered_notes = [x for x in match['entity']['note'].split("\n") \
                                if x != "" and x[0] != "!"]
            context_str = " ".join(filtered_notes)
            results.append({'file': file, 
                            'notes': filtered_notes[:10], 
                            #'notes': match['metadata']['note'].split("\n"),
                            'score': match['distance'],
                            'link': link,
                            'context' : context_str
                            })
        
        # Use a set to track seen 'file' values
        seen = set()
        new_results = [d for d in results if d['file'] not in seen and not seen.add(d['file'])]

        results = sorted(new_results, key=lambda x: x['score'], reverse=True)
        results_time = time.time() - query_time

    st.write(f"About {len(results)} results in {time.time()-start_time:.02f} seconds ⏳")
    if session_variables['generate_ans']:
        expander = st.expander("####### **Summarized Answer:**")

    for result in results:
        st.write(f"\n##### [{result['file']}]({result['link']})")
        with st.expander(f"\nScore - {result['score']}"):
            for note in result['notes']:
                st.write(f"\n{re.sub(r'[#-]', '', note[:150])}\n")
    # st.markdown(create_markdown(results))

    generated_qa = ""
    generated_qa_time = -1
    if session_variables['generate_ans']:
        context_str = "\n---\n".join([x['context'] for x in results])[:CONTEXT_LENGTH]
        if re.search(r'\w', context_str):
            # build our prompt with the retrieved contexts included
            prompt_start = (
                #"Answer the query based on the context below.\n"+
                "Context:\n"
            )
            prompt_end = (
                f"\n---\nGiven this and only this context elaborate on the query: "+
                f"{session_variables['searchtext']}\nElaborate: "
            )
            prompt = prompt_start + context_str + prompt_end
            try:
                generated_qa = complete_gpt_3_5(prompt)
            except Exception as e:
                msg = f"OpenAI GPT-3.5 text completion failed. Exception - {e}"
                logging.error(msg)
                st.error(msg)
                st.stop()

            generated_qa_time = time.time() - results_time

            expander.write(generated_qa)
    logging.error(f"embed_time={embed_time}, query_time={query_time}, results_time={results_time}, generated_qa_time={generated_qa_time}")
