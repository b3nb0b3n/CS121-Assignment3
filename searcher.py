import csv
import json
from collections import defaultdict
from math import log10, sqrt
from nltk.stem import PorterStemmer
import re
import time
from flask import Flask, render_template, request


csv.field_size_limit(100000000)

app = Flask(__name__)

stemmer = PorterStemmer()

NUMBER_OF_ROWS = 0


# Load the row map from the JSON file
def load_row_map(local_path):
    global NUMBER_OF_ROWS
    with open(local_path, "r") as f:
        row_map = json.load(f)
    NUMBER_OF_ROWS = len(row_map)
    return row_map


# Open the CSV file and search for the given term
def search_csv(term, csv_reader, row_map):
    term_row = row_map.get(term)
    if term_row is None:
        print("Term not found.")
        return []

    for i, row in enumerate(csv_reader):
        if i == term_row:
            term_data = eval(row[1])  # Convert string representation to list of dictionaries
            return term_data

    print("Term not found.")
    return []


def open_csv(csv_path):
    with open(csv_path, "r") as f:
        csv_reader = csv.reader(f)
        return csv_reader


# Calculate the tf-idf score for term in document
def calculate_tf_idf(tf, df, N):
    return (1 + log10(tf)) * log10(N / df)


# Cosine similarity between two vectors
def cosine_similarity(tf1, tf2):
    dot_product = tf1 * tf2
    magnitude1 = abs(tf1)
    magnitude2 = abs(tf2)

    return dot_product / (magnitude1 * magnitude2)


#The get_urls function takes in a dictionary tf_scores containing URLs as keys and their corresponding similarity scores as values. 
# It first checks if the tf_scores dictionary is empty, and if so, it returns an empty list urls. 
# Otherwise, it sorts the dictionary items based on the similarity scores in descending order and appends each URL-similarity pair to the urls list. 
# Finally, it returns the list of URLs with their corresponding similarity scores, sorted in descending order.
def get_urls(tf_scores):
    urls = []
    if not tf_scores:
        return urls

    sorted_results = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)
    for url, similarity in sorted_results:
        urls.append((url, similarity))

    return urls


def retrieve_stem_terms(query_term):
    # Create an instance of the Porter Stemmer
    stemmer = PorterStemmer()

    # Find all alphanumeric tokens in the query term
    tokens = re.findall(r"\b[a-zA-Z0-9]{3,}\b", query_term.lower())

    # Stem each token using the Porter Stemmer
    stemmed_terms = [stemmer.stem(token) for token in tokens]

    return stemmed_terms

# Search for documents using tf-idf
def search_documents(terms, csv_reader, row_map):
    global NUMBER_OF_ROWS
    N = NUMBER_OF_ROWS
    tf_idf_scores = defaultdict(float)
    for term in terms:
        urls = search_csv(term, csv_reader, row_map)
        df = len(urls)  # Assuming only one occurrence per term in each document
        for url in urls:
            # Calculate tf-idf score for each document
            tf = url['tf']
            tf_idf = calculate_tf_idf(tf, df, N)
            tf_idf_scores[url['url']] += tf_idf
    return dict(tf_idf_scores)  # Convert defaultdict to dictionary


# Get URLs based on cosine similarity
@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


#The code snippet represents a Flask route handler for a search functionality. It receives a POST request 
# with a search term, retrieves stemmed terms from the input, loads an inverted index and token-row mapping, searches for 
# documents matching the terms using TF-IDF scores, retrieves URLs of the matching documents, measures the search duration, 
# and returns a rendered HTML template ('results.html') with the URLs and search duration displayed.
@app.route("/search", methods=['POST'])
def search():
    term = request.form['search_term']
    terms = retrieve_stem_terms(term)
    csv_path = "inverted_index.csv"
    json_path = "token_row_map.json"
    row_map = load_row_map(json_path)
    with open(csv_path, "r") as f:
        csv.field_size_limit(100000000)  # Increase field size limit
        csv_reader = csv.reader(f)
        start_time = time.time()
        tf_idf_scores = search_documents(terms, csv_reader, row_map)
        query_vector = list(tf_idf_scores.values())[0]  # Use the first vector as the query vector
        urls = get_urls(tf_idf_scores)
        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)
        return render_template('results.html', urls=urls, duration=duration_ms)


#This code block checks if the script is being run directly (as the main module) and if so, it starts the 
# Flask application by calling the run() method on the app object. The application will run on the localhost 
# with the specified port number (5000 in this case) and the debug mode is set to False, meaning it won't display 
# detailed error messages in the browser.
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)