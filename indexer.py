from nltk.tokenize import word_tokenize
import pandas as pd
import time
import string 
import unicodedata as ud
from greek_stemmer import GreekStemmer
import pymongo
import re

"""Indexer Script

This script is used to set up the data used in this project.

It creates a MongoDB database with two collections:
1. Database: stores all data from a csv
2. InvertedIndex: stores inverted index

The script first stores all data into the Database collection. 
It then creates the inverted index and stores it in the InvertedIndex collection.
The algorithm to create the index is based on a merging technique, where data is read in chunks from the Database collection. 
The index is created in parts and merging happens when inserting the index in MongoDB.

The script can be imported as a module and contains the methods listed:

    * create_db - connects to Mongo, creates database and collections
    * tokenize - tokenizes a string
    * preprocess_doc - performs stemming, removes punctuation and stopwords
    * insert_db
    * create_index
    * insert_to_database
"""


def create_db():    
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    client = mongo_client["GreekParliamentProceedings"]
    index = client["InvertedIndex"]
    database = client["Database"]
    return index, database

def tokenize(row):
    return word_tokenize(row)

# add encoding="utf8" at line 339
import time
def preprocess_doc(doc: str, stopwords:list) -> list:
    doc = doc.lower()
    d = {ord('\N{COMBINING ACUTE ACCENT}'):None}
    doc = ud.normalize('NFD',doc).translate(d)
    stemmer = GreekStemmer()
    #remove all punctuation from
    doc = doc.translate(str.maketrans('','',string.punctuation))
    words = []
    if doc!="":
        words = [stemmer.stem(w.upper()).lower() for w in doc.split() if w not in stopwords]
    return words

def insert_db(path_to_csv:str):
    print("Inserting csv to MongoDB...")
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = mongo_client["GreekParliamentProceedings"]
    collection = database["Database"]
    if len(list(collection.find({"_id":"0"})))==0:
        dataframe = pd.read_csv(path_to_csv)
        counter = 0
        index = 0
        for i in range(len(dataframe)):
            row = dataframe.loc[i, :].values.flatten().tolist()
            collection.insert_one({"_id":str(index), "member_name":row[0],"sitting_date":row[1],
                                    "parliamentary_period":row[2],"parliamentary_session":row[3],
                                    "parliamentary_sitting":row[4],"political_party":row[5],
                                    "government":row[6],"member_region":row[7],
                                    "roles":row[8],
                                    "member_gender":row[9],
                                    "speech":row[10]}                  
                                    )
            index += 1
    else:
        print("Database collection already has entries")

def create_index(total_documents:int, chunksize:int, min_doc_length = 20):
    print("Creating Inverted Index...")
    chunk = []
    counter = 0
    start_time = time.time()
    #get inverted index
    index, database = create_db()
    ticks = [x for x in range(0,total_documents,chunksize)]
    ticks.append(total_documents)
    # load stopwords
    with open('stopwords.txt', encoding='utf-8') as file:
        stopwords = [line.rstrip() for line in file]
    for j in range(len(ticks)-1):
        tokens = {}
        chunk = list(database.find({ }, { "_id": 1, "speech": 1 })[ticks[j]:ticks[j+1]])
        print("Length of chunk: ", len(chunk))
        size_distribution = []
        #chunk = ["This is a sentance","This is another one"]
        #for each speech
        start_time = time.time()
        for i, row in enumerate(chunk):
            words_in_row = preprocess_doc(row["speech"].lower(), stopwords)
            '''
            
            TOKENIZED ROWS IN ROW
            We now need to remove stopwords, perform stemming and remove punctuation
            Afterwards, we can add them to the index. This will be done for each row of the dataframe chunk.
            When the chunk is finished, we will create a json file with the index of this chunk and we'll do the process again for the next chunk.
            
            '''
            if(len(words_in_row)>min_doc_length):
                size_distribution.append(len(words_in_row))
                
                for word in words_in_row:
                    
                    if word in tokens.keys():
                        #term already in index
                    
                        if i not in tokens[word]["postinglist"].keys():
                            #term in other document
                            #n = tokens[word]["numdoc"]

                            tokens[word]["postinglist"][row["_id"]] = words_in_row.count(word)
                            tokens[word]["numdoc"] = len(tokens[word]["postinglist"])

                        else:
                            #term in same document
                            n = tokens[word]["numdoc"]
                            tokens[word]["numdoc"] = n+1
                            pass
                            
                    else:
                        #term not in index
                        #replaced str(i) with row["_id"]
                        tokens[word]={"numdoc":1, "postinglist":{row["_id"] : words_in_row.count(word)}}
        end_time = time.time()
        print("Chunk finished after: ", end_time - start_time)
                
        #insert chunk of tokens to a mongo collection named index
        start_time = time.time()
        insert_to_database(tokens, index)
        end_time = time.time()
        print("Chunk into MongoDB: ", end_time - start_time)
        counter +=1
        print("CHUNK", counter, " FINISHED")
    
    return index, database, tokens, size_distribution

        
def insert_to_database(tokens, collection):    
    """ Inserts a part of the inverted index into MongoDB """
    for token in tokens:
        #check if token already exists in MongoDB
        exists = collection.find_one( { "_id": token } )
        if(not exists):
            #if token doesn't exist in MongoDB, insert it to Mongo
            token_to_insert = {"_id":token, "list":{"numdoc":tokens[token]["numdoc"], "postinglist":tokens[token]["postinglist"]}} 
            x = collection.insert_one(token_to_insert)
        else:
            #if token exists in MongoDB, get object from Mongo and update values
            query = { "_id": token }
            x=collection.find_one(query)
            #sum numdoc fields
            numdoc = x['list']['numdoc'] + tokens[token]["numdoc"]
            #merge posting lists
            x['list']['postinglist'].update(tokens[token]["postinglist"])
            token_to_update = {"list":{"numdoc":numdoc, "postinglist":x['list']['postinglist']}}
            collection.update_one({"_id":token}, {"$set":token_to_update})

def post_process_index(index, database):
    #REMOVE TERMS WITH NUMDOC==1
    threshold = list(index.find({"list.numdoc":{"$lt":2}}, { "_id": 1, "list.numdoc": 0 }))
    print(len(threshold))
    for entry in threshold:
        index.delete_one({'_id':entry['_id']})
    # FIND WHICH DOCUMENTS ARE IN INDEX
    res = list(index.find({ }, { "_id": 0, "list.postinglist": 1 }))
    total = set()
    for i in range(len(res)):
        total_documents = set((res[i]['list']['postinglist'].keys()))
        total.update(total_documents)
    # REMOVE DOCUMENTS NOT IN INDEX
    for doc_id in total:
        database.delete_one({'_id':doc_id})
        
#create index (must import database to mongo first!!!!!!! )
import argparse
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'csv_path',
        type=str,
        help="Path to csv file"
    )
    parser.add_argument(
        'total_documents',
        type=int,
        help="Number of documents to read"
    )
    parser.add_argument(
        'chunksize',
        type=int,
        help="The number of chunks"
    )
    parser.add_argument(
        'min_doc_length',
        type=int,
        help="The minimum length of a speech in order to be part of the index"
    )
    args = parser.parse_args()
    index, database = create_db()
    insert_db(args.csv_path)
    create_index(args.total_documents, args.chunksize, args.min_doc_length)
    post_process_index(index, database)

if __name__ == "__main__":
    main()