import os 
import json 
from bs4 import BeautifulSoup
import re 
from collections import defaultdict
import hashlib
from nltk.stem import PorterStemmer

#Creates a file path by joining the current directory "os.getcwd()" and 'DEV' the name of the file of JSONs we're working with
json_file = os.path.join(os.getcwd(), 'DEV')

stemmer = PorterStemmer()

#Initialize variables to keep track of the number of files and size of index for report purposes 
file_counter = 0
index_size = 0

#Method used to build the inverted index
def build_inverted_index():

    #establish variables as global variables within the given scope of the method 
    global file_counter, index_size

    #initialize an ivnverted index variable that is a qdefaultdict with lists as values 
    inverted_index = defaultdict(list)
    urls_dict = {}
    doc_ids_dict = {}

    for cur, subdir, files in os.walk(json_file):
        for file in files:
            print(file)
            file_counter += 1
            if file.endswith('.json'):
                try:
                    cur_file_path = os.path.join(cur, file)
                    with open(cur_file_path,'r') as f:
                        data = json.load(f)
                        soup = BeautifulSoup(data['content'], 'html.parser')
                        text = soup.get_text()
                    tokens = re.findall(r"\b[a-zA-Z0-9]{3,}\b", text.lower())
                    undup_tokens = set(tokens)
                    stemmed_tokens = [stemmer.stem(token) for token in undup_tokens]

                    url = data['url']
                    # Hash the URL to obtain the document ID
                    doc_id = hashlib.md5(url.encode()).hexdigest()
                    # Store the JSON file path in the doc_ids_dict with the document ID as the key
                    doc_ids_dict[doc_id] = cur_file_path
                    # Store the URL in the urls_dict with the document ID as the key
                    urls_dict[doc_id] = url
                    for token in stemmed_tokens:
                        inverted_index[token].append({'doc_id': doc_id, "tf": tokens.count(token)})
                except:
                    print("BAD FILE")
                write_report(inverted_index)
        write_json(inverted_index)

    return inverted_index


def write_json(inverted_dic):
    with open('inverted_index.json', 'w') as f:
            json.dump(inverted_dic, f)


def write_report(inverted_dic):
    global file_counter

    file_path = os.path.join(os.getcwd(), 'inverted_index.json')
    index_size_bytes = os.path.getsize(file_path)
    index_size = (index_size_bytes/1024)
    with open('report.txt', 'w') as f:
        f.write("Inverted Index\n\n")
        f.write(f'Number of Indexed Documents: {file_counter}\n')
        f.write(f'Number of Unique Tokens: {len(inverted_dic.keys())}\n')
        f.write(f'Total Size (kB): {index_size}\n')


if __name__ == "main":
    print("hello")
    inverted = build_inverted_index()
    # write_report(inverted)`