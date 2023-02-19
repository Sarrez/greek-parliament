from nltk import ngrams
from nltk.tokenize import word_tokenize
import unicodedata as ud
import pymongo
import re
import networkx as nx
from greek_stemmer.stemmer import GreekStemmer
import spacy
import math
import string

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
client = mongo_client["GreekParliamentProceedings"]
index = client["InvertedIndex"]
database = client["Database"]

class KeywordExtractor:
    """
    Extracts keywords from a single document. 

    ...

    Methods
    -------
    document_keywords(speech, stopwords, domain_specific_stopwords, window, language)
        returns the top keywords for a given speech
    """
    def __init__(self):
        return
    
    def get_words(self, sentence:spacy, stemmer, domain_specific_stopwords):
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

    def get_candidate_words(self, text, stopwords, domain_specific_stopwords, language):
        stemmer = GreekStemmer()
        nlp = language
        nlp.Defaults.stop_words |= set(stopwords)
        text = text.lower()
        sentences = nlp(text)
        processed_sentences = []
        for sentence in sentences.sents:
            words_to_consider = self.get_words(sentence, stemmer, domain_specific_stopwords)
            if(len(words_to_consider)>0):
                processed_sentences.append(words_to_consider)
        return processed_sentences

    def make_graph(self, word_list: list, window: int):
        """
        Creates a graph of words for a document.
        Arguments:
            word_list: the document as a list of words. 
                       assumes that words are in the same order as in the original document
            window: 
        Returns:
            A networkx Graph.
        """
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

        return g

    def extract_phrases(self, speech, keywords):
        """
        Extracts keyphrases from a document given a list of keywords. 
        If a keyword is part of a phrases it is removed as a single keyword.
        Arguments:
            keywords: list of keywords
        Returns:
            A list of keywords and keyphrases.
        """
        tokenized = speech.split()
        bigrams = ngrams(tokenized, 2)
        for gram in bigrams:
            if(gram[0] in keywords and gram[1] in keywords and gram[0]!=gram[1]):
                keywords.append(gram[0]+" "+gram[1])
                keywords.remove(gram[0])
                keywords.remove(gram[1])
        return keywords
    
    def stem_top_keywords(self, keywords:list):
        """
        Stems keywords or phrases.
        Arguments:
            keywords: list of single words or phrases
        Returns:
            A list of stemmed words or phrases
        """
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
    
    def document_keywords(self, speech, stopwords, domain_specific_stopwords, window, language = spacy.load('el_core_news_sm')):
        """
        Extracts keywords from a speech
        Arguments:
            speech: string
            stopwords: txt file 
            domain_specific_stopwords: txt file
            window: int
            language: spacy language module, greek by default
        Returns:
            A list of stemmed keywords
        """
        sentences = self.get_candidate_words(speech, stopwords, domain_specific_stopwords, language)
        graph = self.make_graph(sentences, window=window)
        scores = nx.pagerank(graph)
        scores = dict(sorted(scores.items(), key=lambda item: -item[1]))
        all_words = list(scores.keys())
        if(len(graph.nodes)>0):
            keywords = all_words[:int(math.log2(len(graph.nodes))+8)]
        else:
            keywords = []
        keywords = self.extract_phrases(speech, keywords)
        top_keywords = self.stem_top_keywords(keywords)
        return top_keywords