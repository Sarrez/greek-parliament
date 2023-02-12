from lsh import LSH

class Top_k_Pairs:
    """
    This class finds the top-k pairs with the highest similarity from a list of entities.
    'k' is a parameter given as input from the user. Each entity is represented as a vector of features.

    ...

    Methods
    -------
    get_pairs(k, feature_vectors, threshold=0.7, num_hashes=256, num_bands=32, num_columns=4)
        returns top-k similar pairs given a list of feature vectors
    """
    def __init__(self):
        return
    
    def get_pairs(self, k, feature_vectors:list, threshold=0.7, num_hashes=256, num_bands=32, num_columns=4):
        #consider keywords as a list of lists. consider each sublist as a feature vector of a parliament member
        lsh = LSH(feature_vectors)
        #find candidate pairs using LSH
        candidates_pairs = lsh.MinHashLSH(num_hashes=num_hashes, num_bands=num_bands, num_columns=num_columns)
        #find most similar pairs 
        accepted = {}
        for pair in candidates_pairs:
            sim = lsh.jaccard_similarity(feature_vectors[pair[0]], feature_vectors[pair[1]])
            if(sim>threshold):
                if(sim not in accepted.keys()):
                    accepted[sim] = [pair]
                else:
                    accepted[sim].append(pair)
        top = []
        keys = sorted(accepted.keys())
        return accepted
    
    def get_similar_features(vector1, vector2):
        return vector1.union(vector2)
    
    
            
                
            
            
            
        
         

    
    