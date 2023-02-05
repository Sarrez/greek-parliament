from nltk.tokenize import word_tokenize
import pandas as pd
import time
import string 
import unicodedata as ud
from greek_stemmer import GreekStemmer
import pymongo
import re
import numpy as np
from collections import Counter
from statistics import mode


def create_db():    
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    #mongo_client.drop_database("GreekParliamentProceedings")
    client = mongo_client["GreekParliamentProceedings"]
    index = client["InvertedIndex"]
    database = client["Database"]
    return index, database

index, database = create_db()


def get_frequency(query_token, document_tokens):
    print("getting term frequency") 
    # print(document_tokens)
    # print(document_tokens)
    # print(type(document_tokens))
    frequencies = Counter(document_tokens)
    # print("FREQUENCIES : ", frequencies)
    # print(query_token)
    term_freq = frequencies.get(query_token)
    # print("TF: ", term_freq)
    
    max_freq = frequencies.most_common(1)[0][1]
    print("MAX_FREQ: ", max_freq, "TERM_FREQ: ", term_freq)
    if(term_freq == None):
        return 0
    tf = term_freq / max_freq
    
    
    return tf
    # max_freq = Counter(document_tokens).most_common()[0][1]
    # term_freq = Counter(document_tokens).most_common().count(query_token)
    # print("Max Frequency", max_freq, "term freq: ", term_freq)


    # print(type(document_tokens))
    
    return 0

from indexer import preprocess_doc
def query(terms, index):
    N = database.count_documents({}) 
    docids = set()
    documentWeights = {} 
    
    
    for term in terms:
        print(term)
        query = {"_id" : term}    
        print("querying for term: ", term)
        for token in index.find(query):
            tokenlist = (token["list"])
            n_t = tokenlist["numdoc"]
            postings = tokenlist["postinglist"]
            # print(postings)
            print("numdoc: ", n_t)
            
            idf = np.log((N/n_t))
            # print(N, n_t, N/n_t)
            print("IDF: ", idf)
            print(postings) 
            for posting in postings:
                if(documentWeights.get(posting) == None):
                    documentWeights[posting] = 0

                print("posting", posting)
                # term_frequency = get_frequency(postings[posting], posting)
                document = get_documents(posting, database)
                print("DOCUMENT", document)
                # print(document[0]["speech"])
                # print(posting, postings[posting])
                with open('stopwords.txt', encoding='utf-8') as file:
                    stopwords = [line.rstrip() for line in file]
                document_words = preprocess_doc(document["speech"], stopwords)            
                
                
                # print(document_words)
                if not document_words:
                    print("EMPTY LIST")
                    continue
                
                tf = get_frequency(token["_id"], document_words)
                print(tf)            
                pw = documentWeights[posting]
                w = tf * idf + pw
                documentWeights[posting] = w        
                # print("W(",token["_id"], posting, ") = ", tf * idf)
                print(documentWeights[posting])
                # break
                # print(token["_id"])
                # tf = get_frequency(token["_id"], document_words)
                # for document_token in document_words:
                    # print(posting, document_token)
                    
    # print(documentWeights)
    # for p in documentWeights:
    #     print(p)
    return documentWeights
    # for term in terms:
        
    
    #     query = {"_id" : term}
    #     print("querying for token: ", term)
    
    #     print("QUERY: ", query)
    
    
    #     for token in index.find(query):
    #         tokenlist = (token["list"])
    #         n_t = tokenlist["numdoc"]
    #         postings = tokenlist["postinglist"]
    #         # print(postings)
    #         # print(postings["0"])
            
    #         print(term)
            
    #         idf = np.log((N/n_t))
    #         print(N, n_t, N/n_t)
    #         print("IDF: ", idf)
            
    #         for posting in postings:
                
    #             # term_frequency = get_frequency(postings[posting], posting)
    #             document = get_documents(posting, database)
    #             # print(document[0]["speech"])
    #             # print(posting, postings[posting])
    #             with open('stopwords.txt', encoding='utf-8') as file:
    #                 stopwords = [line.rstrip() for line in file]
    #             document_words = preprocess_doc(document[0]["speech"], stopwords)            
                
    #             print(token["_id"])
    #             tf = get_frequency(token["_id"], document_words)
    #             # for document_token in document_words:
    #                 # print(posting, document_token)
                    
    #             docids.add(posting)
                # docids.append(posting)
        # print(postings["0"])
        # for posting in postings:
        #     print(posting)
            
        #     print(xlist[str(posting)])
    # print(docids)

def get_documents(docid, database):
    
    
    document_query = {"_id" : docid}
    print(docid)
    document = {}
    for x in database.find(document_query):
        speech = x
        document = speech       
    return document    

def main():
    
    search_string = "να ερθει ο προεδρος της βουλης"
    
    with open('stopwords.txt', encoding='utf-8') as file:
                stopwords = [line.rstrip() for line in file]
    
    query_tokens = preprocess_doc(search_string, stopwords)
    print(query_tokens)
    index, database = create_db()
    query_input = "παρακαλειτα"
    doc_weights = query(query_tokens, index)
    top_k = []
    for p in doc_weights:
        top_k.append(p)

    # for document in documents:
    #     print("DOCUMENT \n", "Member Name: ", document["member_name"], "\n Political Party", document["political_party"], "\n Speech: \n", document["speech"], "\n")
    print(top_k[0:10])
    top_k = top_k[0:10]
    print(top_k, "\n\n\n\n\n\n\n\n\n\n")
    
    documents = []
    for tk in top_k:
        documents.append(get_documents(tk, database))
    
    for doc in documents:
        print(doc["_id"])
        print(doc["speech"])
    
if __name__ == "__main__":
    main()