import streamlit as st
import time
import openai, pinecone
import time, re
import logging, os
from PIL import Image

im = Image.open("static/image/favicon-32.png")
st.set_page_config(
    page_title="Hello",
    page_icon=im,
    layout="wide",
)


# setup Pinecone and OpenAI
URL_PREFIX = "https://notes.ammarh.io/"
# initialize connection to pinecone (get API key at app.pinecone.io)
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="us-east1-gcp"
)
# connect to index
PINECONE_INDEX = pinecone.Index('obsidian-second-brain')

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
        except:
            msg = "OpenAI embedding call failed"
            logging.error(msg)
            st.error(msg)
            st.stop()
        
        embed_time = time.time() - start_time

        try:
            # retrieve from Pinecone
            res = PINECONE_INDEX.query(search_embedding, top_k=20, include_metadata=True)
        except:
            msg = "Pinecone retrieval call failed"
            logging.error(msg)
            st.error(msg)
            st.stop()

        query_time = time.time() - embed_time


        results = []
        for match in res['matches']:
            if match['score'] < session_variables['confidence']:
                continue
            path_list = match['metadata']['file'].split('/')
            file = path_list[-1] + ' :: ' + '/'.join(path_list[5:-1])
            link = (URL_PREFIX + '/'.join(path_list[6:])).replace(" ", "+")
            filtered_notes = [x for x in match['metadata']['note'].split("\n") \
                                if x != "" and x[0] != "!"]
            context_str = " ".join(filtered_notes)
            results.append({'file': file, 
                            'notes': filtered_notes[:10], 
                            #'notes': match['metadata']['note'].split("\n"),
                            'score': match['score'],
                            'link': link,
                            'context' : context_str
                            })
            
        results = sorted(results, key=lambda x: x['score'], reverse=True)
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
