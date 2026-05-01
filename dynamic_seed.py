"""
dynamic_seed.py — Run this to load LIVE sample data
Generates sales relative to TODAY so dashboard always shows real numbers.

Usage:
    python dynamic_seed.py

What it creates:
    - 32 products across 8 categories
    - 10 registered customers
    - 5 coupons
    - 30 days of past sales history
    - 6 sales TODAY (shows on dashboard)
    - Low stock alerts (medicine items)
    - 2 returns (1 pending, 1 approved)
    - Activity log entries
"""

import pymysql
pymysql.install_as_MySQLdb()

import os, random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

# ── Connect ───────────────────────────────────────────────
conn = pymysql.connect(
    host   = os.getenv('MYSQL_HOST', 'localhost'),
    user   = os.getenv('MYSQL_USER', 'root'),
    passwd = os.getenv('MYSQL_PASSWORD', ''),
    db     = os.getenv('MYSQL_DB', 'billing_system'),
    port   = int(os.getenv('MYSQL_PORT', 3306)),
    charset= 'utf8mb4',
    autocommit=False
)
cur = conn.cursor()

def run(sql, params=None):
    cur.execute(sql, params or ())

def runmany(sql, data):
    cur.executemany(sql, data)

print("\n🔄 Loading dynamic sample data...\n")

# ══════════════════════════════════════════════════════════
# 1. RESET all tables
# ══════════════════════════════════════════════════════════
print("  → Clearing old data...")
run("SET FOREIGN_KEY_CHECKS=0")
for tbl in ['login_attempts','activity_log','stock_adjustments','returns',
            'sale_items','sales','coupons','customers',
            'products','categories','settings','users']:
    run(f"TRUNCATE TABLE {tbl}")
run("SET FOREIGN_KEY_CHECKS=1")

# ══════════════════════════════════════════════════════════
# 2. SETTINGS
# ══════════════════════════════════════════════════════════
print("  → Settings...")
settings = [
    ('shop_name',     'ShopEase — General Store'),
    ('shop_address',  'Main Market, Sector 5, Shimla, HP 171001'),
    ('shop_phone',    '9876543210'),
    ('shop_email',    'shopease@example.com'),
    ('shop_gstin',    '02AABCS1429B1Z5'),
    ('currency',      '₹'),
    ('app_version',   '1.0.0'),
    ('return_days',   '7'),
    ('invoice_prefix','INV'),
]
runmany("INSERT INTO settings (setting_key, setting_value) VALUES (%s,%s)", settings)

# ══════════════════════════════════════════════════════════
# 3. USERS
# ══════════════════════════════════════════════════════════
print("  → Users...")
users = [
    ('Administrator', 'admin',    'admin@123',    'admin'),
    ('Ravi Sharma',   'manager',  'manager@123',  'manager'),
    ('Priya Mehta',   'cashier',  'cashier@123',  'cashier'),
    ('Amit Verma',    'cashier2', 'cashier@123',  'cashier'),
]
runmany("""
    INSERT INTO users (full_name, username, password, role, last_login)
    VALUES (%s,%s,%s,%s, NOW())
""", [(n, u, generate_password_hash(p), r) for n,u,p,r in users])

# ══════════════════════════════════════════════════════════
# 4. CATEGORIES
# ══════════════════════════════════════════════════════════
print("  → Categories...")
categories = [
    ('Grocery',      'Daily food and household items'),
    ('Beverages',    'Drinks, juices, water, soft drinks'),
    ('Dairy',        'Milk, cheese, butter, curd'),
    ('Snacks',       'Chips, biscuits, namkeen, chocolates'),
    ('Personal Care','Soap, shampoo, toothpaste, skincare'),
    ('Stationery',   'Pens, notebooks, files, tapes'),
    ('Electronics',  'Batteries, bulbs, wires, adapters'),
    ('Medicine',     'OTC medicines and health products'),
]
runmany("INSERT INTO categories (name, description) VALUES (%s,%s)", categories)

# get category ids
cur.execute("SELECT category_id, name FROM categories")
cat_map = {r[1]: r[0] for r in cur.fetchall()}

