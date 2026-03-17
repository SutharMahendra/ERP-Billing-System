import sqlite3

conn = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()
conn.execute("PRAGMA foreign_keys = ON")

# =========================
# ACCOUNT (USER)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS account (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    password TEXT NOT NULL,
    remark TEXT
)
""")

# =========================
# SELLER (SUPPLIER)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS seller (
    seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_company_name TEXT,
    seller_name TEXT NOT NULL,
    seller_phone_no TEXT NOT NULL,
    seller_email TEXT,
    seller_address TEXT NOT NULL,
    seller_city TEXT,
    seller_gst_number TEXT,
    remark TEXT
)
""")

# =========================
# BUYER (CUSTOMER)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS buyer (
    buyer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_company_name TEXT,
    buyer_name TEXT NOT NULL,
    buyer_phone_no TEXT NOT NULL,
    buyer_email TEXT,
    buyer_address TEXT NOT NULL,
    buyer_city TEXT,
    buyer_gst_number TEXT,
    remark TEXT
)
""")

# =========================
# PRODUCT
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_name TEXT,
    company_name TEXT,
    hsn_code TEXT,
    product_name TEXT NOT NULL,
    product_price REAL NOT NULL,
    product_gst_rate INTEGER,
    primary_unit TEXT,
    product_category TEXT,
    remark TEXT
)
""")

# =========================
# SELL (ONE ROW = ONE PRODUCT SOLD)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS sell (
    sell_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT,
    buyer_id INTEGER,
    user_id INTEGER,
    sell_date TEXT,
    product_id INTEGER,
    product_quantity REAL,
    product_price REAL,
    product_gst_rate INTEGER,
    gst_amount REAL,
    total_amount REAL,
    payment_term TEXT,
    remark TEXT,
               
    FOREIGN KEY (buyer_id) REFERENCES buyer(buyer_id),
    FOREIGN KEY (user_id) REFERENCES account(user_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    
)
""")

# =========================
# PURCHASE (ONE ROW = ONE PRODUCT PURCHASED)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchase (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT,
    seller_id INTEGER,
    user_id INTEGER,
    purchase_date TEXT,
    product_id INTEGER,
    product_quantity REAL,
    product_price REAL,
    product_gst_rate INTEGER,
    gst_amount REAL,
    total_amount REAL,
    remark TEXT,
               
    FOREIGN KEY (seller_id) REFERENCES seller(seller_id),
    FOREIGN KEY (user_id) REFERENCES account(user_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
)
""")

# =========================
# PAYMENT (MONEY PAID TO SELLER)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS payment (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER,
    bill_number TEXT,
    payment_type TEXT,
    payment_status TEXT,
    amount REAL,
    payment_date TEXT,
    remark TEXT,
               
    FOREIGN KEY (purchase_id) REFERENCES purchase(purchase_id)
)
""")

# =========================
# RECEIVE (MONEY RECEIVED FROM BUYER)
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS receive (
    receive_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sell_id INTEGER,
    bill_number TEXT,
    receive_type TEXT,
    receive_status TEXT,
    amount REAL,
    receive_date TEXT,
    remark TEXT,
               
    FOREIGN KEY (sell_id) REFERENCES sell(sell_id)
)
""")


conn.commit()
conn.close()

print("✅ ERP Billing Database Created Successfully")
