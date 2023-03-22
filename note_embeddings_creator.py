import openai
import pinecone
import re, os, hashlib, fnmatch
from tqdm.auto import tqdm
from time import sleep

# global variables
PINECONE_INDEX_NAME = "obsidian-second-brain"
OPENAI_EMBED_MODEL = "text-embedding-ada-002"
openai.api_key = "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"
PINECONE_API_KEY="ab65a920-5194-49fe-a00a-a46841ed398d"
PINECONE_ENVIRONMENT="us-east1-gcp"

def search_image_files(filename, directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            if f == filename:
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.png', '.jpg', '.jpeg', '.gif'):
                    return os.path.join(dirpath, f)
    return None

def get_all_attachments_in_text(note_string):
    regex_pattern = r"\[\[.*?\]\]|!\[\[.*?\]\]"
    strip_char = r"\[|\]|!"
    matches = [re.sub(strip_char,'',match) for match in re.findall(regex_pattern,  note_string) ]
    return matches

def remove_urls(text):
    # Regular expression pattern for matching URLs
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    # Remove URLs from the text
    without_urls = re.sub(url_pattern, '', text)
    return without_urls

def remove_obsidian_links(text):
    clean = re.compile('\[\[.*?\]\]|!\[\[.*?\]\]')
    return re.sub(clean, '', text)

def parse_markdown_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    _, filename = os.path.split(file_path)
    # find the first header to use data from there on
    for i, string in enumerate(lines):
        if string.startswith("#"):
            lines = lines[i:]
            break
    # insert the filename as first element
    lines.insert(0, filename + "\n")
    return lines

def split_list(note_lines_list, word_threshold):
    sublists = []
    sublist = []
    subtotal = 0
    for sentence in note_lines_list:
        sublist.append(sentence)
        word_count = len(sentence.split())
        if subtotal + word_count > word_threshold:
            sublists.append(sublist)
            sublist = []
            subtotal = 0
        subtotal += word_count
    if sublist:
        sublists.append(sublist)
    return sublists


def get_files_to_index(rootdir):
    searchstr = 'publish: true'
    files_to_index = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if fnmatch.fnmatch(file, '*.md') == True:
                filepath = os.path.join(subdir, file)
                if fnmatch.fnmatch(filepath,'*/.trash/*') == False:
                    with open(filepath, 'r') as f:
                        if searchstr in f.read():
                            files_to_index.append(filepath)
    return files_to_index

def initialize_pinecone_index(index_name):
    # initialize connection to pinecone (get API key at app.pinecone.io)
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT
    )

    # check if index already exists (it shouldn't if this is first time)
    if index_name not in pinecone.list_indexes():
        print("creating new pinecone index")
        # if does not exist, create index
        pinecone.create_index(
            index_name,
            dimension=1536,
            metric='cosine',
            metadata_config={'indexed': ['file']}
        )
    # connect to index
    index = pinecone.Index(index_name)
    return index 

def create_note_snippets(files_list):
    VECTOR_WORD_LIMIT = 800
    notes_snippets = []
    for file in files_list:
        note_lines = parse_markdown_file(file)        
        note_text_split = split_list(note_lines, VECTOR_WORD_LIMIT)
        for i,note_text_split_snippet in enumerate(note_text_split):
            note_snippet = "".join(note_text_split_snippet)
            notes_snippets.append({
                'uuid': hashlib.sha256((file + "_^_" + str(i)).encode()).hexdigest(),
                'file': file,
                'section': i,
                'note': note_snippet
            })

    print(f"Adding {len(notes_snippets)} chunks from {len(files_list)} files")
    return notes_snippets

def upload_to_pinecone(notes_snippets, pinecone_index):
    batch_size = 100  # how many embeddings we create and insert at once

    for i in tqdm(range(0, len(notes_snippets), batch_size)):
        #print(f"i - {i}")
        # find end of batch
        i_end = min(len(notes_snippets), i+batch_size)
        meta_batch = notes_snippets[i:i_end]
        # get ids
        ids_batch = [x['uuid'] for x in meta_batch]
        # get notes to encode
        notes = [x['note'] for x in meta_batch]
        # create embeddings (try-except added to avoid RateLimitError)
        try:
            res = openai.Embedding.create(input=notes, engine=OPENAI_EMBED_MODEL)
        except Exception as e:
            # handle the exception by printing a message
            print(f"An exception occurred: {repr(e)}")
            done = False
            while not done:
                #sleep(5)
                try:
                    res = openai.Embedding.create(input=notes, engine=OPENAI_EMBED_MODEL)
                    done = True
                except Exception as e:
                    print(f"Still getting an exception: {e} ... Passing")
                    print(notes)
                    pass
        embeds = [record['embedding'] for record in res['data']]
        # cleanup metadata
        meta_batch = [{
            'uuid': x['uuid'],
            'file': x['file'],
            'note': x['note']
        } for x in meta_batch]

        to_upsert = list(zip(ids_batch, embeds, meta_batch))
        # upsert to Pinecone
        pinecone_index.upsert(vectors=to_upsert)


if __name__ == '__main__':
    pinecone_index = initialize_pinecone_index(index_name=PINECONE_INDEX_NAME)
    files_list = get_files_to_index(rootdir="/Users/ammarh/Documents/second-brain/")
    notes_snippets = create_note_snippets(files_list=files_list)
    upload_to_pinecone(notes_snippets, pinecone_index)
