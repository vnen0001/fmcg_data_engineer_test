 # FMCG Analytics Junior Data Engineer Test 

This repository contains a data engineering pipeline that scrapes book data from an online bookstore, stores it in a PostgreSQL database, performs business analysis through SQL queries, and visualizes the results.

## Table of Contents
- [Project Overview](#project-overview)
- [Components](#components)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Web Scraping](#web-scraping)
- [Database Setup](#database-setup)
- [SQL Queries](#sql-queries)
- [Automation](#automation)

## Project Overview

This project demonstrates a complete data engineering workflow:
1. Web scraping data from https://books.toscrape.com/
2. Storing and organizing data in a relational database
3. Analyzing data with SQL queries
4. Visualizing the results with a business intelligence tool

## Components

- `webscrapper.py`: Python script to scrape book data
- `db_script.sql`: PostgreSQL script to create database schema and load data
- `automation.sh`: Shell script to automate the entire workflow
- `visualization.pbix`: Power BI file for data visualization (see visualization section)

## Setup and Installation

### Prerequisites
- Python 3.x
- PostgreSQL
- pip (Python package manager)
- Power BI Desktop or Microsoft Excel

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd NAME_Results
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required Python packages:
```bash
pip install -r requirements.txt
```

4. Ensure PostgreSQL is running and accessible

## Usage

You can run the entire pipeline with a single command:

```bash
./automation.sh
```

This will:
1. Install required Python packages
2. Run the web scraper to collect data
3. Set up the database and load the data
4. Execute business queries
5. Output results to the console

## Web Scraping

The web scraper (`webscrapper.py`) is built using Scrapy to extract data from https://books.toscrape.com/.

### Design Choices

- **Scrapy Framework**: Used for its efficiency with static websites
- **User-Agent Rotation**: Implements rotation of user agents to avoid bot detection
- **Error Handling**: Comprehensive logging and error handling mechanisms
- **Data Validation**: Validates prices, stock amounts, and ratings

### Key Code Sections

#### Setting Up User Agents and CSV Files

```python
# List of user agents that will be used for rotation to avoid bot detection
agents_list = [UserAgent().random for _ in range(5)]

# CSV files for books and categories
books_data_csv = 'books_data.csv'
categories_data_csv = 'categories_data.csv'

def __init__(self):
    logging.info('Creating csv files for Categories and Book data')
    with open(self.books_data_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Category', 'Price', 'StockAmount', 'Rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        logging.info('Successfully Initialized Books Data CSV file')
```

#### Extracting Book Data

```python
def parse(self, response):
    book_name = response.css("div.product_main h1::text").get().strip()
    book_category = response.css("ul.breadcrumb li:nth-child(3) a::text").get()
    book_category = book_category.strip() if book_category else "Unknown"
    book_price = response.css("p.price_color::text").get()
    
    # Data validation for price
    if book_price:
        book_price = book_price.strip('£')
        try:
            book_price = float(book_price)
        except ValueError:
            logging.error(f'Invalid price for {book_name}: {book_price}')
            return
    else:
        logging.error(f'No price found for {book_name}')
        return
```

## Database Setup

The database setup script (`db_script.sql`) creates a normalized relational database schema and loads the scraped data.

### Database Schema

The database consists of two main tables:
- `categories`: Stores unique book categories
- `books`: Stores book details with a foreign key reference to categories

### Key SQL Operations

#### Table Creation

```sql
-- Create a `categories` table with unique id assigned to each book category
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL
);

-- Create a `books` table with references to categories table
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category_id INTEGER DEFAULT 1 REFERENCES categories (category_id) ON DELETE SET DEFAULT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    rating INT CHECK (
        rating >= 1
        AND rating <= 5
    )
);
```

#### Data Loading Process

```sql
-- Load `categories` data from CSV file
\COPY categories (category_name) FROM 'categories_data.csv' WITH (FORMAT CSV,HEADER TRUE,DELIMITER ',')

-- Load books data into temporary table
\COPY temp_books (name,category_name,price,stock,rating) FROM 'books_data.csv' WITH (FORMAT CSV,HEADER TRUE,DELIMITER ',')

-- Insert from temp table to books table with proper category IDs
INSERT INTO books (title, category_id, price, stock, rating)
SELECT
    tb.name, 
    c.category_id,
    tb.price,
    tb.stock,
    tb.rating
FROM
    temp_books tb
    JOIN categories c ON tb.category_name = c.category_name;
```

## SQL Queries

The SQL queries answer key business questions about the book data.

### Business Query 1: Top Categories by Rating and Price

This query identifies the top three categories with the highest average rating and lowest minimum price:

```sql
SELECT
    c.category_name,
    ROUND(AVG(b.rating), 2) AS avg_rating,
    MIN(b.price) AS min_price
FROM
    books b
    JOIN categories c ON b.category_id = c.category_id
GROUP BY
    c.category_name
ORDER BY
    avg_rating DESC,
    min_price ASC
LIMIT 3;
```

### Business Query 2: Top 5 Books by Rating

This query finds the top 5 books by rating, with secondary sorting by stock and price:

```sql
SELECT
    b.title,
    b.rating,
    b.stock,
    b.price,
    c.category_name
FROM
    books b 
    JOIN categories c ON b.category_id = c.category_id
ORDER BY
    rating DESC, stock DESC, price ASC
LIMIT 5;
```

## Automation

The automation script (`automation.sh`) ties all components together into a seamless workflow.

```bash
#!/bin/bash

read -p "Please Enter database name (press enter to use 'postgres')" DB_NAME
DB_NAME=${DB_NAME:-postgres}

echo "Using database: $DB_NAME"

echo "Installing python packages"
pip3 install -r requirements.txt

echo "Running WebScraper"
python3 webscrapper.py

echo "Initializing tables"
psql -d $DB_NAME -f db_script.sql

echo "Running Business Queries"
echo -e "\n----- Query 1: Top three categories with highest average rating and lower price -----"
psql -d $DB_NAME -c "
SELECT
    c.category_name,
    ROUND(AVG(b.rating), 2) AS avg_rating,
    MIN(b.price) AS min_price
FROM
    books b
    JOIN categories c ON b.category_id = c.category_id
GROUP BY
    c.category_name
ORDER BY
    avg_rating DESC,
    min_price ASC
LIMIT 3;"

echo -e "\n----- Query 2: Top 5 books by rating -----"
psql -d $DB_NAME -c "
SELECT
    b.title,
    b.rating,
    b.stock,
    b.price,
    c.category_name
FROM
    books b 
    JOIN categories c ON b.category_id = c.category_id
ORDER BY
    rating DESC, stock DESC, price ASC
LIMIT 5;"

echo -e "\nAll tasks completed successfully!"
```

This script provides a one-click solution to run the entire data pipeline.
