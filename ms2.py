# we must remove duplicates for extra credit

import json
from collections import defaultdict
from math import log10, sqrt


# Load the inverted index from the JSON file
def load_inverted_index():
    with open("inverted_index.json", "r") as f:
        inverted_index = json.load(f)
    return inverted_index


# Calculate the tf-idf score for term in document
def calculate_tf_idf(tf, df, N):
    return (1 + log10(tf)) * log10(N / df)


# Search for documents that contain all the query terms using AND
def search_documents(query, inverted_index):
    query_terms = query.lower().split()
    result = defaultdict(float)

    for term in query_terms:
        if term in inverted_index:
            docs = inverted_index[term]
            for doc in docs:
                doc_id = doc["doc_id"]
                tf = doc["tf-dif"]
                df = len(docs)
                N = len(inverted_index)
                tf_idf = calculate_tf_idf(tf, df, N)
                result[doc_id] += tf_idf

    sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    return sorted_result



if __name__ == "__main__":
    print("Please give a second to finish indexing...\n")
    inverted_index = load_inverted_index()
    print("Instructions:\n- Type 'Q' to exit.\n- Type in seach for results.\n")
    while True:
        query = input("Search Here: ")
        if(query == 'Q'):
            break
        else:
            results = search_documents(query, inverted_index)
            print(f"Search results for query '{query}':")
            if not results:
                print("N/A")
            else:
                for result in results[0:5]:
                    print(f"Document: {result[0]}, Score: {result[1]}")
                print()

