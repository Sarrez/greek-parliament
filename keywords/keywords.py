import spacy
import math
import string

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
    language = spacy.load('el_core_news_sm')
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
def keywords_per_member(members, database):
    #get a list of keywords for each parliament member from a list of parliament member
    keywords_by_member = {}
    for i in range(1, len(members)):
        top_keywords = get_member_keywords(members[i], database)
        keywords_by_member[members[i]] = top_keywords
    return keywords_by_member

def document_keywords(speech_indexes: list, database):
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
        scores, keywords = document_keywords(speech[0]['speech'], stopwords, domain_specific_stopwords, window = 3, language = language)
        database.update_one({"_id":str(speech_indexes[i])},{'$set':{'keywords':list(keywords)}})
        
def get_party_keywords(party, database)->list:
    #get keywords for one party
    pipeline = [{'$match' : {'political_party':party}},
                {'$group':{'_id':'$keywords'}}]
    keywords_by_party = database.aggregate(pipeline)
    total_keywords = []
    print(f"Party {party}")
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
      
def keywords_per_party(parties, database):
    #get a set of keywords for each party from a list of parties
    keywords_by_party = {}
    for i in range(1, len(parties)):
        top_keywords = get_party_keywords(parties[i], database)
        keywords_by_party[parties[i]] = top_keywords
    return keywords_by_party