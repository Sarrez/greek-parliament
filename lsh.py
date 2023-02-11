class LSH:
    def __init__(self, documents:list):
        self.documents = documents
    
    def get_k_shingles(self, vector: list, k: int)->set:
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
    def get_vocabulary(self, all_shingles:set)->set:
        vocab = set()
        for i in range(len(all_shingles)):
            vocab.update(all_shingles[i])
            
        return vocab