
-- E-commerce Seller Performance Analysis
-- SQL dialect: PostgreSQL
-- Expected tables: orders, order_items, sellers, order_reviews

-- 1. Top 10 sellers by item revenue
SELECT
    s.seller_id,
    s.seller_city,
    ROUND(SUM(oi.price)::numeric, 2) AS total_item_revenue,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM sellers s
JOIN order_items oi
    ON s.seller_id = oi.seller_id
GROUP BY s.seller_id, s.seller_city
ORDER BY total_item_revenue DESC
LIMIT 10;


-- 2. Seller-associated on-time delivery rate
-- Delivery status is measured at order level, not seller level.
WITH seller_orders AS (
    SELECT DISTINCT seller_id, order_id
    FROM order_items
),
delivery_metrics AS (
    SELECT
        so.seller_id,
        so.order_id,
        CASE
            WHEN o.order_delivered_customer_date
                 <= o.order_estimated_delivery_date
            THEN 1
            ELSE 0
        END AS on_time
    FROM seller_orders so
    JOIN orders o
        ON so.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
)
SELECT
    seller_id,
    COUNT(*) AS eligible_orders,
    ROUND(AVG(on_time::numeric) * 100, 2) AS on_time_delivery_pct
FROM delivery_metrics
GROUP BY seller_id
ORDER BY on_time_delivery_pct DESC;


-- 3. Average review score associated with each seller
-- Reviews belong to orders. Multi-seller orders share the same review
-- across their associated sellers, so this is an approximate measure.
WITH seller_orders AS (
    SELECT DISTINCT seller_id, order_id
    FROM order_items
)
SELECT
    so.seller_id,
    COUNT(DISTINCT so.order_id) AS reviewed_orders,
    ROUND(AVG(r.review_score)::numeric, 2) AS average_review_score
FROM seller_orders so
JOIN order_reviews r
    ON so.order_id = r.order_id
GROUP BY so.seller_id
ORDER BY average_review_score DESC;


-- 4. Seller cancellation rate
WITH seller_orders AS (
    SELECT DISTINCT seller_id, order_id
    FROM order_items
)
SELECT
    so.seller_id,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE o.order_status = 'canceled'
    ) AS cancelled_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE o.order_status = 'canceled'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_rate_pct
FROM seller_orders so
JOIN orders o
    ON so.order_id = o.order_id
GROUP BY so.seller_id
ORDER BY cancellation_rate_pct DESC;
