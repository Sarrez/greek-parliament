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



mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_client.drop_database("GreekParliamentProceedings")
inverted_index = mongo_client["GreekParliamentProceedings"]
collection = inverted_index["InvertedIndex"]

dataframe = pd.read_csv('Greek_Parliament_Proceedings_1989_2020.csv', chunksize=1000)

def tokenize(row):
    return word_tokenize(row)

# add encoding="utf8" at line 339
stemmer = GreekStemmer()


# load stopwords
with open('stopwords.txt', encoding='utf-8') as file:
    stopwords = [line.rstrip() for line in file]
# print(stopwords)



def preprocess_doc(doc: str) -> list:
    d = {ord('\N{COMBINING ACUTE ACCENT}'):None}
    if doc!="":
        words = [stemmer.stem(ud.normalize('NFD',w).upper().translate(d)).lower() for w in word_tokenize(doc) if w not in stopwords and w not in string.punctuation]
    return words
        
# doc = "!Τρεις. τίγρεις ]\. και, τρία><τιγράκια'"
# ws = preprocess_doc(doc)
# print(ws)



chunk = []
tokens = {}
counter = 0
start_time = time.time()
for data in dataframe:
    # print(data)
    chunk = (data["speech"].values.tolist())
    
    for i, row in enumerate(chunk):
        words_in_row = preprocess_doc(row.lower())
        # words_in_row = word_tokenize(row)
        # print("ROW: ", i, "\n")
        # print(words_in_row)
        # print("\n")
        
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
                    n = tokens[word]["numdoc"]
                    tokens.append({word:{"numdoc":n+1, "postinglist":{str(i) : words_in_row.count(word)}}})
                    
                else:
                    #term in same document
                    # tokens[word]["postinglist"][str(i)] += 1
                    pass
                    
            else:
                #term not in index
                tokens.update({word:{"numdoc":1, "postinglist":{str(i) : words_in_row.count(word)}}})
            
            # # print("Term: ", word, "document: ", i)
            # if word in tokens.keys():  
            #     tok = tokens[word][1]
            #     # tok[len(tokens[word][1])-1][0]
            #     if i != tok[len(tokens[word][1])-1][0]:
                    
                    
            #         tokens[word][1].append([i, words_in_row.count(word)])
            #     tokens[word][0] = tokens[word][0] + 1
            # else:
            #     tokens.update({word:[1,[[i,words_in_row.count(word)]]]})
            
        
    # for token in tokens:
    # #     print("TOKEN: ", token)
    # #     # print("DOCUMENTS: ", tokens[token][0], "POSTING LIST: ", tokens[token][1])
    # #     for doc in tokens[token][1]:
    # #         print(doc)
    
    # # print(tokens['εκθέσεων'])
    # # print("The term appears in ", tokens["εκθέσεων"][0], " documents. \nPostings Lists: ", tokens["εκθέσεων"][1])
    # # for doc in tokens["εκθέσεων"][1]:
    # #     print("DOCUMENT: ", doc[0])
    # #     print("SPEECH: ", chunk1[doc[0]])
        # for doc in tokens[token]:
        #     print(doc)
        # print(token, tokens[token],"\n")
    #     unique_words = set(words_in_row)
    #     for word in unique_words:
    #         # print(word)
    #         if word in tokens.keys():
    #             tokens[word][1].append([i, words_in_row.count(word)])
    #             tokens[word][0] = tokens[word][0] + 1
    #         else:
    #             tokens.update({word:[1,[[i,words_in_row.count(word)]]]})
    # print(len(chunk1))
    # break
    counter +=1
    print("CHUNK", counter, " FINISHED")
    print("Number of Tokens: ", len(tokens))
    
    print(type(tokens))
    
    
    
    for token in tokens:
        # print("HERE", tokens[token])
        # # token_to_insert = {token : tokens[token]}
        # token_to_insert = {token : {"numdoc":tokens[token][0], "postingslist":{tokens[token][1][0][0] : tokens[token][1][0][1]}}}
        token_to_insert = {token:{"numdoc":tokens[token]["numdoc"], "postinglist":tokens[token]["postinglist"]}} 

        
        
        x = collection.insert_one(token_to_insert)
        break
    
    
    if(counter == 3):
        break
    
print(tokens["αρχιεπισκοπ"])
    
j = 0
for token in tokens:
    print("TOKEN: ", token)
    print("DOCUMENTS: ", tokens[token]["numdoc"], "POSTING LIST: ", tokens[token]["postinglist"])
    if(j == 100):
        break
    j += 1
# print(tokens)
# print(tokens['παρακαλειτα'])
# print(tokens)
delta_time = time.time() - start_time
print("Time for ", len(tokens), "tokens: ", delta_time)
