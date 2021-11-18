"""
run this file to interact with the search engine system
"""

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
pre_training_path_1 = os.path.relpath('doc_vectors_json.txt', cur_path)
pre_training_path_2 = os.path.relpath('id_list_json.txt', cur_path)
pre_training_path_3 = os.path.relpath('tf_idf_table_json.txt', cur_path)
# with open(pre_training_path_1, 'w') as outfile_1:
#     with open(pre_training_path_2, 'w') as outfile_2:
#         with open(pre_training_path_3, 'w') as outfile_3:
#             processor.train(outfile_1, outfile_2, outfile_3)

with open(pre_training_path_1, 'r') as infile_1:
    with open(pre_training_path_2, 'r') as infile_2:
        with open(pre_training_path_3, 'r') as infile_3:
            processor.read_pre_train_data(infile_1, infile_2, infile_3)

# outfile.close()
# with open(pre_training_path, 'rb') as f_in:
#     with gzip.open(pre_training_path + '.gz', 'wb') as f_out:
#         shutil.copyfileobj(f_in, f_out)
# with gzip.open(pre_training_path + '.gz', 'rb') as f:
#     pre_training_data = f.read()
# f.close()
# with open(pre_training_path, 'wb') as outfile:
#     outfile.write(pre_training_data)
# outfile.close()
# f = open(pre_training_path, 'r')
# processor.read_pre_train_data(f)
# f.close()

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


if __name__ == "__main__":
    main()
