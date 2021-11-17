"""
run this file to interact with the search engine system
"""

from re import search
import os
import gzip
import shutil
from time import sleep
from importlib import reload
import data_container
import query_processor
reload(data_container)
reload(query_processor)
from data_container import DataContainer
from query_processor import QueryProcessor

data = DataContainer()
data.read_data()

processor = QueryProcessor(data)

cur_path = os.path.dirname(__file__)
pre_training_path = os.path.relpath('pre_training_json.txt', cur_path)
# with open(pre_training_path, 'w') as outfile:
#     processor.train(outfile)
# outfile.close()
with open(pre_training_path, 'rb') as f_in:
    with gzip.open(pre_training_path + '.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
# f = open(pre_training_path)
# content = f.read()
# with gzip.open(pre_training_path, 'wb') as f:
#     f.write(content)

def main():
    while True:
        print("Enter a search query:")
        query = input()

        search_results = processor.process_query(query)
        # print(processor.individual_doc_vectors.get(1))
        # process query
            #
            #
            #
        if search_results == []:
            print('\nSorry, there were no matches to your query')
        else:
            print("\nHere are your search results:")
            for doc in search_results:
                print(f'\t- talk id: {doc[1]}, title: {data.get_title(doc[1])}')
        sleep(3)
        print("\n\nWould you like to make another query? [Y/n]")
        another = ''
        while another != 'Y' and another != 'n':
            another = input()
        if another != 'Y':
            break


# if __name__ == "__main__":
#     main()
