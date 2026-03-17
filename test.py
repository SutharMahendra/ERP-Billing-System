import tkinter as tk 
import sqlite3 
from tkinter import ttk
from tkinter import scrolledtext
import dashboard
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy
import pandas as pd 
from rapidfuzz import process
import re


conn = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()


training_questions = [
    # ---- Product count ----
    "how many products are there",
    "total products",
    "count products",
    "number of products",
    
    # ---- Product list ----
    "list products",
    "show all products", 
    "display product list",
    "what products are available",
    
    # ---- Search product ----
    "find product surf",
    "search product biscuit",
    "is there product lux soap",
    "check product colgate",
    
    # ---- Total purchase ----
    "total purchased quantity",
    "sum of purchased quantity",
    "how many items purchased",
    "total purchase stock",
    
    # ---- Total sell ----
    "total sold quantity",
    "sum of sold items",
    "how many items sold",
    "total sell stock",
    
    # ---- Total stock ----
    "total stock",
    "sum of stock",
    "total inventory",
    "available stock",
    
    # ---- Maximum purchase ----
    "maximum purchase quantity",
    "product with highest purchase",
    "max purchase",
    "most purchased product",
    
    # ---- Maximum sell ----
    "maximum sell quantity",
    "product with highest sell",
    "max sell",
    "most sold product",
    
    # ---- Maximum stock ----
    "maximum stock quantity",
    "product with highest stock",
    "max stock",
    "highest inventory",
    
    # ---- Minimum purchase ----
    "minimum purchase quantity",
    "lowest purchase",
    "min purchase",
    "least purchased product",
    
    # ---- Minimum sell ----
    "minimum sell quantity",
    "lowest sell",
    "min sell",
    "least sold product",
    
    # ---- Minimum stock ----
    "minimum stock quantity",
    "lowest stock",
    "min stock",
    "least inventory"
    # ---- Find Purchase Quantity ----
    "find product with purchase quantity 0",
    "which product has purchase quantity 200",
    "is there a product with purchase quantity 300",
    "show product with purchase quantity 400",
    "find product with total purchase 500",
    "product with purchase quantity 0",
    "product having purchase quantity 700",
    "which item has 800 purchase quantity",
    "show item with purchase quantity 900",
    "find item with total purchase quantity 0",
    "is any product purchased 300 times",
    "which product purchased 200 quantity",
    "product purchased quantity 400",
    "show product whose purchase quantity is 500",
    # ---- Find Sell Quantity ----
    "find product with sell quantity 0",
    "which product has sell quantity 200",
    "is there a product with sell quantity 300",
    "show product with sell quantity 400",
    "find product with total sell 500",
    "product with sell quantity 0",
    "product having sell quantity 700",
    "which item has 800 sell quantity",
    "show item with sell quantity 900",
    "find item with total sell quantity 0",
    "is any product sold 300 times",
    "which product sold 200 quantity",
    "product sold quantity 400",
    "show product whose sell quantity is 500",
    # ---- Find Stock Quantity ----
    "find product with stock quantity 0",
    "which product has stock quantity 200",
    "is there a product with stock quantity 300",
    "show product with stock quantity 400",
    "find product with total stock 500",
    "product with stock quantity 0",
    "product having stock quantity 700",
    "which item has 800 stock quantity",
    "show item with stock quantity 900",
    "find item with total stock quantity 0",
    "is any product stocked 300 times",
    "which product stocked 200 quantity",
    "product stocked quantity 400",
    "show product whose stock quantity is 500",
    
    # ---- Low Stock Calculation ----
    "which products have low stock",
    "show low stock products",
    "products with very low inventory",
    "which items are running out of stock",
    "show products with small stock quantity",
    "which product needs restocking",
    "products that need restock",
    "show products with stock less than 50"
]

training_labels = [
    "count","count","count","count",
    "list","list","list","list",
    "search_product","search_product","search_product","search_product",
    "total_purchase","total_purchase","total_purchase","total_purchase",
    "total_sell","total_sell","total_sell","total_sell",
    "total_stock","total_stock","total_stock","total_stock",
    "max_purchase","max_purchase","max_purchase","max_purchase",
    "max_sell","max_sell","max_sell","max_sell",
    "max_stock","max_stock","max_stock","max_stock",
    "min_purchase","min_purchase","min_purchase","min_purchase",
    "min_sell","min_sell","min_sell","min_sell",
    "min_stock","min_stock","min_stock","min_stock",
    "find_purchase","find_purchase","find_purchase","find_purchase","find_purchase","find_purchase","find_purchase",
    "find_purchase","find_purchase","find_purchase","find_purchase","find_purchase","find_purchase","find_purchase",
    "find_sell","find_sell","find_sell","find_sell","find_sell","find_sell","find_sell",
    "find_sell","find_sell","find_sell","find_sell","find_sell","find_sell","find_sell",
    "find_stock","find_stock","find_stock","find_stock","find_stock","find_stock","find_stock",
    "find_stock","find_stock","find_stock","find_stock","find_stock","find_stock","find_stock",
    "low_stock","low_stock","low_stock","low_stock","low_stock","low_stock","low_stock",
]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(training_questions)
model = LogisticRegression()
model.fit(X, training_labels)

    # ---------- Chatbot response ----------
