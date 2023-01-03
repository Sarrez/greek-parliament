from indexer import create_index
import query_processor as qp
import unittest
import pandas as pd

class TestIndex(unittest.TestCase):
    def test_num_tokens(self):
        dataframe = pd.read_csv('test.csv', encoding='utf8', chunksize=3)
        tokens = create_index(dataframe = dataframe)
        num_tokens = len(tokens.keys())
        self.assertEqual(num_tokens, 6)

    def test_posting_list_length(self):
        dataframe = pd.read_csv('test.csv', encoding='utf8', chunksize=3)
        tokens = create_index(dataframe = dataframe)
        posting_list = len(tokens['αυτ']['postinglist'].keys())
        self.assertEqual(posting_list, 2)
        posting_list = len(tokens['ομιλ']['postinglist'].keys())
        self.assertEqual(posting_list, 3)
    
    def test_posting_list_docs(self):
        dataframe = pd.read_csv('test.csv', encoding='utf8', chunksize=3)
        tokens = create_index(dataframe = dataframe)
        #print(tokens)
        correct = {'2':1}
        posting_list = tokens['τριτ']['postinglist']
        #print(posting_list)
        self.assertEquals(correct, posting_list)
        posting_list = tokens['αυτ']['postinglist']
        correct = {'0':1, '1':1}

class TestTopk(unittest.TestCase):
    def test_idf(self):
        dataframe = pd.read_csv('test.csv', encoding='utf8', chunksize=3)
        tokens = create_index(dataframe = dataframe)
        data = tokens['αυτ']
        idf = qp.idf(num_of_docs=3, num_of_docs_with_term=data["numdocs"])

if __name__ == '__main__':
    unittest.main()