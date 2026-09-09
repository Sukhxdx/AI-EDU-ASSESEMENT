-- =============================================================================
-- BDA Lecture — SQL Attendance Queries
-- Student : Sukhada Dhingra
-- Date    : 09 September 2026
--
-- Assumed table : orders
-- Assumed columns used by the tasks:
--   order_status, category, revenue, customer_segment, sales_channel,
--   payment_method, profit, customer_rating, city, product
-- Replace `orders` with your Hive/Spark table name if it is different.
-- =============================================================================

-- Task 1: Show all delivered orders.
SELECT *
FROM orders
WHERE order_status = 'Delivered';


-- Task 2: Show Electronics orders with revenue above 50,000.
SELECT *
FROM orders
WHERE category = 'Electronics'
  AND revenue > 50000;


-- Task 3: Count orders by customer_segment.
SELECT
    customer_segment,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_segment;


-- Task 4: Calculate total revenue by sales_channel.
SELECT
    sales_channel,
    SUM(revenue) AS total_revenue
FROM orders
GROUP BY sales_channel;


-- Task 5: Calculate total profit by payment_method.
SELECT
    payment_method,
    SUM(profit) AS total_profit
FROM orders
GROUP BY payment_method;


-- Task 6: Find average customer rating by city.
SELECT
    city,
    AVG(customer_rating) AS avg_customer_rating
FROM orders
GROUP BY city;


-- Task 7: Find the top 10 products by total profit.
SELECT
    product,
    SUM(profit) AS total_profit
FROM orders
GROUP BY product
ORDER BY total_profit DESC
LIMIT 10;


-- Task 8: Find the top 10 city/category combinations by revenue.
SELECT
    city,
    category,
    SUM(revenue) AS total_revenue
FROM orders
GROUP BY city, category
ORDER BY total_revenue DESC
LIMIT 10;
