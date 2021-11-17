import sklearn

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

import nltk
import math
import json

nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
stopwords = stopwords.words('english')
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()


class QueryProcessor:

    def __init__(self, data_container):
        self.query = ''
        self.data_container = data_container
        self.term_frequencies = {} # { term : { doc : frequency } }
        self.tf_idf_table = {} # { term : { doc : tf-idf val } }
        self.num_docs = len(data_container.data.keys())
        self.term_list = []
        self.id_list = []
        self.term_vectors = {}
        
        
        self.tokenized_query = []
        self.query_vector = []
        self.full_doc_corpus = []
        self.individual_doc_vectors = {}

    def train(self, fp):
        print('\n[Training Model...]')
        print('\t- Learning Term Frequencies...')
        term_set = set()
        for id, doc in self.data_container.data.items():
            print(id)
            self.id_list.append(id)
            words = word_tokenize(doc.description)
            words = [word.lower() for word in words if word not in stopwords]
            stems = [stemmer.stem(word) for word in words]
            for term in set(stems):
                term_set.add(term)
                if term not in self.term_frequencies:
                    self.term_frequencies[term] = {id: words.count(term)}
                else:
                    self.term_frequencies[term][id] = words.count(term)
        for term in term_set:
            self.term_list.append(term)
        print('\t- Computing TF-IDF for each term...')
        for term, docs in self.term_frequencies.items():
            self.tf_idf_table[term] = {}
            for id, count in docs.items():
                term_tf_idf = self.tf(count) * self.idf(term)
                self.tf_idf_table[term][id] = term_tf_idf
        print('\t- Creating Centroid Vector for each Document...\n\t   - this takes about a minute')
        for id, doc in self.data_container.data.items():
            print(id)
            term_vectors = []
            words = word_tokenize(doc.description)
            words = [word.lower() for word in words if word not in stopwords]
            stems = [stemmer.stem(word) for word in words]
            for term in set(stems):
                curr_term_vector = []
                if term in self.term_vectors:
                    curr_term_vector = self.term_vectors.get(term)
                else:
                    for doc_id in self.id_list:
                        if doc_id in self.tf_idf_table.get(term):
                            curr_term_vector.append(self.tf_idf_table.get(term).get(doc_id))
                        else:
                            curr_term_vector.append(0)
                    self.term_vectors[term] = curr_term_vector
                term_vectors.append(curr_term_vector)
            centroid = [0] * len(self.id_list)
            for vector in term_vectors:
                for i in range(len(centroid)):
                    centroid[i] = centroid[i] + vector[i]
            for i in range(len(centroid)):
                centroid[i] = centroid[i] / len(term_vectors)
            doc.set_vector(centroid)
            self.individual_doc_vectors[id] = centroid
        json.dump(self.individual_doc_vectors, fp)
        print('[Done Training]')


    def tf(self, term_count):
        return math.log10(term_count + 1)

    def idf(self, term):
        return math.log10(self.num_docs / len(self.term_frequencies.get(term).keys()))



    def process_query(self, query):
        print('\nProcessing Your Query...')
        term_vectors = []
        words = word_tokenize(query)
        words = [word.lower() for word in words if word not in stopwords]
        stems = [stemmer.stem(word) for word in words]
        for term in set(stems):
            curr_term_vector = []
            if term in self.term_vectors:
                curr_term_vector = self.term_vectors.get(term)
            else:
                if term not in self.tf_idf_table:
                    continue
                for doc_id in self.id_list:
                    if doc_id in self.tf_idf_table.get(term):
                        curr_term_vector.append(self.tf_idf_table.get(term).get(doc_id))
                    else:
                        curr_term_vector.append(0)
                self.term_vectors[term] = curr_term_vector
            term_vectors.append(curr_term_vector)
        if term_vectors == []:
            return []
        query_vector = [0] * len(self.id_list)
        for vector in term_vectors:
            for i in range(len(query_vector)):
                query_vector[i] = query_vector[i] + vector[i]
        for i in range(len(query_vector)):
            query_vector[i] = query_vector[i] / len(term_vectors)
        similarities = []
        for id, doc in self.data_container.data.items():
            similarities.append((self.cosine_similarity(doc.get_vector(), query_vector), id))
        similarities.sort(key=lambda x:x[0], reverse=True)
        return similarities[:10]
        

    #     # initialize query vector and doc vectors
    #     self.tokenized_query = word_tokenize(self.query.lower())
    #     for key, doc in self.data_container.data.items():
    #         self.full_doc_corpus.append(doc.description.lower())
    #         curr_corpus = doc.transcript.lower()
    #         new_pipe = Pipeline([('count', CountVectorizer(vocabulary=self.tokenized_query)),
    #               ('tfid', TfidfTransformer())]).fit([curr_corpus])
    #         new_vector = new_pipe['tfid'].idf_
    #         # print(new_vector)
    #         self.individual_doc_vectors[key] = new_vector
    #     pipe = Pipeline([('count', CountVectorizer(vocabulary=self.tokenized_query)),
    #               ('tfid', TfidfTransformer())]).fit(self.full_doc_corpus)
    #     self.query_vector = pipe['tfid'].idf_
    #     # print(self.query_vector)

    #     similarities = []
    #     for ind, vec in self.individual_doc_vectors.items():
    #         similarity = self.cosine_similarity(vec, self.query_vector)
    #         similarities.append((similarity, ind))
        
    #     similarities.sort(key=lambda x:x[0], reverse=True)
    #     return similarities[:10]

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


        






