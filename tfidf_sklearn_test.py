import sklearn

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

corpus = ["first document", "this is the second document", "welcome to NLP", "NLP", "NLP is fun", "VSCode"]
vocab = ["this", "is", "NLP", "fun", "application"]

pipe = Pipeline([('count', CountVectorizer(vocabulary=[elem.lower() for elem in vocab])),
                  ('tfid', TfidfTransformer())]).fit(corpus)
print(pipe['count'].transform(corpus).toarray())

print(pipe['tfid'].idf_)
print(pipe.transform(corpus).shape)