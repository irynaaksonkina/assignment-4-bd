CREATE OR REPLACE VIEW order_summary AS
SELECT
    o.id AS order_id,
    o.created_at AS order_date,
    o.status AS order_status,
    o.total_amount,
    c.first_name,
    c.last_name,
    c.email,
    a.city,
    a.street,
    COALESCE(SUM(oi.quantity), 0) AS number_of_items,
    p.method AS payment_method,
    p.status AS payment_status
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN addresses a ON o.address_id = a.id
LEFT JOIN order_items oi ON oi.order_id = o.id
LEFT JOIN payments p ON p.order_id = o.id
GROUP BY o.id, c.id, a.id, p.id;

EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';

EXPLAIN ANALYZE
SELECT * FROM orders WHERE total_amount > 1000;