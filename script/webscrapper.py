"""

FMCG Analytics test for Junior Data Engineer role
--------------------------------------------------
This Script perfroms web scrapping on https://books.toscrape.com/ page
it would extract details such as Name, Category,Price, StockAmount and
Rating from the first page. The ouput will be in two csv files one with
catgeory data and one with books data.

Name - Vraj Nena
Date Started - 26th March, 2024 
--------------------------------------------------
 """


import scrapy
from scrapy.crawler import CrawlerProcess
import csv
from urllib.parse import urljoin
import logging
import random
from fake_useragent import UserAgent
import re


# Setting up Logging as it would help track errors
# Example - 2025-03-26 09:26 - ERROR - Url failed to parse
logging.basicConfig(
    format="{asctime} -{levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

class BookScrapper(scrapy.Spider):
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
            fieldnames = ['Category_Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            logging.info('Succesfully Intialised Categories Data  CSVfile')
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,
                                 headers={"User-Agent": random.choice(self.agents_list)},
                                 callback= self.scrape_categories,
                                 errback=self.error_handler)


    def scrape_categories(self,response):
        """
        This function will fetch all the categories from book listing page
        and store it in csv files.
        
        """
        categories_list = response.css("div.side_categories ul li ul li a")

        for category in categories_list:
            category_name = category.css("::text").get().strip()
            # category_url = category.css("::attr(href)").get().strip()
            # category_joined_url= urljoin(response.url,category_url)
           
            
            
            with open(self.categories_data_csv,'a',newline='',encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([category_name])
                
            logging.info(f"Successfully scraped category: {category_name}")
        # for url in self.start_urls:
        #     yield scrapy.Request(url=url,
        #                          headers={"User-Agent": random.choice(self.agents_list)},
        #                          callback= self.scrape_book_listing_url,
        #                          errback=self.error_handler)

        yield from self.scrape_book_listing_url(response)
        
    def scrape_book_listing_url(self,response):

        """
        The scrape_book_lisiting_url functionality is to get all urls of books details page
        on the first page.  
       """
        
        books_url = response.css("article.product_pod")
        for url in books_url:
            individual_book_url = url.css("h3 a::attr(href)").get()
            joined_url = urljoin(response.url,individual_book_url)
            print(joined_url)

            yield scrapy.Request(
                url=joined_url,
                headers={"User-Agent": random.choice(self.agents_list)},
                callback=self.parse,
                errback=self.error_handler
            )


                
    def parse(self,response):
        """
        The scrape_book_details is important function getting the books details i.e data we need
        it will  scrape  Name, Category, Price,StockAmount and Rating.
        """

        book_name = response.css("div.product_main h1::text").get().strip()
        book_category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
        book_category = book_category.strip() if book_category else "Unknown"
        book_price = response.css("p.price_color::text").get().strip('£')
        book_stock_text = response.css("p.instock.availability::text").getall()
        book_stock = re.search(r'\d+', " ".join(book_stock_text).strip())

        book_stock = int(book_stock.group()) if book_stock else "Unknown"
        book_rating = response.css("p.star-rating::attr(class)").get()
        # replace_empty_rating = book_rating.replace("star-rating","").strip() if book_rating else "Unknown"
        rating_mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        book_rating_value = rating_mapping.get(book_rating.split()[-1], "Unknown") if book_rating else "Unknown"

        with open(self.books_data_csv,'a',newline='',encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([book_name,book_category,book_price,book_stock,book_rating_value])

        logging.info(f"Successfully scraped book: {book_name}")
            
        
    def error_handler(self, fail):
        logging.error(f"Request failed: {fail.request.url}")
        logging.error(f"Error: {fail.value}")




if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(BookScrapper)
    process.start()
    