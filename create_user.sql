DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'shop_readonly') THEN
        CREATE ROLE shop_readonly LOGIN PASSWORD 'readonly123';
    END IF;
END $$;

GRANT CONNECT ON DATABASE shop_db TO shop_readonly;
GRANT USAGE ON SCHEMA public TO shop_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO shop_readonly;



DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'shop_manager') THEN
        CREATE ROLE shop_manager LOGIN PASSWORD 'manager123';
    END IF;
END $$;

GRANT CONNECT ON DATABASE shop_db TO shop_manager;
GRANT USAGE ON SCHEMA public TO shop_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO shop_manager;
GRANT INSERT, UPDATE ON orders TO shop_manager;
GRANT INSERT, UPDATE ON order_items TO shop_manager;
GRANT INSERT, UPDATE ON payments TO shop_manager;


DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'shop_app') THEN
        CREATE ROLE shop_app LOGIN PASSWORD 'shopapp123';
    END IF;
END $$;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO shop_manager;
GRANT CONNECT ON DATABASE shop_db TO shop_app;
GRANT USAGE ON SCHEMA public TO shop_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO shop_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO shop_app;