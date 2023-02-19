import spacy
import math
import string
from keyword_extractor import KeywordExtractor
"""
    This module implements methods for extracting keywords from various groups of the speeches database.
    There are methods for extracting keywords:
        - per speech
        - per parliament member
        - per political party
        - per parliament member per governement
        - per political party per government
"""
################### FOR DOCUMENTS ###################

def extract_document_keywords(speech_indexes:list, database):
    ex = KeywordExtractor()
    #get a set of keywords for each speech given the index of the speech in the MongoDB database
    with open('../stopwords.txt', encoding='utf-8') as file:
        stopwords = [line.rstrip() for line in file]
        stopwords = set(stopwords)
    with open('../domain-specific-stopwords.txt', encoding='utf-8') as file:
        domain_specific_stopwords = [line.rstrip() for line in file]
    language = spacy.load('el_core_news_sm')
    for i in range(0, len(speech_indexes)):
        print("Doc:", speech_indexes[i])
        speech = list(database.find({"_id": str(speech_indexes[i]) }, { "_id": 0, "speech": 1 }))
        keywords = ex.document_keywords(speech[0]['speech'], stopwords, domain_specific_stopwords, window = 3, language = language)
        database.update_one({"_id":str(speech_indexes[i])},{'$set':{'keywords':list(keywords)}})
        
################### FOR MEMBERS ###################

def get_member_keywords(member_name:string, database, government=None)->list:
    #get keywords for a single parliament member 
    if(government==None):
        pipeline = [{'$match' : {'member_name':member_name}},
                    {'$group':{'_id':'$keywords'}}]
        keywords_by_speech = database.aggregate(pipeline)
    else:
        pipeline = [{'$match' : {'member_name':member_name, 'government':government}},
                    {'$group':{'_id':'$keywords'}}]    
        keywords_by_speech = database.aggregate(pipeline)
        
    total_keywords = []
    #language = spacy.load('el_core_news_sm')
    counter = 0
    for keyword_list in keywords_by_speech:
        total_keywords.extend(keyword_list['_id'])
        #print('Doc: ', counter)
        counter+=len(keyword_list['_id'])
    keyword_frequency = {}
    for keyword in set(total_keywords):
        keyword_frequency[keyword] = total_keywords.count(keyword)
        
    keyword_frequency = sorted(keyword_frequency.items(), key=lambda d: d[1], reverse=True)
    if(counter>0):
        number_of_keywords = int(math.log(counter))
    else:
        number_of_keywords = 0
    top_keywords = dict(keyword_frequency[:number_of_keywords])
    return top_keywords

def keywords_per_member(members:list, database):
    #get a list of keywords for each parliament member from a list of parliament member
    keywords_by_member = {}
    for i in range(1, len(members)):
        top_keywords = get_member_keywords(members[i], database)
        keywords_by_member[members[i]] = top_keywords
    return keywords_by_member

def keywords_per_member_per_government(members:list, database):
    governments_per_member = {}
    #get governments for each member
    for member in members:
        print(f"Member {member}")
        governments_per_member[member] = {}
        pipeline = [{'$match' : {'member_name':member}}, {'$group':{'_id':'$government'}}]
        governments = database.aggregate(pipeline)
        for government in governments:
            keywords = get_member_keywords(member, database, government=government['_id'])
            governments_per_member[member][government['_id']] = keywords
    return governments_per_member

################### FOR POLITICAL PARTIES ###################

def keywords_per_party(parties:list, database):
    #get a set of keywords for each party from a list of parties
    keywords_by_party = {}
    for i in range(1, len(parties)):
        top_keywords = get_party_keywords(parties[i], database)
        keywords_by_party[parties[i]] = top_keywords
    return keywords_by_party

def get_party_keywords(party:string, database, government=None)->list:
    #get keywords for one party
    if(government==None):
        pipeline = [{'$match' : {'political_party':party}},
                    {'$group':{'_id':'$keywords'}}]
        keywords_by_party = database.aggregate(pipeline)
    else:
        pipeline = [{'$match' : {'political_party':party, 'government':government}},
                    {'$group':{'_id':'$keywords'}}]    
        keywords_by_party = database.aggregate(pipeline)

    total_keywords = []
    counter = 0
    for keyword_list in keywords_by_party:
        total_keywords.extend(keyword_list['_id'])
        counter+=len(keyword_list['_id'])
    keyword_frequency = {}
    for keyword in set(total_keywords):
        keyword_frequency[keyword] = total_keywords.count(keyword)
        
    keyword_frequency = sorted(keyword_frequency.items(), key=lambda d: d[1], reverse=True)
    if(counter>0):
        number_of_keywords = int(math.log(counter))
    else:
        number_of_keywords = 0
    top_keywords = dict(keyword_frequency[:number_of_keywords+5])
    return top_keywords

def keywords_per_party_per_government(parties:list, database):
    governments_per_party = {}
    for party in parties:
        print(f"Party {party}")
        governments_per_party[party] = {}
        pipeline = [{'$match' : {'political_party':party}}, {'$group':{'_id':'$government'}}]
        governments = database.aggregate(pipeline)
        for government in governments:
            keywords = get_party_keywords(party, database, government=government['_id'])
            governments_per_party[party][government['_id']] = keywords
    return governments_per_party