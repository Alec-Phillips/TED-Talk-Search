"""
run this file to interact with the search engine system
"""

from time import sleep
from importlib import reload
import data_container
reload(data_container)
from data_container import DataContainer

data = DataContainer()
data.read_data()

def main():
    while True:
        print("Enter a search query:")
        query = input()
        # process query
            #
            #
            #
        print("Here are your search results:")
        sleep(3)
        print("\n\nWould you like to make another query? [Y/n]")
        another = ''
        while another != 'Y' and another != 'n':
            another = input()
        if another != 'Y':
            break


# if __name__ == "__main__":
#     main()
