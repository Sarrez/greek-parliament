from nltk import ngrams
from nltk.tokenize import word_tokenize
import unicodedata as ud
import pymongo
import re
import networkx as nx
from greek_stemmer import GreekStemmer
import spacy
import math

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
client = mongo_client["GreekParliamentProceedings"]
index = client["InvertedIndex"]
database = client["Database"]


def get_words(sentence:spacy, stemmer, domain_specific_stopwords):
    words = []
    regex = "^[0-9][0-9][0-9].*"
    for token in sentence:
        #remove words with specified format
        if(re.search(regex, token.text)==None):
            #only keep NOUNs and ADJECTIVEs that are not stowords or punctuation
            if(token.pos_ in ('NOUN','ADJ') and token.is_stop==False and token.is_punct==False):
                d = {ord('\N{COMBINING ACUTE ACCENT}'):None}
                if(stemmer.stem(ud.normalize('NFD',token.text.upper()).translate(d)).lower() not in domain_specific_stopwords):
                    words.append(token.text)
    return words

def get_candidate_words(text, stopwords, domain_specific_stopwords, language):
    stemmer = GreekStemmer()
    nlp = language
    nlp.Defaults.stop_words |= set(stopwords)
    text = text.lower()
    sentences = nlp(text)
    processed_sentences = []
    for sentence in sentences.sents:
        words_to_consider = get_words(sentence, stemmer, domain_specific_stopwords)
        if(len(words_to_consider)>0):
            processed_sentences.append(words_to_consider)
    return processed_sentences

def extract_pairs(word_list, window):
    pairs = []
    #print(word_list)
    g = nx.Graph()
    for a_list in word_list:
        if(len(a_list)>window):
            candidate_lists = [a_list[k:window+k] for k in range(0, len(a_list)) if window+k<=len(a_list)]
        else:
            candidate_lists = [a_list]
        for candidate_list in candidate_lists:
            #print(candidate_list)
            for i in range(0, len(candidate_list)-1):
                for j in range(i+1, len(candidate_list)):
                    pairs.append((candidate_list[i], candidate_list[j]))
                    #avoid self-loops
                    if(candidate_list[i] == candidate_list[j]):
                        pass
                    #if edge does not exist create it
                    elif((candidate_list[i], candidate_list[j]) not in g.edges):
                        g.add_edge(candidate_list[i], candidate_list[j])

    return pairs, g

def document_keywords(speech, stopwords, domain_specific_stopwords, window, language):
    sentences = get_candidate_words(speech, stopwords, domain_specific_stopwords, language)
    pairs, graph = extract_pairs(sentences, window=window)
    scores = nx.pagerank(graph)
    scores = dict(sorted(scores.items(), key=lambda item: -item[1]))
    all_words = list(scores.keys())
    if(len(graph.nodes)>0):
        keywords = all_words[:int(math.log2(len(graph.nodes))+8)]
    else:
        keywords = []
    return scores, keywords

import string
def extract_phrases(speech, keywords):
    tokenized = speech.split()
    bigrams = ngrams(tokenized, 2)
    for gram in bigrams:
        if(gram[0] in keywords and gram[1] in keywords and gram[0]!=gram[1]):
            keywords.append(gram[0]+" "+gram[1])
            keywords.remove(gram[0])
            keywords.remove(gram[1])
    return keywords
def stem_top_keywords(keywords:dict):
    #dict(keyword_frequency[:20])
    stemmer = GreekStemmer()
    d = {ord('\N{COMBINING ACUTE ACCENT}'):None}
    final = set()
    for token in keywords:
        #split to tokens
        words = word_tokenize(token)
        stemmed = ""
        for word in words:
            #remove punctuation
            word = word.translate(str.maketrans('', '', string.punctuation))
            if(word!=''):
                #remove word if it is duplicate or already exists in keyphrase
                stemmed_word = stemmer.stem(ud.normalize('NFD',word.upper()).translate(d)).lower()
                stemmed = stemmed + stemmed_word
                if len(words)>1:
                    stemmed = stemmed + " "
                    if(stemmed_word in final or stemmed_word in string.punctuation and stemmed_word in final):
                        final.remove(stemmed_word)            

            final.add(stemmed)
    return final
    
def get_member_keywords(member_name:string, stopwords, domain_specific_stopwords, collection)->list:
    #get keywords for member from MongoDB
    pipeline = [{'$match' : {'member_name':member_name}},
                {'$group':{'_id':'$keywords'}}]
    keywords_by_speech = database.aggregate(pipeline)
    total_keywords = []
    language = spacy.load('el_core_news_sm')
    print(f"Member {member_name}")
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

def keywords_per_member():
    member_names = database.distinct("member_name")
    # RUN FOR ALL MEMBERS
    keywords_by_member = {}
    with open('../stopwords.txt', encoding='utf-8') as file:
        stopwords = [line.rstrip() for line in file]
        stopwords = set(stopwords)
    with open('../domain-specific-stopwords.txt', encoding='utf-8') as file:
        domain_specific_stopwords = [line.rstrip() for line in file]
    for i in range(1, len(member_names)):
        top_keywords = get_member_keywords(member_names[i], stopwords, domain_specific_stopwords, database)
        keywords_by_member[member_names[i]] = top_keywords
    return keywords_by_member