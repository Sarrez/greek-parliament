import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
import pymongo
import numpy as np

def create_db():    
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
    #mongo_client.drop_database("GreekParliamentProceedings")
    client = mongo_client["GreekParliamentProceedings"]
    index = client["InvertedIndex"]
    database = client["Database"]
    return index, database

# function to get documents from the database
def get_documents(docids, database):
    document = []
    for document_id in docids:
        document_query = {"_id" : str(document_id)}
        for x in database.find(document_query):
            speech = x
            document.append(speech["speech"])     
    return document    

# function that yields batches for the Singular Value Decomposition (or LSA)
def batch_loader(database, batch=10000):
    len = database.count_documents({})
    for index in range(0, len, batch):
        yield get_documents(list(range(index, index+batch)), database)

# function that uses the TfidfVectorizer in order to create a term-document matrix for a batch of documents
# returns a document-term matrix.
def vectorize(documents):
    vectorizer = TfidfVectorizer()
    documents = vectorizer.fit_transform(documents)
    print(documents.shape)
    
    return documents

# function that performs Latent Semantic Analysis and dimensionality reduction to the dataset of documents.
# The TruncatedSVD class from sklearn.decomposition library is used, to perform the Singular Value Decomposition
# For every batch of documents, we use the vectorize function to create a document-term matrix and then use the 
# svd.fit_transform() method of the TruncatedSVD class for this batch's matrix, getting the reduced dimensions matrix. 
# Each batch's reduced dimensions matrix is then appended to the end of the reduced_dimension_matrix, untill all the batches
# are processed and we have the final reduced_dimensions_matrix with a shape of 1280918 x 500. 
def latent_semantic_analysis_dimensionality_reduction(database):
    
    number_of_dimensions = 500
    
    svd = TruncatedSVD(number_of_dimensions)
  
    reduced_dimension_matrix = np.empty((0,number_of_dimensions))
    
    for documents in batch_loader(database):      
        print(len(documents))
        vectorized_documents = vectorize(documents)
        next_rows = svd.fit_transform(vectorized_documents)
        print(next_rows.shape)
        reduced_dimension_matrix = np.append(reduced_dimension_matrix, next_rows, axis=0)
                
    print(reduced_dimension_matrix)
    print(reduced_dimension_matrix.shape)

    return reduced_dimension_matrix

# Creating the reduced_matrix and using the np.save method to save it to a .npy file.
def main():
    index, database = create_db()

    reduced_matrix = latent_semantic_analysis_dimensionality_reduction(database)    
    print(reduced_matrix.shape)
    
    with open('reduced_dimension_matrix.npy', 'wb') as f:
        np.save(f, reduced_matrix)

    with open('reduced_dimension_matrix.npy', 'rb') as f:
        a = np.load(f, allow_pickle=True)
        
    print(a.shape)
    
if __name__ == "__main__":
    main()