import sklearn

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

import nltk
import math

nltk.download('punkt')
from nltk.tokenize import word_tokenize


class QueryProcessor:

    def __init__(self, query, data_container):
        self.query = query
        self.data_container = data_container
        self.tokenized_query = []
        self.query_vector = []
        self.full_doc_corpus = []
        self.individual_doc_vectors = {}

    def process_query(self):
        # initialize query vector and doc vectors
        self.tokenized_query = word_tokenize(self.query.lower())
        for key, doc in self.data_container.data.items():
            self.full_doc_corpus.append(doc.description.lower())
            curr_corpus = doc.transcript.lower()
            new_pipe = Pipeline([('count', CountVectorizer(vocabulary=self.tokenized_query)),
                  ('tfid', TfidfTransformer())]).fit([curr_corpus])
            new_vector = new_pipe['tfid'].idf_
            # print(new_vector)
            self.individual_doc_vectors[key] = new_vector
        pipe = Pipeline([('count', CountVectorizer(vocabulary=self.tokenized_query)),
                  ('tfid', TfidfTransformer())]).fit(self.full_doc_corpus)
        self.query_vector = pipe['tfid'].idf_
        # print(self.query_vector)

        similarities = []
        for ind, vec in self.individual_doc_vectors.items():
            similarity = self.cosine_similarity(vec, self.query_vector)
            similarities.append((similarity, ind))
        
        similarities.sort(key=lambda x:x[0], reverse=True)
        return similarities[:10]

    def cosine_similarity(self, v1, v2):
        numerator = self.dot_product(v1, v2)
        denominator = self.cosine_denominator(v1, v2)
        return numerator / denominator

    def dot_product(self, v1, v2):
        sum = 0
        for i, x in enumerate(v1):
            sum += (x * v2[i])
        return sum

    def cosine_denominator(self, v1, v2):
        sum1 = 0
        for x in v1:
            sum1 += (x**2)
        sum2 = 0
        for x in v2:
            sum2 += (x**2)
        return math.sqrt(sum1) * math.sqrt(sum2)


        






