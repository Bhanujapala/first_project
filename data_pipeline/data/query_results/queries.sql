-- query_1_select_where
SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
        ORDER BY rating DESC

-- query_2_order_limit
SELECT title, price_gbp, rating
        FROM books
        ORDER BY price_gbp DESC
        LIMIT 10

-- query_3_distinct
SELECT DISTINCT category_name
        FROM categories
        ORDER BY category_name

-- query_4_between
SELECT title, price_gbp, rating
        FROM books
        WHERE price_gbp BETWEEN 10 AND 30
        ORDER BY price_gbp

-- query_5_join
SELECT
            b.title,
            b.price_gbp,
            b.price_inr,
            b.rating,
            b.in_stock,
            c.category_name
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY b.rating DESC, c.category_name, b.title
        LIMIT 10

