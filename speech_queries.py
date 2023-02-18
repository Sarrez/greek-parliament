import statistics
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
from indexer import preprocess_doc


def create_db():    
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    #mongo_client.drop_database("GreekParliamentProceedings")
    client = mongo_client["GreekParliamentProceedings"]
    index = client["InvertedIndex"]
    database = client["Database"]
    return index, database

index, database = create_db()

# Getting the TF value of a token, given a list of tokens that appear in a document.
# The document_tokens list is the result of the preprocess_docs() function which returns
# a list of each token of a document, preproccesed (remove stopwords, stemming etc.) in the
# order they appear on the document. The elements on the list (i.e., the tokens) are not unique,
# they are just a list representation of the document.
def get_frequency(query_token, document_tokens):
    # print("getting term frequency") 
    # print("query token ", query_token)
    # print(document_tokens)
    
    # Using the Counter class to count the frequencies of each token
    # and then getting the maximum frequency using the Counter.most_common() method
    # Also, using the Counter.get() method to get the frequency of the query_token 
    # in the document.
    frequencies = Counter(document_tokens)
    term_freq = frequencies.get(query_token)
    max_freq = frequencies.most_common(1)[0][1]
    
    # print("MAX_FREQ: ", max_freq, "TERM_FREQ: ", term_freq)
    
    # If the term_freq (i.e., the frequency of the query_token) is not set (is None)
    # then we return 0, since tf would be 0/max_freq which is 0.
    if(term_freq == None):
        return 0
    
    # compute the tf (term_frequency) as term_freq / max_freq. 
    # We normalize the frequency in order to avoid a bias towards larger documents.
    tf = term_freq / max_freq
        
    return tf

# This function is used to query the index, given a list of terms.
# For each term, the MongoDB index collection is queried, and for each term we
# 1) use the numdoc (number of documents in which the term apperas in) to find the IDF value 
#    for that term (log(N/n_t), where N is the total number of documents in the collection and 
#    n_t is the numdoc)
# 2) Iterate through each posting in the posting list of the term, and for each posting 
#    (i.e., a document that contains the term) calculate the TF value using the get_frequency() function
#    Each document is preproccessed the same way as when we created the Inverted Index, in order to remove stopwords
#    and stem the terms. The list of preproccessed terms is passed to the get_frequency() function. 
# We then update the weight of (or aggregator) of each document, by getting the documentWeights[posting] value and setting
# the new value as w = tf * idf + documentWeights[posting].
# documentWeights is a set with the document_ids as the key and the documents' weights (or aggregator value) as the values.
# We return the set with which we will find the top-k documents to display.
def query(terms, index):

    N = database.count_documents({}) 
    documentWeights = {} 
        
    for term in terms:
        query = {"_id" : term}    
        print("querying for term: ", term)
        # Querying the index for the given term
        for token in index.find(query):
            tokenlist = (token["list"])
            n_t = tokenlist["numdoc"]
            postings = tokenlist["postinglist"]
            # print("numdoc: ", n_t)
            # Calculating the IDF value.            
            idf = np.log((N/n_t))
            print("IDF:  ", idf)
            
            average_n_t = statistics.mean(list(postings.values()))
            print("AVERAGE Nt ", average_n_t)
            # Finding the TF value for each posting and updating the weight aggregators
            for posting in postings:
                # We check the documentWeights set to see if an entry for this specific posting exists.
                # If not, then we create a new entry for this posting with a value of 0.
                
                
                if(postings[posting]< 3):
                    continue
                if(documentWeights.get(posting) == None):
                    documentWeights[posting] = 0

                document = get_documents(posting, database)
                
                # Preprocessing the documents and getting a list of each token in the document
                with open('stopwords.txt', encoding='utf-8') as file:
                    stopwords = [line.rstrip() for line in file]
                document_words = preprocess_doc(document["speech"], stopwords)            
                
                # If an empty list is returned, we continue the loop.                
                if not document_words:
                    print("EMPTY LIST")
                    continue
                
                #Calculating the TF value and updating the weights aggregator for this posting.
                # tf = get_frequency(token["_id"], document_words)
                tf = np.log10(1 + postings[posting] )
                pw = documentWeights[posting]
                w = tf * idf + pw * postings[posting]
                documentWeights[posting] = w        
                # print(documentWeights[posting])
                
    return documentWeights

# Function used to retrieve documents from the document collection, given a docid
def get_documents(docid, database):
    
    document_query = {"_id" : docid}
    document = {}
    for x in database.find(document_query):
        speech = x
        document = speech       
    return document    

def get_top_k_documents(doc_aggregators):
    top_k = []
    for aggregator in doc_aggregators:
        # print(aggregator)
        top_k.append(aggregator)
    return top_k[0:50]

def main():
    
    search_string = "να ερθει ο προεδρος της βουλης"
    # search_string = "Το ΠΑΣΟΚ ειναι εδω"
    # search_string = "Μνημόνιο Λιτότητα"
    # # search_string = "ΦΕΚ"
    # search_string = "Παρακαλειται ο κυριος Βουλγαρακης να παραλαβει τον"
    # search_string = "του μονου προφητη"
    search_string = "Ελληνοτουρκικα"
    
    # search_string = "Πρυτανης Αριστοτελειο Πανεπιστημιο Θεσσαλονικης ΑΠΘ"
    # search_string = "μεταπολιτευση κυβερνησεις"
    
    with open('stopwords.txt', encoding='utf-8') as file:
                stopwords = [line.rstrip() for line in file]
    
    query_tokens = preprocess_doc(search_string, stopwords)
    print(query_tokens)
    index, database = create_db()
    start_time = time.time()
    doc_weights = query(query_tokens, index)
    print(len(doc_weights))
    print("Results shown in ", time.time()-start_time, " seconds.")
    # top_k = []
    # for p in doc_weights:
    #     top_k.append(p)

    # print(top_k[0:10])
    # top_k = top_k[0:10]
    # print(top_k, "\n\n\n\n\n\n\n\n\n\n")
    
    top_k = get_top_k_documents(doc_weights)
    print(len(top_k))
    documents = []
    for document in top_k:
        documents.append(get_documents(document, database))
    
    result = ""
    
    with open("query_results.txt", "w", encoding="utf-8") as f:
        for doc in documents:
            f.write("Query: "+  search_string+ "\n\n\n")
            print("\n", doc["_id"], " MP: ", doc["member_name"], " Sitting Date: ", doc["sitting_date"])
            print("Political Party: ", doc["political_party"])
            print(doc["speech"], "\n")
            
            result += "\n"
            result += doc["_id"] + " MP: " +  doc["member_name"] + "\nSitting Date: " + doc["sitting_date"]
            result += "\nPolitical Party: " + doc["political_party"] + "\n"
            result += doc["speech"] + "\n"
            
            f.write(result)
        f.close()
        
if __name__ == "__main__":
    main()