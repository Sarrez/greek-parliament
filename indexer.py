import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import csv
import pandas as pd
import json
import time
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import string 
import unicodedata as ud
from greek_stemmer import GreekStemmer
import pymongo
import numpy as np
import re




def create_db():    
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    mongo_client.drop_database("GreekParliamentProceedings")
    inverted_index = mongo_client["GreekParliamentProceedings"]
    collection = inverted_index["InvertedIndex"]
    return collection


def tokenize(row):
    return word_tokenize(row)

# add encoding="utf8" at line 339



# print(stopwords)



def preprocess_doc(doc: str) -> list:
    stemmer = GreekStemmer()
    d = {ord('\N{COMBINING ACUTE ACCENT}'):None}
    # load stopwords
    with open('stopwords.txt', encoding='utf-8') as file:
        stopwords = [line.rstrip() for line in file]
    #doc = doc.lower()
    if doc!="":
        words = [stemmer.stem(ud.normalize('NFD',w).upper().translate(d)).lower() for w in filter(None, re.split("[,~`; _'.\-!?:]+",doc)) if w not in stopwords and w not in string.punctuation]
    return words
        
# doc = "!Τρεις. τίγρεις ]\. και, τρία><τιγράκια'"
# ws = preprocess_doc(doc)
# print(ws)


def create_index(dataframe):
    chunk = []
    counter = 0
    start_time = time.time()
    
    collection = create_db()

    for data in dataframe:
        tokens = {}
        chunk = (data["speech"].values.tolist())
        print("Length of chunk: ", len(chunk))
        #chunk = ["This is a sentance","This is another one"]
        for i, row in enumerate(chunk):
            words_in_row = preprocess_doc(row.lower())
            '''
            
            TOKENIZED ROWS IN ROW
            We now need to remove stopwords, perform stemming and remove punctuation
            Afterwards, we can add them to the index. This will be done for each row of the dataframe chunk.
            When the chunk is finished, we will create a json file with the index of this chunk and we'll do the process again for the next chunk.
            
            '''
            
            for word in words_in_row:
                
                if word in tokens.keys():
                    #term already in index
                    if i not in tokens[word]["postinglist"].keys():
                        #term in other document
                        #n = tokens[word]["numdoc"]
                        tokens[word]["postinglist"][str(i)] = words_in_row.count(word)
                        tokens[word]["numdoc"] = len(tokens[word]["postinglist"])

                    else:
                        #term in same document
                        n = tokens[word]["numdoc"]
                        tokens[word]["numdoc"] = n+1
                        pass
                        
                else:
                    #term not in index
                    tokens[word]={"numdoc":1, "postinglist":{str(i) : words_in_row.count(word)}}
                
                
        
        insert_to_database(tokens, collection)
        counter +=1
        print("CHUNK", counter, " FINISHED")
        print("Number of Tokens: ", len(tokens))
        
        print(type(tokens))
        if(counter == 1):
            break
    
    
    return collection

        
def insert_to_database(tokens, collection):    

    for token in tokens:
        token_to_insert = {"_id":token, "list":{"numdoc":tokens[token]["numdoc"], "postinglist":tokens[token]["postinglist"]}} 
        x = collection.insert_one(token_to_insert)
    #    break
            
# print(tokens)
# print(tokens['παρακαλειτα'])
# print(tokens)
#delta_time = time.time() - start_time
#print("Time for ", len(tokens), "tokens: ", delta_time)
#dataframe = pd.read_csv('Greek_Parliament_Proceedings_1989_2020.csv', chunksize=1000)

#tokens = create_index(dataframe)

#j = 0
#for token in tokens.keys():
    #print("TOKEN: ", token)
    #print("DOCUMENTS: ", tokens[token]["numdoc"])
    #print(tokens[token])
    #print(len(tokens[token]["postinglist"]))
    #if(j == 100):
    #    break
    #j += 1
