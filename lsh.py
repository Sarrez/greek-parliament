import random
from random import randint
import itertools
from collections import Counter
import hashlib

#ToDo: DOCUMENTATION
class LSH:
    """
    Performs the LSH technique for a list of documents using MinHash. 

    ...

    Attributes
    ----------
    documents : list
        a list containing all documents to perform LSH on. 
        each documents must be represented as a list of words.

    Methods
    -------
    jaccard_similarity(signature1, signature1)
        returns the jaccard similarity of two lists
    """
    def __init__(self, documents:list):
        self.documents = documents
        self.num_sets = (len(documents))
    
    def __get_k_shingles(self, vector: list, k: int)->set:
        shingles = []
        if(k>0):
            word = ' '.join(vector)
            for i in range(len(word) - k+1):
                shingles.append(word[i:i+k])
        else:
            for word in vector:
                shingles.append(word)
        return set(shingles)

    #all_shingles is a list of sets
    def __get_vocabulary(self, all_shingles:set)->set:
        vocab = set()
        for i in range(len(all_shingles)):
            vocab.update(all_shingles[i])
            
        return vocab

    def __get_sparse_matrix(self, vocab:set, all_shingles:set):
        #CREATE SPARSE MATRIX MxN, WHERE M = LEN(keywords) and N = LEN(vocab)
        matrix = []
        for k in range(self.num_sets):
            matrix.append([0 for i in range(len(vocab))])
        for i, shingle in enumerate(all_shingles):
            for s in shingle:
                position = list(vocab).index(s)
                matrix[i][position] = 1    
        return matrix


    def __create_signature_matrix(self, vocab:set, num_hashes:int, matrix:list):
        hash_ = [i for i in range(0, len(vocab))]
        hashes = []
        for i in range(num_hashes):
            random.shuffle(hash_)
            hashes.append(list(hash_))
        #INITIALISE SIGNATURE MATRIX
        signature_matrix = []
        for i in range(self.num_sets):
            signature_matrix.append([len(hashes)+10 for i in range(len(hashes))])
        #CREATE SIGNATURES
        for i in range(len(matrix[0])):
            for j in range(len(matrix)):
                if(matrix[j][i]==1):
                    # there are k=128 hashes, each hash has i=408 items
                    # CRITICAL
                    for k, hash_ in enumerate(hashes):
                        if(hash_[i]<signature_matrix[j][k]):
                            signature_matrix[j][k] = hash_[i]

        return signature_matrix

    def jaccard_similarity(self, signature1: list, signature2: list):
        sim = 0
        sig1 = set(signature1)
        sig2 = set(signature2)
        if(len(sig1.union(sig2))!=0):
            sim = len(sig1.intersection(sig2)) / len(sig1.union(sig2))

        return sim
    
    def __split_into_bands(self, signature_matrix:list, b:int, columns:int):
        steps = [i for i in range(0,len(signature_matrix[1]), columns)]
        #print(steps)
        steps.append(len(signature_matrix[0]))
        #splits = [signature_matrix[steps[i]:steps[i+1]] for i in range(len(steps)-1)]
        splits = [[signature[steps[i]:steps[i+1]] for signature in signature_matrix[:]] for i in range(len(steps)-1)]
        #for i in range(len(steps)-1):
            #print(steps[i], steps[i+1])
        return splits
    
    def __get_band_buckets(self, band, hash_funct):
        buckets = {}
        for doc_id in range(0,len(band)):
            value = hash_funct.get_hash_value( band[doc_id] )
            if value not in buckets:
                buckets[value] = [doc_id]
            else:
                buckets[value].append(doc_id)
        return buckets
    
    def MinHashLSH(self, num_hashes: int, num_bands:int, num_columns:int):
        # STEP 1: CREATE SHINGLES FOR SET OF INPUT DOCUMENTS AND CREATE VOCAB OF DISTINCT SHINGLES
        all_shingles = []
        for list_ in self.documents:
            all_shingles.append(self.get_k_shingles(list_,0))
        vocab = self.get_vocabulary(all_shingles)

        #STEP 2: CREATE SPARSE MATRIX
        sparse_matrix = self.get_sparse_matrix(vocab, all_shingles)

        #STEP 3: CREATE SIGNATURES
        signature_matrix = self.create_signature_matrix(vocab, num_hashes, sparse_matrix)

        #STEP 4: SPLIT SIGNATURE MATRIX TO B SUBVECTORS WITH C COLUMNS EACH (MATRIX IS TRANSPOSED)
        bands = self.split_into_bands(signature_matrix, num_bands, num_columns)

        #STEP 5: CREATE ONE BUCKET FOR EACH BAND

        hashFunction = hashFamily(randint(0,10000000000))
        buckets = []
        for band in bands:
            buckets.append(self.get_band_buckets(band, hashFunction))
        
        #STEP 6: EXTRACT CANDIDATE PAIRS FROM ALL BUCKETS
        candidates_pairs = []


        for bucket in buckets:
            for key in bucket.keys():
                if(len(bucket[key])>1):
                    candidates_pairs.extend(list((itertools.combinations(bucket[key], 2))))

        distinct_pairs = Counter(frozenset(s) for s in candidates_pairs)
        candidates_pairs = []
        for key in distinct_pairs.keys():
            candidates_pairs.append(list(key))
        return candidates_pairs
    
#SOURCE: https://www.codemotion.com/magazine/backend/fast-document-similarity-in-python-minhashlsh/
# the family of hash functions, in this case, is the same function (sha1) applied with a different salt.
class hashFamily:
    def __init__(self, i):
        self.resultSize = 8 # how many bytes we want back
        self.maxLen = 20 # how long can our salt be (in decimal)
        self.salt = str(i).zfill(self.maxLen)[-self.maxLen:]

    def get_hash_value(self, el_to_hash):
        return int(hashlib.sha1(str(el_to_hash).encode('utf-8') + self.salt.encode('utf-8')).hexdigest()[-self.resultSize:], 16)

# NOTE: we use sha1 to avoid installing and importing an external library, sacrificing performances. No crypto-hash is required for this use case.