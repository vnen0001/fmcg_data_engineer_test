
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



"""
PROCESS FLOW

Step 1 : The initial request is sent to https://books.toscrape.com/ and with css selectors the 
         categoreis and  url for each book description page is fetched. The request is sent by
         selecting a random User-Agent to mimic real browser behaviour.

Step 2 : The categories data is stored in a csv file while scrapy sends a request to each url
         of deatiled page for books present in first page. 

Step 3 : The request response from step 2 is being scrapped by using css selectors with some
        data validation to make sure accurate data is being fetched. 

Step 4 : It has been assumed quantifiable metrics such as price , stock and rating are business
        critical values so there has been proper data validation approach.
        For example - A book with no price is not useful but a book with no stock and no rating
                     can be assumed that either it is out of stock or no rating are provided.

Step 5 : The books data scrapped is stored in a csv filw using a csv writer object and stored in 
        same project directory.

"""

"""
DESIGN CHOICES
- I have used scrapy as web scrapping library due to reaosn being the https://books.toscrape.com/ website
  is a static website and there is less use of javascript. If the website was more heavy on javascript the 
  preferred option would have been to use Selenium.
- The scrapy also provides some built in functionality such as `callback` and `errback` which has helped
  me to pass the request data to required function and also to call error function whenever required
- I have implemented user-agent rotation as I don't want scrapper to not work due to bot detection.
- Each step is logged so that error can be traceback easily.

"""

import scrapy                                # Scrapy for craling website
from scrapy.crawler import CrawlerProcess
import csv                                   # csv to write data into csv file
from urllib.parse import urljoin             # To join url to with root url
import logging                               # Loggint to track errors
import random                                # To select random values 
from fake_useragent import UserAgent         # Generates fake use agent
import re                                    # Specifally use fetching price and stock quantity.
 

# Setting up Logging as it would help track errors
# Example - 2025-03-26 09:26 - ERROR - Url failed to parse
logging.basicConfig(
    format="{asctime} -{levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# This class defines the logic of crawling , data extraction and data storage function.
class BookScrapper(scrapy.Spider):
    name='BooksScrapper'
    allowed_domains=['books.toscrape.com']
    start_urls=['https://books.toscrape.com/']

    # list of user agent that will be used for rotation. To avoid bot detection.
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
    
    # Responsbile for starting the crwaling process 
    def start_requests(self):
        """
        The `start_requests` function generates scrapy requests for each URL in `self.start_urls` with a
        random User-Agent header and specified callback and error handling functions.

        """
        for url in self.start_urls:
            yield scrapy.Request(url=url,
                                 headers={"User-Agent": random.choice(self.agents_list)},
                                 callback= self.scrape_categories,
                                 errback=self.error_handler)


  
    # Scrapes list of categories and stores it in csv file.
    def scrape_categories(self,response):
        """
    The function `scrape_categories` scrapes category names from a website response and writes them to a
    CSV file while logging the successful scraping of each category.
    
    :param response: The `response` parameter in the `scrape_categories` method is  an object
    that contains the data retrieved from a web page after making a request. 
        """
      
        categories_list = response.css("div.side_categories ul li ul li a")

        for category in categories_list:
            category_name = category.css("::text").get().strip()
 
            with open(self.categories_data_csv,'a',newline='',encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([category_name])
                
            logging.info(f"Successfully scraped category: {category_name}")
        yield from self.scrape_book_listing_url(response)
        
    # Scrapes all the url from book detail page.
    def scrape_book_listing_url(self,response):
        """
        The function scrapes individual book URLs from a response and generates requests to parse each
        book page.
        
        :param response: The `scrape_book_listing_url` function is a method that takes a `response` object
        as input. The `response` object typically contains the HTML content of a webpage that has been
        fetched Scrapy requests.
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


    # Main function that scrapes book_name, category, price , stock and rating                
    def parse(self,response):
        """
        This Python function parses information from a website response and writes the extracted data to a
        CSV file.
        
        :param response: Python function that parses data from a web scraping response object and writes the extracted
        information to a CSV file. The function extracts book name, category, price, stock availability, and rating 
        from the response object using CSS selectors
        """

        book_name = response.css("div.product_main h1::text").get().strip()               # Book Name
        book_category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()       # Book Category and replacing it by Unkown if empty
        book_category = book_category.strip() if book_category else "Unknown"             
        book_price = response.css("p.price_color::text").get()                 # Stripiing whitespace and £ sign 

        #Data validation for price
        if book_price:
            book_price = book_price.strip('£')
            try:
                book_price = float(book_price)
            except ValueError:
                logging.error(f'Invalid price for {book_name}: {book_price}')
                return  # It will skip the book with invalid price
        else:
            logging.error(f'No price found for {book_name}')
            return # Will also skip book if no price.
        book_stock_text = response.css("p.instock.availability::text").getall()
        book_stock = re.search(r'\d+', " ".join(book_stock_text).strip())                 # Using regex to stock quantity e.g. In Stock (22) will give 22. 

        # Data validation for book stock 
        if book_stock:
            book_stock = int(book_stock.group())
        else:
            logging.error(f'Assuming 0 stock for {book_name}')
            book_stock=0
            
        book_rating = response.css("p.star-rating::attr(class)").get()                    # Mapping rating words to number 
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
        """
        The function `error_handler` logs the failed request URL and error message.
        """
        logging.error(f"Request failed: {fail.request.url}")
        logging.error(f"Error: {fail.value}")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(BookScrapper)
    process.start()
    