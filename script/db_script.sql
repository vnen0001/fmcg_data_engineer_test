-- Active: 1731834456484@@127.0.0.1@5432


------------------------------------------------------
-- Name: Vraj Nena
-- Database: PostgreSQL 15.8
-- Description: Perfroms Database setup and Data loading
------------------------------------------------------
 select CURRENT_USER;

------------------------------------------------------
-- DATABASE SETUP: Drop exisitng table if they exists
------------------------------------------------------

-- Drop `categories` table if it exisits to prevent conflicts
DROP TABLE IF EXISTS categories CASCADE;

-- Create a `categories` table with unique id assigned to each book category.
-- `category_id` will have an auto increment primary key.
-- `category_name` has constraint to be each value as unique as we only need distinct list.
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) UNIQUE NOT NULL
);

-- Inserting a Unknown category if webscrapping misses any categories they all should be grouped 
INSERT INTO categories (category_name) VALUES ('Unknown');
-- Drop `books` table if it exisits to prevent conflicts
DROP TABLE IF EXISTS books CASCADE; 

-- Create a `books` table with unique id `book_id` and referncing `categories` table.
-- `book_id` auto increment primary key for the table
-- `category_id` referencing to `categories` table 
-- `rating` column with values between 1 to 5 
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category_id INTEGER DEFAULT 1 REFERENCES categories (category_id) ON DELETE SET DEFAULT,
    -- The default value is set to 1. If any category is deleted it will maitain books records with `Unknown` Category.
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    rating INT CHECK (
        rating >= 1
        AND rating <= 5
    )
    -- Ensuring rating values are between 1 to 5
);

------------------------------------------------------
-- TEMP TABLE FOR DATA LOADING
------------------------------------------------------

--  Below line is optional as temp_tables are droppes after each session
-- DROP TABLE IF EXISTS temp_books;

-- Creating a temp table `temp_books` to load data 
CREATE TEMP TABLE temp_books (
    name TEXT,
    category_name TEXT,
    price DECIMAL(10, 2),
    stock INT,
    rating INTEGER
);

------------------------------------------------------
-- DATA LOADING FROM CSV FILE
------------------------------------------------------

-- Load `categories` data from a specified csv file. (Use absolute path or set permission for postgres to access folder).
-- This step populates category tables 
\COPY categories (category_name) FROM 'categories_data.csv' WITH (FORMAT CSV,HEADER TRUE,DELIMITER ',')

-- Load `temp_books` data from books_data.csv file
-- This step temporarily stores books data before migrating to books table
\COPY temp_books (name,category_name,price,stock,rating)FROM 'books_data.csv' WITH (FORMAT CSV,HEADER TRUE,DELIMITER ',')

------------------------------------------------------
-- DATA LOADING INTO BOOKS TABLE
------------------------------------------------------

-- This step loads books data from `temp_books` into `books` table
-- It ensures that correct `category_id` is mapped from `categories` table.
INSERT INTO
    books (
        title,
        category_id,
        price,
        stock,
        rating
    )
SELECT
    tb.name, 
    c.category_id,  -- category id from categories table
    tb.price,
    tb.stock,
    tb.rating
FROM
    temp_books tb
    JOIN categories c ON tb.category_name = c.category_name;


-- Drop temporary table although there is no need to explicitly mention it as it will be droppes after every seesion
DROP TABLE temp_books;


