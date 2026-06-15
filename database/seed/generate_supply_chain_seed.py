import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

CUSTOMERS = 100
WAREHOUSES = 10
PRODUCTS = 200
ORDERS = 1000

start_date = datetime(2024, 1, 1)

customer_types = ["Retail", "Wholesale", "Enterprise"]
product_categories = ["Electronics", "Furniture", "Apparel", "Food", "Automotive"]
order_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
priorities = ["Low", "Medium", "High"]
shipment_statuses = ["In Transit", "Delivered", "Delayed"]
invoice_statuses = ["Paid", "Pending", "Overdue"]
payment_statuses = ["Completed", "Pending", "Failed"]
claim_types = ["Damage", "Late Delivery", "Missing Item"]
claim_statuses = ["Open", "Closed", "Investigating"]
issue_types = ["Payment Issue", "Shipment Delay", "Wrong Product", "Damaged Product"]
ticket_statuses = ["Open", "Resolved", "In Progress"]

sql_lines = []

# Customers
for i in range(1, CUSTOMERS + 1):
    sql_lines.append(f"""
INSERT INTO customers VALUES (
{i},
'{fake.company().replace("'", "")}',
'{random.choice(customer_types)}',
'{fake.city().replace("'", "")}',
'{fake.country().replace("'", "")}',
'{fake.date_between(start_date="-2y", end_date="today")}'
);
""")

# Warehouses
for i in range(1, WAREHOUSES + 1):
    sql_lines.append(f"""
INSERT INTO warehouses VALUES (
{i},
'Warehouse_{i}',
'{fake.city().replace("'", "")}',
'{fake.country().replace("'", "")}',
{random.randint(1000, 10000)}
);
""")

# Products
for i in range(1, PRODUCTS + 1):
    sql_lines.append(f"""
INSERT INTO products VALUES (
{i},
'{fake.word().capitalize()} Product',
'{random.choice(product_categories)}',
{round(random.uniform(10, 5000), 2)}
);
""")

# Orders
for i in range(1, ORDERS + 1):

    customer_id = random.randint(1, CUSTOMERS)
    order_date = start_date + timedelta(days=random.randint(0, 500))

    sql_lines.append(f"""
INSERT INTO orders VALUES (
{i},
{customer_id},
'{order_date.date()}',
'{random.choice(order_statuses)}',
'{random.choice(priorities)}'
);
""")

# Order Items
order_item_id = 1

for order_id in range(1, ORDERS + 1):

    for _ in range(random.randint(1, 5)):

        product_id = random.randint(1, PRODUCTS)
        quantity = random.randint(1, 20)
        price = round(random.uniform(10, 5000), 2)

        sql_lines.append(f"""
INSERT INTO order_items VALUES (
{order_item_id},
{order_id},
{product_id},
{quantity},
{price}
);
""")

        order_item_id += 1

# Shipments
for i in range(1, ORDERS + 1):

    shipment_date = start_date + timedelta(days=random.randint(0, 500))
    expected_date = shipment_date + timedelta(days=random.randint(2, 10))
    actual_date = expected_date + timedelta(days=random.randint(-1, 5))

    sql_lines.append(f"""
INSERT INTO shipments VALUES (
{i},
{i},
{random.randint(1, WAREHOUSES)},
'{shipment_date.date()}',
'{expected_date.date()}',
'{actual_date.date()}',
'{fake.company().replace("'", "")}',
'{random.choice(shipment_statuses)}'
);
""")

# Invoices
for i in range(1, ORDERS + 1):

    amount = round(random.uniform(100, 20000), 2)

    sql_lines.append(f"""
INSERT INTO invoices VALUES (
{i},
{i},
'{fake.date_between(start_date="-1y", end_date="today")}',
{amount},
'{random.choice(invoice_statuses)}'
);
""")

# Payments
for i in range(1, 801):

    amount = round(random.uniform(100, 20000), 2)

    sql_lines.append(f"""
INSERT INTO payments VALUES (
{i},
{random.randint(1, ORDERS)},
'{fake.date_between(start_date="-1y", end_date="today")}',
{amount},
'{random.choice(payment_statuses)}'
);
""")

# Claims
for i in range(1, 301):

    sql_lines.append(f"""
INSERT INTO claims VALUES (
{i},
{random.randint(1, ORDERS)},
{random.randint(1, CUSTOMERS)},
'{fake.date_between(start_date="-1y", end_date="today")}',
'{random.choice(claim_types)}',
{round(random.uniform(50, 5000), 2)},
'{random.choice(claim_statuses)}'
);
""")

# Support Tickets
for i in range(1, 501):

    sql_lines.append(f"""
INSERT INTO support_tickets VALUES (
{i},
{random.randint(1, CUSTOMERS)},
{random.randint(1, ORDERS)},
'{fake.date_between(start_date="-1y", end_date="today")}',
'{random.choice(issue_types)}',
'{random.choice(priorities)}',
'{random.choice(ticket_statuses)}'
);
""")

with open("database/migrations/002_seed_supply_chain_data.sql", "w", encoding="utf-8") as f:
    f.writelines(sql_lines)

print("Seed SQL file generated successfully.")