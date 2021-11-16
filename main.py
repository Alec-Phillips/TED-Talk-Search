"""
run this file to interact with the search engine system
"""

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


def main():
    while True:
        print("Enter a search query:")
        query = input()

        processor = QueryProcessor(query, data)
        search_results = processor.process_query()
        # print(processor.individual_doc_vectors.get(1))
        # process query
            #
            #
            #
        print("Here are your search results:")
        for doc in search_results:
            print(f'\t{data.get_title(doc[1])}')
        sleep(3)
        print("\n\nWould you like to make another query? [Y/n]")
        another = ''
        while another != 'Y' and another != 'n':
            another = input()
        if another != 'Y':
            break


if __name__ == "__main__":
    main()