def chatbot_response():
    # ---- store data in dataframe ----
    df = pd.read_sql_query("""
        SELECT 
                pro.product_id,
                pro.product_name,
               IFNULL(SUM(pur.product_quantity),0) AS total_purchase,
                IFNULL(SUM(s.product_quantity),0) AS total_sell,
                IFNULL(SUM(pur.product_quantity),0) - IFNULL(SUM(s.product_quantity),0) AS current_stock
            FROM product pro
            LEFT JOIN purchase pur 
            ON pro.product_id = pur.product_id
            LEFT JOIN sell s 
            ON pro.product_id = s.product_id
            GROUP BY pro.product_id, pro.product_name;
    """,conn)
    # ---- Take user input ----
    user_input = entry_chat.get().lower()
    entry_chat.delete(0,tk.END)
    X_test = vectorizer.transform([user_input])
    prediction = model.predict(X_test)[0]
    response = "Sorry, I didn't understand the question."
    # ---- Count Prediction ----
    if prediction == "count":
        total_product = len(df)
        response = f"Total products: {total_product}"
    # ---- List Prediction ----
    if prediction == "list":
        names = df["product_name"].tolist()
        response = "Products:\n"
        for i, name in enumerate(names, start=1):
            response += f"{i}. {name}\n"
    # ---- Search product name Prediction ----
    if prediction == "search_product":
        product_names = df["product_name"].tolist()
        match_name = process.extractOne(user_input, product_names)
    
        if match_name:
            product = match_name[0]
            row = df[df["product_name"] == product].iloc[0]
            response = f"{row['product_name']} stock: {row['current_stock']}"
        else:
            response = "Product is not found!!"
    # ---- Total Purchase Prediction ----
    if prediction == "total_purchase":
        total = df["total_purchase"].sum()
        response = f"Total purchased quantity: {total}"
    # ---- Total Sell Prediction ----
    elif prediction == "total_sell":
        total = df["total_sell"].sum()
        response = f"Total Sold quantity: {total}"
    # ---- Total stock Prediction ----
    elif prediction == "total_stock":
        total = df["current_stock"].sum()
        response = f"Total Stock quantity: {total}"
    # ---- Maxi of purchase Prediction ----
    elif prediction == "max_purchase":
        max_product = df.loc[df["total_purchase"].idxmax()]
        response = f"Highest Purchased product: {max_product["product_name"]} ({max_product["total_purchase"]})"
    # ---- Maxi of sell Prediction ----
    elif prediction == "max_sell":
        max_product = df.loc[df["total_sell"].idxmax()]
        response = f"Highest Sold product: {max_product["product_name"]} ({max_product["total_sell"]})"
    # ---- Maxi of Stock Prediction ----
    elif prediction == "max_stock":
        max_product = df.loc[df["current_stock"].idxmax()]
        response = f"Highest stock product: {max_product["product_name"]} ({max_product["current_stock"]})"
    # ---- Mini of purchase Prediction ----
    elif prediction == "min_purchase":
        min_product = df.loc[df["total_purchase"].idxmin()]
        response = f"Least Purchased product: {min_product["product_name"]} ({min_product["total_purchase"]})"
    # ---- Mini of sell Prediction ----
    elif prediction == "min_sell":
        min_product = df.loc[df["total_sell"].idxmin()]
        response = f"Least Sold product: {min_product["product_name"]} ({min_product["total_sell"]})"
    # ---- Mini of Stock Prediction ----
    elif prediction == "min_stock":
        min_product = df.loc[df["current_stock"].idxmin()]
        response = f"Least stock product: {min_product["product_name"]} ({min_product["current_stock"]})"
     
    # ---- find purchase by quantity Prediction ----
    elif prediction == "find_purchase":
        number = re.findall(r'\d+', user_input)
        if number :
            qty = int(number[0])
            result = df[df["total_purchase"] == qty]
            if not result.empty:
                products = result["product_name"].tolist()
                response = f"Products with purchase quantity {qty}:\n "
                count = 0 
                for i, products in enumerate(products,start=1):
                    response += f"{i}.{products}\n"
                    count = i
                
                response += f"\nTotal Products: {count}"
            else:
                response = f"No product found with purchase quantity {qty}."
    
    # ---- find sell by quantity Prediction ----
    elif prediction == "find_sell":
        number = re.findall(r'\d+', user_input)
        if number :
            qty = int(number[0])
            result = df[df["total_sell"] == qty]
            if not result.empty:
                products = result["product_name"].tolist()
                response = f"Products with sell quantity {qty}:\n"
                count = 0 
                for i, products in enumerate(products,start=1):
                    response += f"{i}.{products}\n"
                    count = i
                
                response += f"\nTotal Products: {count}"
            else:
                response = f"No product found with sell quantity {qty}."
     # ---- find stock by quantity Prediction ----
    elif prediction == "find_stock":
        number = re.findall(r'\d+', user_input)
        if number:
            qty = int(number[0])
            result = df[df["current_stock"] == qty]
            if not result.empty:
                products = result["product_name"].tolist()
                response = f"Products with Stock quantity {qty}:\n"
                count = 0 
                for i, products in enumerate(products,start=1):
                    response += f"{i}.{products}\n"
                    count = i
                
                response += f"\nTotal Products: {count}"
            else:
                response = f"No product found with stock quantity {qty}."
    elif prediction == "low_stock":
        low_stock_products = df[df["current_stock"] < 50]
        if not low_stock_products.empty:
        
            names = low_stock_products["product_name"].tolist()
            quantities = low_stock_products["current_stock"].tolist()
            response = "⚠️ These products have low stock:\n\n"
            for name, qty in zip(names, quantities):
                response += f"• {name} (Stock: {qty})\n"
        else:
            response = "✅ All products have sufficient stock."
            
    # ---- ChatBot Response ----
    chat_display.config(state="normal")
    chat_display.insert(tk.END, f"                                          You: {user_input}\n\n")
    chat_display.insert(tk.END, f"Mitra: {response}\n")
    chat_display.insert(tk.END, "-----------------------------------------------------\n\n")
    chat_display.config(state="disabled")
    chat_display.yview(tk.END)

    # ---------- load data ----------