# ══════════════════════════════════════════════════════════
# 5. PRODUCTS
# ══════════════════════════════════════════════════════════
print("  → Products...")
# (name, category, brand, barcode, buy_price, sell_price, gst%, unit, stock, reorder)
products_data = [
    # Grocery
    ('Aashirvaad Atta 5kg',      'Grocery',      'ITC',       'BAR001', 190, 235, 0,  'bag', 42, 10),
    ('Fortune Sunflower Oil 1L', 'Grocery',      'Fortune',   'BAR002', 120, 148, 5,  'btl', 28,  8),
    ('India Gate Basmati 1kg',   'Grocery',      'KRBL',      'BAR003',  88, 110, 0,  'pkt', 35, 10),
    ('Tata Salt 1kg',            'Grocery',      'Tata',      'BAR004',  20,  26, 0,  'pkt', 60, 15),
    ('Surf Excel 1kg',           'Grocery',      'HUL',       'BAR005', 188, 230, 18, 'pkt', 22,  8),
    ('Ariel Detergent 500g',     'Grocery',      'P&G',       'BAR006',  95, 120, 18, 'pkt', 18,  5),
    # Beverages
    ('Coca-Cola 2L',             'Beverages',    'Coca-Cola', 'BAR007',  72,  90, 12, 'btl', 30, 10),
    ('Pepsi 1.5L',               'Beverages',    'PepsiCo',   'BAR008',  58,  75, 12, 'btl', 25, 10),
    ('Real Mango Juice 1L',      'Beverages',    'Dabur',     'BAR009',  78,  95, 12, 'btl', 20,  8),
    ('Bisleri Water 1L',         'Beverages',    'Bisleri',   'BAR010',  10,  20, 18, 'btl', 80, 20),
    ('Red Bull 250ml',           'Beverages',    'Red Bull',  'BAR011', 100, 130, 28, 'can', 15,  5),
    # Dairy
    ('Amul Full Cream Milk 1L',  'Dairy',        'Amul',      'BAR012',  56,  68, 0,  'pkt', 50, 15),
    ('Amul Butter 100g',         'Dairy',        'Amul',      'BAR013',  50,  60, 12, 'pkt', 30, 10),
    ('Nestle Dahi 400g',         'Dairy',        'Nestle',    'BAR014',  38,  48, 5,  'pkt', 22,  8),
    ('Amul Cheese Slice 200g',   'Dairy',        'Amul',      'BAR015',  88, 110, 12, 'pkt', 12,  5),
    # Snacks
    ('Lays Classic 52g',         'Snacks',       'PepsiCo',   'BAR016',  18,  25, 12, 'pkt', 48, 15),
    ('Kurkure Masala 80g',       'Snacks',       'PepsiCo',   'BAR017',  20,  28, 12, 'pkt', 40, 15),
    ('Parle-G 250g',             'Snacks',       'Parle',     'BAR018',  18,  22, 18, 'pkt', 55, 15),
    ('Cadbury Dairy Milk 35g',   'Snacks',       'Mondelez',  'BAR019',  28,  40, 18, 'bar', 60, 20),
    ('Haldiram Bhujia 200g',     'Snacks',       'Haldiram',  'BAR020',  48,  60, 12, 'pkt', 35, 10),
    # Personal Care
    ('Dove Soap 100g',           'Personal Care','HUL',       'BAR021',  35,  48, 18, 'bar', 40, 10),
    ('Pantene Shampoo 340ml',    'Personal Care','P&G',       'BAR022', 175, 220, 18, 'btl', 15,  5),
    ('Colgate 200g',             'Personal Care','Colgate',   'BAR023',  75,  95, 18, 'tube',25,  8),
    ('Nivea Cream 100ml',        'Personal Care','Nivea',     'BAR024', 110, 145, 18, 'jar', 12,  5),
    # Stationery
    ('Reynolds Pen (10pc)',      'Stationery',   'Reynolds',  'BAR025',  55,  75, 12, 'box', 20,  5),
    ('Classmate Notebook 200pg', 'Stationery',   'ITC',       'BAR026',  55,  70, 12, 'pcs', 30,  8),
    ('Scotch Tape 1inch',        'Stationery',   '3M',        'BAR027',  28,  40, 18, 'roll',15,  5),
    # Electronics
    ('Duracell AA Battery 4pc',  'Electronics',  'Duracell',  'BAR028',  90, 120, 28, 'pkt', 18,  5),
    ('Syska LED Bulb 9W',        'Electronics',  'Syska',     'BAR029',  58,  80, 12, 'pcs', 10,  3),
    # Medicine — LOW STOCK intentionally
    ('Dolo 650 Strip',           'Medicine',     'Micro Labs','BAR030',  28,  36, 12, 'strip', 4, 10),
    ('Crocin 500mg Strip',       'Medicine',     'GSK',       'BAR031',  24,  32, 12, 'strip', 3, 10),
    ('ORS Sachet (10pc)',        'Medicine',     'Electral',  'BAR032',  38,  50, 12, 'pkt',   8,  5),
]
for name, cat, brand, barcode, buy, sell, gst, unit, stock, reorder in products_data:
    run("""
        INSERT INTO products
        (name,category_id,brand,barcode,purchase_price,selling_price,gst_percent,unit,stock_qty,reorder_level)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (name, cat_map[cat], brand, barcode, buy, sell, gst, unit, stock, reorder))

# get product ids
cur.execute("SELECT product_id, barcode, selling_price, gst_percent FROM products")
prod_rows = cur.fetchall()
prod_map  = {r[0]: {'price': float(r[2]), 'gst': float(r[3])} for r in prod_rows}
barcode_to_id = {r[1]: r[0] for r in prod_rows}

# ══════════════════════════════════════════════════════════
# 6. CUSTOMERS
# ══════════════════════════════════════════════════════════
print("  → Customers...")
customers = [
    ('Rahul Gupta',   '9811223344', 'rahul@example.com',  'House 12, Sector 3, Shimla', 2000),
    ('Sunita Devi',   '9822334455', 'sunita@example.com', 'Village Rampur, Shimla',     1000),
    ('Vikas Thakur',  '9833445566', 'vikas@example.com',  'Near Bus Stand, Solan',      3000),
    ('Meera Sharma',  '9844556677', 'meera@example.com',  'Flat 5B, New Colony, Shimla',1500),
    ('Rajan Kapoor',  '9855667788', 'rajan@example.com',  '14 Mall Road, Shimla',       5000),
    ('Anjali Singh',  '9866778899', 'anjali@example.com', 'Lakkar Bazaar, Shimla',      2000),
    ('Deepak Rawat',  '9877889900', 'deepak@example.com', 'Village Koti, Rampur',          0),
    ('Pooja Chauhan', '9888990011', 'pooja@example.com',  'Near Church, Shimla',        1000),
    ('Suresh Kumar',  '9899001122', None,                 'Sanjauli, Shimla',           2500),
    ('Nisha Verma',   '9800112233', None,                 'Chhota Shimla, HP',          1500),
]
runmany("""
    INSERT INTO customers (name, phone, email, address, credit_limit)
    VALUES (%s,%s,%s,%s,%s)
""", customers)

cur.execute("SELECT customer_id FROM customers ORDER BY customer_id")
cust_ids = [r[0] for r in cur.fetchall()]

# ══════════════════════════════════════════════════════════
# 7. COUPONS
# ══════════════════════════════════════════════════════════
print("  → Coupons...")
today = datetime.now().date()
coupons = [
    ('WELCOME10', 'percent', 10,  200,  50, today + timedelta(days=30)),
    ('FLAT50',    'fixed',   50,  500,  20, today + timedelta(days=15)),
    ('SAVE20PCT', 'percent', 20, 1000,  10, today + timedelta(days=7)),
    ('DIWALI100', 'fixed',  100,  800,  30, today + timedelta(days=60)),
    ('NEWCUST15', 'percent', 15,  300,  25, today + timedelta(days=45)),
]
runmany("""
    INSERT INTO coupons (code,discount_type,discount_value,min_order,max_uses,expiry_date)
    VALUES (%s,%s,%s,%s,%s,%s)
""", coupons)

# ══════════════════════════════════════════════════════════
# 8. SALES — past 30 days + TODAY
# ══════════════════════════════════════════════════════════
print("  → Generating sales history (30 days + today)...")

# Helper: calculate line totals
def make_item(sale_id, prod_id, qty):
    p     = prod_map[prod_id]
    price = p['price']
    gst_p = p['gst']
    gst_a = round((price * qty * gst_p) / 100, 2)
    total = round(price * qty + gst_a, 2)
    return (sale_id, prod_id, qty, price, gst_p, gst_a, total)

# cashier user_id = 3 (Priya)
CASHIER_ID = 3

invoice_num = 1
all_items   = []

def insert_sale(dt, customer_id, payment_mode, product_qty_list, discount=0):
    global invoice_num
    inv = f"INV-2024-{invoice_num:04d}"
    invoice_num += 1

    subtotal  = sum(prod_map[pid]['price'] * qty for pid, qty in product_qty_list)
    total_gst = sum(round((prod_map[pid]['price'] * qty * prod_map[pid]['gst']) / 100, 2)
                    for pid, qty in product_qty_list)
    grand     = round(subtotal + total_gst - discount, 2)
    status    = 'unpaid' if payment_mode == 'credit' else 'paid'

    run("""
        INSERT INTO sales
        (invoice_number,customer_id,cashier_id,sale_date,
         subtotal,total_gst,discount_amount,grand_total,payment_mode,payment_status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (inv, customer_id, CASHIER_ID, dt,
          round(subtotal,2), round(total_gst,2), discount, grand,
          payment_mode, status))

    cur.execute("SELECT LAST_INSERT_ID()")
    sale_id = cur.fetchone()[0]

    for pid, qty in product_qty_list:
        all_items.append(make_item(sale_id, pid, qty))

    return sale_id

# ── Product ID shortcuts ──────────────────────────────────
P = barcode_to_id  # P['BAR001'] = product_id

# ── 30 days of history ───────────────────────────────────
now = datetime.now()

# Day -28
d = now - timedelta(days=28)
insert_sale(d.replace(hour=10,minute=15), cust_ids[0], 'cash',
            [(P['BAR001'],1),(P['BAR012'],2),(P['BAR016'],2),(P['BAR018'],1)])
insert_sale(d.replace(hour=14,minute=30), None, 'upi',
            [(P['BAR007'],1),(P['BAR010'],4),(P['BAR019'],1)])

# Day -25
d = now - timedelta(days=25)
insert_sale(d.replace(hour=9,minute=20), cust_ids[1], 'cash',
            [(P['BAR002'],2),(P['BAR013'],2),(P['BAR022'],1)])
insert_sale(d.replace(hour=16,minute=45), cust_ids[2], 'card',
            [(P['BAR001'],2),(P['BAR005'],2),(P['BAR003'],2),(P['BAR012'],4)], discount=50)

# Day -22
d = now - timedelta(days=22)
insert_sale(d.replace(hour=11,minute=0), None, 'cash',
            [(P['BAR017'],3),(P['BAR018'],2),(P['BAR019'],3),(P['BAR010'],3)])
insert_sale(d.replace(hour=13,minute=30), cust_ids[3], 'upi',
            [(P['BAR021'],3),(P['BAR023'],2),(P['BAR024'],1)])
insert_sale(d.replace(hour=17,minute=20), cust_ids[4], 'card',
            [(P['BAR028'],2),(P['BAR029'],5),(P['BAR006'],3),(P['BAR005'],2),(P['BAR002'],2)], discount=100)

# Day -18
d = now - timedelta(days=18)
insert_sale(d.replace(hour=10,minute=40), cust_ids[5], 'cash',
            [(P['BAR001'],1),(P['BAR012'],3),(P['BAR014'],2),(P['BAR020'],2)])
insert_sale(d.replace(hour=15,minute=10), None, 'upi',
            [(P['BAR030'],2),(P['BAR032'],1),(P['BAR010'],2)])

# Day -14
d = now - timedelta(days=14)
insert_sale(d.replace(hour=9,minute=55), cust_ids[6], 'cash',
            [(P['BAR003'],3),(P['BAR002'],2),(P['BAR013'],2),(P['BAR004'],3),(P['BAR012'],1)])
insert_sale(d.replace(hour=12,minute=20), cust_ids[7], 'upi',
            [(P['BAR022'],1),(P['BAR021'],2),(P['BAR019'],1)])
insert_sale(d.replace(hour=16,minute=0), cust_ids[8], 'credit',
            [(P['BAR005'],3),(P['BAR006'],2),(P['BAR001'],2),(P['BAR002'],2)])

# Day -10
d = now - timedelta(days=10)
insert_sale(d.replace(hour=10,minute=30), cust_ids[0], 'cash',
            [(P['BAR007'],2),(P['BAR008'],2),(P['BAR009'],2)])
insert_sale(d.replace(hour=14,minute=0), None, 'upi',
            [(P['BAR016'],4),(P['BAR017'],3),(P['BAR018'],2),(P['BAR019'],1)])
insert_sale(d.replace(hour=17,minute=30), cust_ids[9], 'card',
            [(P['BAR025'],2),(P['BAR026'],4),(P['BAR027'],3),(P['BAR028'],1),(P['BAR010'],2)])

# Day -7
d = now - timedelta(days=7)
insert_sale(d.replace(hour=9,minute=10), cust_ids[1], 'cash',
            [(P['BAR015'],2),(P['BAR012'],3),(P['BAR014'],3),(P['BAR013'],2)])
insert_sale(d.replace(hour=13,minute=45), cust_ids[2], 'card',
            [(P['BAR001'],2),(P['BAR002'],3),(P['BAR005'],1),(P['BAR004'],2)], discount=100)
insert_sale(d.replace(hour=16,minute=20), None, 'upi',
            [(P['BAR030'],1),(P['BAR031'],2),(P['BAR010'],2),(P['BAR019'],1)])

# Day -4
d = now - timedelta(days=4)
insert_sale(d.replace(hour=10,minute=0), cust_ids[3], 'cash',
            [(P['BAR022'],1),(P['BAR023'],2),(P['BAR024'],1),(P['BAR021'],1)])
insert_sale(d.replace(hour=14,minute=30), cust_ids[4], 'card',
            [(P['BAR029'],8),(P['BAR028'],5),(P['BAR006'],4),(P['BAR005'],2),(P['BAR002'],2)], discount=200)
insert_sale(d.replace(hour=17,minute=0), None, 'upi',
            [(P['BAR016'],5),(P['BAR017'],3),(P['BAR011'],2)])

# Day -2
d = now - timedelta(days=2)
insert_sale(d.replace(hour=11,minute=15), cust_ids[5], 'cash',
            [(P['BAR003'],2),(P['BAR012'],2),(P['BAR014'],2),(P['BAR020'],1)])
insert_sale(d.replace(hour=15,minute=40), cust_ids[6], 'upi',
            [(P['BAR001'],1),(P['BAR013'],2),(P['BAR007'],2),(P['BAR016'],4),(P['BAR019'],2)])

# Day -1 (Yesterday)
d = now - timedelta(days=1)
insert_sale(d.replace(hour=9,minute=30), cust_ids[7], 'cash',
            [(P['BAR012'],4),(P['BAR004'],2),(P['BAR018'],3),(P['BAR019'],2)])
insert_sale(d.replace(hour=13,minute=0), cust_ids[0], 'upi',
            [(P['BAR022'],1),(P['BAR021'],2),(P['BAR023'],1),(P['BAR010'],3)])
insert_sale(d.replace(hour=16,minute=30), None, 'cash',
            [(P['BAR007'],3),(P['BAR008'],2),(P['BAR011'],1),(P['BAR016'],2)])

# ── TODAY'S SALES (these show on dashboard) ───────────────
print("  → Generating TODAY's sales...")

today_times = [
    now.replace(hour=8,  minute=45, second=0),
    now.replace(hour=10, minute=20, second=0),
    now.replace(hour=11, minute=55, second=0),
    now.replace(hour=13, minute=10, second=0),
    now.replace(hour=14, minute=30, second=0),
    now.replace(hour=16, minute=0,  second=0),
]
# Only use times that have already passed
today_times = [t for t in today_times if t <= now]

today_sales_data = [
    (cust_ids[0], 'cash',  [(P['BAR001'],1),(P['BAR012'],2),(P['BAR016'],3),(P['BAR019'],2)],  0),
    (cust_ids[7], 'upi',   [(P['BAR022'],1),(P['BAR021'],2),(P['BAR010'],3)],                  0),
    (None,        'upi',   [(P['BAR030'],1),(P['BAR010'],2),(P['BAR019'],2)],                  0),
    (cust_ids[1], 'card',  [(P['BAR005'],2),(P['BAR006'],2),(P['BAR002'],2),(P['BAR004'],2)],  50),
    (None,        'cash',  [(P['BAR007'],2),(P['BAR008'],1),(P['BAR011'],1)],                  0),
    (cust_ids[4], 'card',  [(P['BAR028'],2),(P['BAR029'],3),(P['BAR025'],2),(P['BAR026'],2)],  0),
]

for i, t in enumerate(today_times):
    if i < len(today_sales_data):
        cid, mode, items, disc = today_sales_data[i]
        insert_sale(t, cid, mode, items, discount=disc)

# ── Bulk insert all sale_items ────────────────────────────
print(f"  → Inserting {len(all_items)} sale line items...")
runmany("""
    INSERT INTO sale_items
    (sale_id, product_id, qty, unit_price, gst_percent, gst_amount, line_total)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
""", all_items)

# ══════════════════════════════════════════════════════════
# 9. RETURNS
# ══════════════════════════════════════════════════════════
print("  → Returns...")
cur.execute("SELECT sale_id FROM sales ORDER BY sale_id LIMIT 5")
sale_ids = [r[0] for r in cur.fetchall()]

runmany("""
    INSERT INTO returns
    (original_sale_id,product_id,product_name,return_qty,return_reason,
     refund_amount,refund_mode,status,approved_by,return_date)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
""", [
    (sale_ids[4] if len(sale_ids)>4 else 1,
     P['BAR017'],'Kurkure Masala 80g',1,
     'Packet was damaged / torn',28.00,'cash','approved',2,
     now - timedelta(days=20)),
    (sale_ids[2] if len(sale_ids)>2 else 1,
     P['BAR005'],'Surf Excel 1kg',1,
     'Customer bought wrong variant',230.00,'credit','pending',None,
     now - timedelta(days=12)),
])

# ══════════════════════════════════════════════════════════
# 10. STOCK ADJUSTMENTS
# ══════════════════════════════════════════════════════════
print("  → Stock adjustments...")
runmany("""
    INSERT INTO stock_adjustments
    (product_id,old_qty,new_qty,reason,adjusted_by,created_at)
    VALUES (%s,%s,%s,%s,%s,%s)
""", [
    (P['BAR030'],10,4,'Physical count mismatch — 6 strips missing',2, now-timedelta(days=5)),
    (P['BAR031'],8, 3,'Expiry check — 5 strips near expiry removed',2, now-timedelta(days=3)),
    (P['BAR029'],15,10,'Sold 5 units manually (offline transaction)',2, now-timedelta(days=8)),
])

# ══════════════════════════════════════════════════════════
# 11. ACTIVITY LOG
# ══════════════════════════════════════════════════════════
print("  → Activity log...")
runmany("""
    INSERT INTO activity_log (user_id,action,ip_address,created_at)
    VALUES (%s,%s,%s,%s)
""", [
    (1,'LOGIN','127.0.0.1',                    now - timedelta(hours=2)),
    (3,'LOGIN','127.0.0.1',                    now - timedelta(hours=3)),
    (3,'NEW_SALE:INV-2024-0001','127.0.0.1',   now - timedelta(hours=2, minutes=30)),
    (3,'NEW_SALE:INV-2024-0002','127.0.0.1',   now - timedelta(hours=1, minutes=45)),
    (2,'STOCK_ADJUST:Dolo 650','127.0.0.1',    now - timedelta(days=5)),
    (2,'LOGIN','127.0.0.1',                    now - timedelta(days=1)),
    (3,'NEW_SALE:INV-2024-0003','127.0.0.1',   now - timedelta(minutes=45)),
])

# ══════════════════════════════════════════════════════════
# COMMIT & SUMMARY
# ══════════════════════════════════════════════════════════
conn.commit()
cur.close()
conn.close()

print("\n" + "="*45)
print("  ✅  Dynamic sample data loaded!")
print("="*45)
print(f"  Products   : {len(products_data)}")
print(f"  Customers  : {len(customers)}")
print(f"  Total sales: {invoice_num - 1}")
print(f"  Today sales: {len(today_times)}")
print(f"  Sale items : {len(all_items)}")
print("="*45)
print("\n  Login credentials:")
print("  admin    / admin@123")
print("  manager  / manager@123")
print("  cashier  / cashier@123")
print("\n  Open: http://localhost:5000\n")
