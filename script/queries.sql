
------------------------------------------------------
-- Name: Vraj Nena
-- Database: PostgreSQL 15.8
-- Description  - Contains Queries to answer Business problems
------------------------------------------------------

------------------------------------------------------
-- Query 1 
-- Problem : Which are the top three categories with the highest average rating and the lower price?
------------------------------------------------------

-- STEPS (Logical order in which query is executed)
-- 1. FROM/JOIN -  The data is pulled from `books` and `category` table and joined on `category_id`
-- 2. SELECT - It will select `category_name`, `avg_rating` and `price`.
-- 3. GROUPBY - Performs group by as we need top 3 categoies 
-- 4. ORDER BY - First it will sort by avg_rating in descending and price in ascending order.
-- 5. LIMIT - We only need top 3  limit 3 is used. 

select
    c.category_name,
    round(avg(b.rating), 2) as avg_rating,
    round(avg(b.price),2) as price
from
    books b
    join categories c on b.category_id = c.category_id
group by
    c.category_name
ORDER BY
    avg_rating DESC,
    price ASC
LIMIT
    3;


------------------------------------------------------
-- Query 2 
-- Problem : Which are the top 5 books by rating?
------------------------------------------------------
-- Note: THIS QUERY CAN BE RETRIEVED ALONE FROM `books` table BUT JOINED WITH `category` FOR BETTER FILTERING IN BI DASHBOARD.

-- STEPS (Logical order in which query is executed)
--1. FROM/JOIN - The data is pulled from `books` and `category` table and joined on `category_id`
--2. SELECT - It will select `title`, `rating`, `stock`, `price` and `category_name`.
--3. ORDER BY - It will sort by rating in desceding , stock in decedning and price in ascending order.
--4. LIMIT - We only need top 5  limit 5 is used. 


select
    b.title,
    b.rating,
    b.stock,
    b.price,
    c.category_name
from
    books b 
    join categories c on b.category_id = c.category_id
ORDER BY
    rating DESC,stock DESC,price ASC
LIMIT
    5;
