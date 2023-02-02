from nltk.tokenize import word_tokenize
import pandas as pd
import time
import string 
import unicodedata as ud
from greek_stemmer import GreekStemmer
import pymongo
import re


def create_db():    
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    #mongo_client.drop_database("GreekParliamentProceedings")
    client = mongo_client["GreekParliamentProceedings"]
    index = client["InvertedIndex"]
    database = client["Database"]
    return index, database

def query(token, index):
    docids = []
    query = {"_id" : token}
    print("querying")
    for x in index.find(query):
        xlist = (x["list"])
        postings = xlist["postinglist"]
        print(postings)
        print(postings["0"])
        for posting in postings:
            print(posting, postings[posting])
            docids.append(posting)
        # print(postings["0"])
        # for posting in postings:
        #     print(posting)
            
        #     print(xlist[str(posting)])
    return docids

def get_documents(docids, database):
    speeches = []
    
    for docid in docids:
        speech_query = {"_id" : docid}
        for x in database.find(speech_query):
            
            speeches.append(x)
            
            # print(type(x))
            # print(len(speeches))
            # if (len(speeches) != 0):
            #     print("made it")
            #     speeches["_id"].append(x["_id"])
            #     speeches["member_name"].append(x["member_name"])
            #     speeches["sitting_date"].append(x["sitting_date"])
            #     speeches["parliamentary_period"].append(x["parliamentary_period"])
            #     speeches["parliamentary_session"].append(x["parliamentary_session"])
            #     speeches["parliamentary_sitting"].append(x["parliamentary_sitting"])
            #     speeches["political_party"].append(x["political_party"])
            #     speeches["government"].append(x["government"])
            #     speeches["member_region"].append(x["member_region"])
            #     speeches["roles"].append(x["roles"])
            #     speeches["member_gender"].append(x["member_gender"])
            #     speeches["speech"].append(x["speech"])
            # else:
            #     print("made it 2")
            #     speeches["_id"] = (x["_id"])
            #     speeches["member_name"] = (x["member_name"])
            #     speeches["sitting_date"] = (x["sitting_date"])
            #     speeches["parliamentary_period"] = (x["parliamentary_period"])
            #     speeches["parliamentary_session"] = (x["parliamentary_session"])
            #     speeches["parliamentary_sitting"] = (x["parliamentary_sitting"])
            #     speeches["political_party"] = (x["political_party"])
            #     speeches["government"] = (x["government"])
            #     speeches["member_region"] = (x["member_region"])
            #     speeches["roles"] = (x["roles"])
            #     speeches["member_gender"] = (x["member_gender"])
            #     speeches["speech"] = (x["speech"])
            
            # print(speeches["_id"])
        
    return speeches    

def main():
    index, database = create_db()
    docids = query("παρακαλειτα", index)
    
    
    documents = get_documents(docids, database)
    for document in documents:
        print("DOCUMENT \n", "Member Name: ", document["member_name"], "\n Political Party", document["political_party"], "\n Speech: \n", document["speech"], "\n")


if __name__ == "__main__":
    main()