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




import numpy as np

csv.field_size_limit(291950)

dataframe = pd.read_csv('Greek_Parliament_Proceedings_1989_2020.csv', chunksize=100)


# df = pd.DataFrame(dataframe)
# print(df.loc[102])

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
        words_in_row = preprocess_doc(row)
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
            # print("Term: ", word, "document: ", i)
            if word in tokens.keys():
                tokens[word][1].append([i, words_in_row.count(word)])
                tokens[word][0] = tokens[word][0] + 1
            else:
                tokens.update({word:[1,[[i,words_in_row.count(word)]]]})
            
        
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
    print(len(tokens))
    if(counter == 5):
        break
j = 0
for token in tokens:
    print("TOKEN: ", token)
    # print("DOCUMENTS: ", tokens[token][0], "POSTING LIST: ", tokens[token][1])
    if(j == 100):
        break
    j += 1
# print(tokens)
# print(tokens)
delta_time = time.time() - start_time
jsontokens = json.dumps(tokens)
with open('json_tokens.json', 'w', encoding='utf8') as json_file:
    json.dump(tokens, json_file, ensure_ascii=False)