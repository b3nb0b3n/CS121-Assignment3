import os
import csv
from bs4 import BeautifulSoup
import re
import hashlib
import json
from collections import defaultdict
from nltk.stem import PorterStemmer


""""Global Paths"""
json_file = os.path.join(os.getcwd(), 'DEV')
output_directory = os.path.join(os.getcwd(), 'json_outputs')

"""Stemmer Module being called"""
stemmer = PorterStemmer()

"""Global Values"""
row_number = 1
indexed_doc_count = 0


"""
Builds an inverted index from a collection of JSON files, storing the mapping of tokens to their 
corresponding documents. It iterates over the files, extracts tokens, and adds them to the inverted index
along with the document information. The resulting inverted index is returned as the output.
"""
def build_inverted_index():
    global indexed_doc_count
    inverted_index = {}
    token_row_map = {}
    hashed_urls = set()
    LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "other"]

    # Create output directory if it doesn't exist
    create_output_dir()

    for cur, subdir, files in os.walk(json_file):
        for file in files:
            print("FILE:\n", file)
            indexed_doc_count += 1
            if file.endswith('.json'):
                cur_file_path = os.path.join(cur, file)
                url, stemmed_tokens = tokenizer(cur_file_path)
                print("URL:\n", url)
                hashed_url = hashlib.md5(url.encode()).hexdigest()
                if hashed_url not in hashed_urls:
                    add_inverted_index(inverted_index, stemmed_tokens, token_row_map, url)
                    hashed_urls.add(hashed_url)
        # Write token data to separate JSON files
        dump_all_jsons(LETTERS ,inverted_index)
        write_report(indexed_doc_count)
    dump_token_row_map(token_row_map)
    write_csv(LETTERS, token_row_map)
    return inverted_index


"""
Creates the output directory if it does not already exist. This function checks if the specified output 
directory exists and creates it if it does not. This ensures that the output directory is available for storing the generated jsons.
"""
def create_output_dir():
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)


"""
Tokenizes the content of a file using BeautifulSoup and regular expressions. This function extracts the 
text content from a JSON file, performs tokenization to extract alphanumeric tokens of length 3 or more, 
applies stemming to the tokens, and returns the URL and stemmed tokens.
"""
def tokenizer(cur_file_path):
    with open(cur_file_path, 'r') as f:
        data = json.load(f)
        soup = BeautifulSoup(data['content'], 'html.parser')
        text = soup.get_text()
    tokens = re.findall(r"\b[a-zA-Z0-9]{3,}\b", text.lower())
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    url = data['url']
    return url, stemmed_tokens


"""
Adds entries to the inverted index and token-row mapping based on the provided stemmed tokens, URL, and 
the global row number. This function ensures that each token is associated with its corresponding URL and
term frequency (tf) in the inverted index. If the token already exists in the token-row map, it appends 
the URL and tf to its entry in the inverted index. If the token is not present in the token-row map, it creates 
a new entry in both the inverted index and token-row map.
"""
def add_inverted_index(inverted_index, stemmed_tokens, token_row_map, url):
    global row_number
    no_duplicate_token = set(stemmed_tokens)
    for token in no_duplicate_token:
        # if token in inverted_index:
        if token in token_row_map:
            if token in inverted_index:
                inverted_index[token].append({'url': url, "tf": stemmed_tokens.count(token)})
            else:
                inverted_index[token] = [{'url': url, "tf": stemmed_tokens.count(token)}]
        else:
            inverted_index[token] = [{'url': url, "tf": stemmed_tokens.count(token)}]
            token_row_map[token] = row_number
            row_number += 1


"""
This function dumps the data from the inverted index into multiple JSON files based on the starting letter of 
the tokens. It iterates over the provided letters and collects tokens starting with each letter. Then, it merges the
token data from the inverted index into the corresponding JSON file. Finally, it clears the collected token data 
from the inverted index.
"""
def dump_all_jsons(letters, inverted_dic):
    for letter in letters:
        hold_tokens = []
        json_file_path = os.path.join(output_directory, f'{letter}.json')
        json_data = defaultdict(list)
        for token in inverted_dic.keys():
            if token[0] == letter:
                hold_tokens.append(token)
            elif token[0] not in 'abcdefghijklmnopqrstuvwxyz' and letter == 'other':
                hold_tokens.append(token)
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                json_data = json.load(f)
        for token in hold_tokens:
            if token not in json_data.keys():
                json_data[token] = []
            try:
                json_data[token].extend(inverted_dic[token])
            except KeyError:
                json_data[token] = inverted_dic[token]
        with open(json_file_path, 'w') as f:
            json.dump(json_data, f)
        for used_token in hold_tokens:
            del inverted_dic[used_token]
    inverted_dic.clear()

"""

This function writes the inverted index data to a CSV file. It iterates over the tokens in the token-row map and 
retrieves the corresponding data from the JSON files. It then writes the token, URL and TF data, and row number to 
the CSV file.
"""
def write_csv(letters, token_row_map):
    with open('inverted_index.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Token', 'URL and TF', 'Row Number'])
        alphabet = 'abcdefghijklmnopqrstuvwxyz'

        json_data = {}  # Dictionary to store loaded JSON data
        
        for token, row in sorted(token_row_map.items(), key=lambda x: x[1]):
            first_letter = token[0]
            if first_letter in alphabet:
                json_file_path = os.path.join(output_directory, f'{first_letter}.json')
            else:
                json_file_path = os.path.join(output_directory, f'other.json')

            if first_letter not in alphabet and 'other' not in json_data:
                with open(json_file_path, 'r') as f:
                    json_data['other'] = json.load(f)
            elif first_letter not in json_data:
                with open(json_file_path, 'r') as f:
                    json_data[first_letter] = json.load(f)

            if first_letter in json_data and token in json_data[first_letter]:
                writer.writerow([token, json_data[first_letter][token], row])
            elif first_letter not in alphabet and token in json_data['other']:
                writer.writerow([token, json_data['other'][token], row])

"""
This function dumps the token-row map dictionary into a JSON file.
"""
def dump_token_row_map(token_row_map):
    with open('token_row_map.json', 'w') as f:
        json.dump(token_row_map, f)
        

"""
For user to keep track the number of urls that has been indexed.
"""
def write_report(doc_count):
    with open('report.txt', 'w') as f:
        f.write("Inverted Index\n\n")
        f.write(f'Number of Indexed Documents: {doc_count}\n')



if __name__ == "__main__":
    print("START")
    inverted = build_inverted_index()
    print("END")
