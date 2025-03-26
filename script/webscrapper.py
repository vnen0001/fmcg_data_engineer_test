"""

FMCG Analytics test for Junior Data Engineer role
--------------------------------------------------
This Script perfroms web scrapping on https://books.toscrape.com/ page
it would extract details such as Name, Category,Price, StockAmount and
Rating from the first page. The ouput will be in two csv files one with
catgeory data and one with book data.

Name - Vraj Nena
Date Started - 26th March, 2024 
--------------------------------------------------
 """


import scrapy
from scrapy.crawlers import CrawlerProcess
from scrapy.utils.project import get_project_settings
import csv
from urllib.parse import urljoin
import logging
import random
from fake_useragent import UserAgent


# Setting up Logging as it would help track errors
# Example - 2025-03-26 09:26 - ERROR - Url failed to parse
logging.basicConfig(
    format="{asctime} -{levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

class BookScrapper(scrapy.spider):
    name='BooksScrapper'
    allowed_domains=['books.toscrape.com']
    start_urls=['https://books.toscrape.com/']

    # list of user agent that will be used for rotation.
    agents_list = [ UserAgent().random for _ in range(5)]

    #csv files for books and categories
    books_data_csv = 'books_data.csv'
    categories_data_csv = 'categories_data.csv'

    def __init__(self):
        logging.info('Creating csv files for Categories and Book data')
        with open(self.books_data_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Name', 'Category', 'Price', 'StockAmount', 'Rating']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            logging.info('Succesfully Intialised Books Data CSVfile')

        with open( self.categories_data_csv,'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Category_Name', 'Category_Url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            logging.info('Succesfully Intialised Categories Data  CSV file')

    



            




