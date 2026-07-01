import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2 import Error
from psycopg2.extras import execute_values


HOST = "localhost"
PORT = "5432"
DATABASE = "shop_db"
USER = "postgres"
PASSWORD = "kukusik2007"

TOTAL_ORDERS = 500000
EXTRA_CUSTOMERS = 1000
BATCH_SIZE = 10000

STATUSES = (
    ["pending"] * 2 +
    ["confirmed"] * 15 +
    ["shipped"] * 25 +
    ["delivered"] * 50 +
    ["cancelled"] * 8
)

CITIES = [
    "Kyiv",
    "Lviv",
    "Odesa",
    "Kharkiv",
    "Dnipro"
]


def create_connection():
    try:
        connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DATABASE,
            user=USER,
            password=PASSWORD
        )

        print("Connected to PostgreSQL")
        return connection

    except Error as error:
        print("Connection error:", error)
        return None


def add_extra_customers(connection):
    print("Adding customers...")

    query = """
    INSERT INTO customers
    (first_name, last_name, email, phone, is_active)
    VALUES %s
    ON CONFLICT (email) DO NOTHING
    """

    data = [
        (
            f"Customer{i}",
            f"Test{i}",
            f"customer{i}@example.com",
            f"+38050{i:07}",
            True
        )
        for i in range(1, EXTRA_CUSTOMERS + 1)
    ]

    with connection.cursor() as cursor:
        execute_values(cursor, query, data)

    connection.commit()

    print("Customers added")


def create_addresses(connection):
    print("Creating addresses...")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id
            FROM customers c
            WHERE NOT EXISTS (
                SELECT 1
                FROM addresses a
                WHERE a.customer_id = c.id
            )
        """)

        customers = [row[0] for row in cursor.fetchall()]

    if not customers:
        print("All customers already have addresses")
        return

    query = """
    INSERT INTO addresses
    (customer_id, country, city, street, postal_code)
    VALUES %s
    """

    data = []

    for customer_id in customers:
        data.append(
            (
                customer_id,
                "Ukraine",
                random.choice(CITIES),
                f"Street {customer_id}",
                str(random.randint(10000, 99999))
            )
        )

    with connection.cursor() as cursor:
        execute_values(cursor, query, data)

    connection.commit()

    print(f"Inserted {len(data)} addresses")


def load_customer_address_pairs(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT ON (customer_id)
                customer_id,
                id
            FROM addresses
            ORDER BY customer_id, id
        """)

        pairs = cursor.fetchall()

    print(f"Loaded {len(pairs)} customer/address pairs")

    return pairs


def generate_orders(connection, pairs):
    print("Generating orders...")

    query = """
    INSERT INTO orders
    (
        customer_id,
        address_id,
        status,
        total_amount,
        created_at
    )
    VALUES %s
    """

    now = datetime.now()

    inserted = 0

    with connection.cursor() as cursor:

        while inserted < TOTAL_ORDERS:

            batch_size = min(
                BATCH_SIZE,
                TOTAL_ORDERS - inserted
            )

            batch = []

            for _ in range(batch_size):

                customer_id, address_id = random.choice(pairs)

                created_at = (
                    now -
                    timedelta(days=random.uniform(0, 365))
                )

                batch.append(
                    (
                        customer_id,
                        address_id,
                        random.choice(STATUSES),
                        0,
                        created_at
                    )
                )

            execute_values(
                cursor,
                query,
                batch
            )

            connection.commit()

            inserted += batch_size

            print(
                f"Inserted {inserted:,} "
                f"of {TOTAL_ORDERS:,} orders"
            )


def vacuum_analyze(connection):
    print("Running VACUUM ANALYZE...")

    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute(
            "VACUUM ANALYZE orders"
        )

    connection.autocommit = False

    print("VACUUM ANALYZE completed")


def main():

    connection = create_connection()

    if connection is None:
        return

    try:

        add_extra_customers(connection)

        create_addresses(connection)

        pairs = load_customer_address_pairs(
            connection
        )

        if not pairs:
            raise Exception(
                "No customer/address pairs found"
            )

        generate_orders(
            connection,
            pairs
        )

        vacuum_analyze(connection)

        print("Done")

    except Exception as error:

        print("Error:", error)

    finally:

        connection.close()

        print("Connection closed")


if __name__ == "__main__":
    main()

