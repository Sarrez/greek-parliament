import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
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
# from indexer import preprocess_doc


def create_db():    
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    #mongo_client.drop_database("GreekParliamentProceedings")
    client = mongo_client["GreekParliamentProceedings"]
    index = client["InvertedIndex"]
    database = client["Database"]
    return index, database



def get_documents(docid, database):
    # print(docid)
    document = []
    for did in docid:

        document_query = {"_id" : str(did)}
        for x in database.find(document_query):
            speech = x
            document.append(speech["speech"])     
    return document    


def batch_loader(database, batch=10000):
    len = database.count_documents({})
    for index in range(0, len, batch):
        yield get_documents(list(range(index, index+batch)), database)

def vectorize(document):
    vectorizer = TfidfVectorizer()
    
    # document = np.array(document)

    # print(document.shape)
    # print(document)

    document = vectorizer.fit_transform(document)
    # print(documents)
    
    print(document.shape)
    # print(documents)
    
    return document


def latent_semantic_analysis_dimensionality_reduction(database):
    svd = TruncatedSVD(500)
    
    
    a = np.empty((0,500))
    
    for documents in batch_loader(database):

        # documents = get_documents(["122", "1555", "1", "11", "13", "17", "16", "14", "12"], database)
        # print(documents)
        # documents.append(vectorize(documents))
        
        
        # svd.fit(documents)
        
        # a = svd.transform(documents)
        
        print(len(documents))
        vectorized_documents = vectorize(documents)
        # for document in documents:
        #     # print(document)
        #     vectorized_documents.append(vectorize(document))
        next_rows = svd.fit_transform(vectorized_documents)
        # a = svd.transform(vectorized_documents)
        print(next_rows.shape)
        a = np.append(a, next_rows, axis=0)
        
        
    # print(a)
    print(a)
    print(a.shape)

    return a

def main():
    index, database = create_db()
    
    
    # documents = []
    # for docid in docidlist:
    #     documents.append(get_documents(docid, database))
        # print(get_documents(docid, database))
    
    reduced_matrix = latent_semantic_analysis_dimensionality_reduction(database)
    
    print(reduced_matrix.shape)
    
    with open('reduced_dimension_matrix.npy', 'wb') as f:
        np.save(f, reduced_matrix)
        
    with open('reduced_dimension_matrix.npy', 'rb') as f:
        a = np.load(f, allow_pickle=True)
        
    print(a.shape)
    
    
if __name__ == "__main__":
    main()