
import nltk
import math
import json
import spacy

#nltk.download('punkt')
#nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
stopwords = stopwords.words('english')
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()


class QueryProcessor:
    """
    This module holds the actual search engine model/code
    The train function sets up the TF-IDF vectors for each document and reads to txt file
    Another method for loading in the pre-trained data
    Finally the method for actually processing the query
    """

    def __init__(self, data_container):
        self.query = ''
        self.data_container = data_container
        self.term_frequencies = {} # { term : { doc : frequency } }
        self.tf_idf_table = {} # { term : { doc : tf-idf val } } NEED THIS
        self.num_docs = len(data_container.data.keys())
        self.term_list = []
        self.id_list = []   # NEED THIS
        self.term_vectors = {}  
        self.individual_doc_vectors = {}    # NEED THIS

    def train(self, fp_1, fp_2, fp_3):
        """
        This method pre-trains by saving the TF-IDF centroid vectors
        they are stored in json format in txt files
        """
        print('\n[Training Model...]')
        print('\t- Learning Term Frequencies...')
        term_set = set()
        for id, doc in self.data_container.data.items():
            print(id)
            self.id_list.append(id)
            words = word_tokenize(doc.transcript)
            words = [word.lower() for word in words if word not in stopwords]

            topics = [topic for topic in doc.topics]
            words += topics

            desc = word_tokenize(doc.description)
            desc = [word.lower() for word in desc if word not in stopwords]
            words += desc

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
            words = word_tokenize(doc.transcript)
            words = [word.lower() for word in words if word not in stopwords]

            topics = [topic for topic in doc.topics]
            words += topics

            desc = word_tokenize(doc.description)
            desc = [word.lower() for word in desc if word not in stopwords]
            words += desc

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
        json.dump(self.individual_doc_vectors, fp_1)
        json.dump(self.id_list, fp_2)
        json.dump(self.tf_idf_table, fp_3)
        print('[Done Training]')

    def tf(self, term_count):
        return math.log10(term_count + 1)

    def idf(self, term):
        return math.log10(self.num_docs / len(self.term_frequencies.get(term).keys()))

    def read_pre_train_data(self, fp_1, fp_2, fp_3):
        """
        Reads in the pre-traineed data and sets up the proper member variables
        so that new queries can be processed
        """
        data = json.load(fp_1)
        for id, vec in data.items():
            self.data_container.data.get(int(id)).set_vector(vec)
        ids = json.load(fp_2)
        self.id_list = ids
        self.tf_idf_table = json.load(fp_3)

    def process_query(self, query):
        """
        Vectorizes the query and performs cosine similarity between the query
        and each document, returning the ten best matches
        """
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
                    if str(doc_id) in self.tf_idf_table.get(term):
                        curr_term_vector.append(self.tf_idf_table.get(term).get(str(doc_id)))
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

            # make sure that the doc appended actually has some similarity
            # i.e., cos similarity > 0
            if self.cosine_similarity(doc.get_vector(), query_vector) > 0:
                similarities.append((self.cosine_similarity(doc.get_vector(), query_vector), id))
            else:
                similarities.append((0, id))

        similarities.sort(key=lambda x:x[0], reverse=True)

        # check to make sure that cos similarity is nontrivial
        # in the trivial case, let the user know that there is no match

        # if there are no relevant entries (i.e., all cos similarities == 0)
        # tell the user there is no match
        # if there is at least 1 relevant entry, return it
        # if there are 10, return all

        relevant_entries = []
        for similarity in similarities:
            if similarity[0] == 0 and len(relevant_entries) == 0: # no relevant entries - max cos similarity is 0
                return self.topic_search(query)
            elif similarity[0] > 0: # at least one nontrivial match
                relevant_entries.append(similarity)

        # return 10 most important matches
        relevant_entries.sort(key=lambda x:x[0], reverse=True)

        return relevant_entries[:10] # at this point, already taken care of the case where len(relevant_entries) == 0

    def topic_search(self, query):

        # get the root of the query
        # find nsubj that depends on root
        # search: for topic in topics, see if nsubj in topic
        # aggregate all talks and return list of best talks
        en_nlp = spacy.load("en_core_web_sm")

        doc = en_nlp(query) # query is a string which comes directly from user input
        query_nsubj = ""
        query_root = ""
        query_term = ""

        # simple case: len(query) == 1
        if " " not in query.strip():
            query_nsubj = query

        # general case: query is a multiple-word user input
        # use word.text from spacy's word token
        # https://stackoverflow.com/questions/62786554/got-argument-other-has-incorrect-type-expected-spacy-tokens-token-token-got
        else:
            for word in doc:
                if word.dep_ == "nsubj":
                    query_nsubj = str(word.text)
                if word.dep_ == "ROOT":
                    query_root = str(word.text)
                if query_nsubj != "" and query_root != "":
                    break

        # decide whether or not the key term is root or nsubj
        # if nsubj is available, use that
        # otherwise, default to root
        query_term = query_root if query_nsubj == "" else query_nsubj

        talks = []

        # pass in appropriate format of (cos_similarity, id) - here, cos similarity is 0, so use None
        for id, document in self.data_container.data.items():
            if query_term in document.topics:
                talks.append((None, id))

        # filter talks by most popular
        # if len(talks) > 10, sort talks by popular and return top 10
        if len(talks) <= 10:
            return talks
        else:
            talks.sort(key=lambda x:self.data_container.data.get(x[1]).views, reverse=True)
            return talks[:10]

    def cosine_similarity(self, v1, v2):
        numerator = self.dot_product(v1, v2)
        denominator = self.cosine_denominator(v1, v2)
        if denominator == 0:
            return 0
        else:
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
