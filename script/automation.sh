#!/bin/bash

read -p "Please Enter database name (press enter to use 'postgres')" DB_NAME
DB_NAME=${DB_NAME:-postgres}

echo "Using database: $DB_NAME"

echo "Installing python packages"
pip3 install -r requirements.txt

echo "Runing WebScrapper"
python3 webscrapper.py

echo "Initialising tables"
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