def load_data():
    for row in tree.get_children():
        tree.delete(row)
    quary = """
            SELECT 
                pro.product_id,
                pro.product_name,
               IFNULL(SUM(pur.product_quantity),0) AS total_purchase,
                IFNULL(SUM(s.product_quantity),0) AS total_sell,
                IFNULL(SUM(pur.product_quantity),0) - IFNULL(SUM(s.product_quantity),0) AS current_stock
                
            FROM product pro
            LEFT JOIN purchase pur 
            ON pro.product_id = pur.product_id
            LEFT JOIN sell s 
            ON pro.product_id = s.product_id
            GROUP BY pro.product_id, pro.product_name;
        """
    
    cursor.execute(quary)
    conn.commit()
    rows = cursor.fetchall()
    for i in rows:
        tree.insert("",tk.END, values= i)

    # ---------- Move Back  ----------
# def move_back():
#     stock_win.destroy()
#     dashboard.open_dashboard()
    
# ---------- GUI ----------
stock_win = tk.Tk()
stock_win.title("Stock Management")
stock_win.state("zoomed")
stock_win.configure(bg="#f4f6f9")

# ---------- Styling ----------
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Segoe UI", 11), background="#f0f2f5")
style.configure("TButton",
                font=("Segoe UI", 10, "bold"),
                padding=8)
style.configure("Treeview",
                font=("Segoe UI", 10),
                rowheight=28)
style.configure("Treeview.Heading",
                font=("Segoe UI", 10, "bold"))
# ---------- Title ----------
title = tk.Label(
    stock_win,
    text="Product Stock Overview",
    font=("Segoe UI", 18, "bold"),
    bg="#2c3e50",
    fg="white",
    pady=10
)
title.pack(fill=tk.X)
# ---------- Back button ----------
btn_style = {
    "font": ("Segoe UI", 10, "bold"),
    "width": 12,
    "bg": "#1f6aa5",
    "fg": "white",
    "bd": 0
}
# tk.Button(stock_win, text="Back", command=move_back, **btn_style).pack(anchor="e")
# ---------- Table Frame ----------
table_frame = tk.Frame(stock_win, bg="white")
table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
# ---------- Treeview ----------
columns = ("ID","Product Name","Total Purchase","Total Sell","Current Stock")
tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=15
)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# ---------- Chatbot UI ----------
# Chat display area
chat_display = scrolledtext.ScrolledText(
    stock_win,
    width=70,
    height=10,
    font=("Arial", 11),
    wrap=tk.WORD
)
chat_display.pack(padx=10, pady=5)
chat_display.config(state="disabled")  # user cannot edit chat
# Input frame
input_frame = tk.Frame(stock_win)
input_frame.pack(pady=10)
entry_chat = tk.Entry(input_frame, width=45, font=("Arial", 11))
entry_chat.pack(side=tk.LEFT, padx=5)
tk.Button(
    input_frame,
    text="Ask",
    width=10,
    font=("Arial", 10, "bold"),
    command=chatbot_response
).pack(side=tk.LEFT)
# ---------- Scrollbar ----------
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscrollcommand=scrollbar.set)
load_data()

tk.mainloop()