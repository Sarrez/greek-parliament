import math
import numpy as np
from indexer import create_index, preprocess_doc
import pandas as pd

def idf(num_of_docs, num_of_docs_with_term):
    return float(math.log(num_of_docs/num_of_docs_with_term)) #log base?

def tf_p(term_frequency, max_frequency, doc_length, average_doc_length, delta, b = 0.75):
    tf = float(term_frequency/max_frequency)
    s = tf / (1 - b + b * (doc_length/average_doc_length))
    a = 1 + np.log(s + delta)
    tf_p = float(1 + np.log(a))
    return tf_p

def tf(ftd: float) -> float:
    return 1 + math.log(ftd)

def top_k(query: str, index: dict, k:int) -> list:
    acc = {}
    query = preprocess_doc(query)
    for term in query:
        print(term)
        try:
            data = index[term]
            nt = data['numdoc']
            term_idf = idf(num_of_docs=3000, num_of_docs_with_term=nt)
            for document in data["postinglist"].keys():
                #αν δεν υπάρχει ο συσσωρευτής τότε δημιουργείται
                if(document not in acc.keys()):
                    acc[document] = 0
                ftd = data["postinglist"][document]
                term_frequency = tf(ftd) 
                tfidf = term_idf * term_frequency
                acc[document] = acc[document] + tfidf
        except KeyError:
            print(f"Ο όρος δεν υπάρχει")
            
    sort_by_score = sorted(acc.items(), key=lambda x:x[1], reverse=True)
    top = sort_by_score[:k]
    return top