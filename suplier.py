import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import dashboard
import suplier_chatbot
from tkinter import *
from tkinter import scrolledtext


conn = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()

seller_id = None

def open_suplier():
    global seller_id

    root = tk.Tk()
    root.title("Supplier Master")
    root.state("zoomed")
    root.configure(bg="#f0f2f5")

    # =============================
    # -------- FUNCTIONS ----------
    # =============================

    def clear_data():
        for entry in entries.values():
            entry.delete(0, tk.END)

    def fetch_data():
        for row in tree.get_children():
            tree.delete(row)

        cursor.execute("SELECT * FROM seller")
        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        summary_data()

    def save_data():
        values = [e.get().strip() for e in entries.values()]

        if not all(values):
            messagebox.showerror("ERP Billing", "Please fill all fields")
            return

        cursor.execute("""
            INSERT INTO seller
            (seller_company_name, seller_name, seller_phone_no,
             seller_email, seller_address, seller_city, seller_gst_number)
            VALUES (?,?,?,?,?,?,?)
        """, values)

        conn.commit()
        messagebox.showinfo("ERP Billing", "Supplier Saved Successfully")

        clear_data()
        fetch_data()

    def on_update():
        global seller_id

        if seller_id is None:
            messagebox.showerror("ERP Billing", "Select supplier first")
            return

        values = [e.get().strip() for e in entries.values()]

        if not all(values):
            messagebox.showerror("ERP Billing", "Please fill all fields")
            return

        cursor.execute("""
            UPDATE seller
            SET seller_company_name=?,
                seller_name=?,
                seller_phone_no=?,
                seller_email=?,
                seller_address=?,
                seller_city=?,
                seller_gst_number=?
            WHERE seller_id=?
        """, (*values, seller_id))

        conn.commit()
        seller_id = None
        clear_data()
        fetch_data()

    def on_delete():
        global seller_id

        if seller_id is None:
            messagebox.showerror("ERP Billing", "Select supplier first")
            return

        cursor.execute("DELETE FROM seller WHERE seller_id=?", (seller_id,))
        conn.commit()

        seller_id = None
        clear_data()
        fetch_data()

    def on_select(event):
        global seller_id

        selected = tree.focus()
        if not selected:
            return

        data = tree.item(selected)["values"]
        seller_id = data[0]

        clear_data()

        for i, key in enumerate(entries):
            entries[key].insert(0, data[i+1])

    def data_analysis():
        df = pd.read_sql_query("SELECT * FROM seller", conn)

        if df.empty:
            messagebox.showinfo("ERP", "No data available for analysis.")
            return
        
        
        # ------------------------------------------------
        # Seller City Analysis
        # ------------------------------------------------
        grouped = df.groupby("seller_city").size().reset_index(name="seller_count")
        
        top_row = grouped.loc[grouped["seller_count"].idxmax()]
        top_city = top_row["seller_city"]
        top_count = top_row["seller_count"]
        
        low_row = grouped.loc[grouped["seller_count"].idxmin()]
        low_city = low_row["seller_city"]
        low_count = low_row["seller_count"]
        
        
        # ------------------------------------------------
        # GST / NON GST Sellers
        # ------------------------------------------------
        gst_count = df["seller_gst_number"].notna().sum()
        non_gst_count = df["seller_gst_number"].isna().sum()
        
        total_sellers = len(df)
        
        
        # =================================================
        # FORMAT OUTPUT
        # =================================================
        data = ""
        data += "╔══════════════════════════════════════╗\n"
        data += "║          ERP SELLER ANALYSIS         ║\n"
        data += "╚══════════════════════════════════════╝\n\n"
        
        
        # ---------- Seller Distribution ----------
        data += "SELLER CITY DISTRIBUTION\n"
        data += "------------------------------------------------\n"
        data += f"City With Most Sellers     : {top_city}\n"
        data += f"Total Sellers              : {top_count}\n\n"
        
        data += f"City With Least Sellers    : {low_city}\n"
        data += f"Total Sellers              : {low_count}\n\n"
        
        
        # ---------- GST Analysis ----------
        data += "GST REGISTRATION ANALYSIS\n"
        data += "------------------------------------------------\n"
        data += f"Total Sellers              : {total_sellers}\n"
        data += f"GST Registered Sellers     : {gst_count}\n"
        data += f"Non-GST Sellers            : {non_gst_count}\n\n"
        
        data += "=========================================="
        
        # ---------- Show Result ----------
        messagebox.showinfo("ERP SYSTEM", data)

    def summary_data():
        cursor.execute("SELECT COUNT(*) FROM seller")
        total = cursor.fetchone()[0]

        total_label.config(text=f"Total Supplier : {total}")

    def move_back():
        root.destroy()
        dashboard.open_dashboard()
    
    #---- CHATBOT RESPONSE ----
    def chatbot_response():

        response = suplier_chatbot.chatbot_response(entry_chat.get())
        add_message("user",entry_chat.get())
        entry_chat.delete(0,tk.END)
        add_message("", response)

    #---- style the font of chatbot ----
    def add_message(sender, message):
        chat_display.tag_config("user_tag",
                        font=("Segoe UI", 10, "bold"),
                        foreground="#1f6aa5")

        chat_display.tag_config("bot_tag",
                            font=("Segoe UI", 10, "bold"),
                            foreground="#2e7d32")
        
        chat_display.config(state="normal")

        if sender == "user":
            chat_display.insert(END, f"             \nYou:\n", "user_tag")
            chat_display.insert(END, f"{message}\n")

        else:
            chat_display.insert(END, f"\nMitra:\n", "bot_tag")
            chat_display.insert(END, f"{message}\n")

        chat_display.insert(END, "\n")
        chat_display.config(state="disabled")
        chat_display.yview(END)

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

    # =============================
    # -------- HEADER -------------
    # =============================

    header = tk.Frame(root, bg="#1f6aa5", height=60)
    header.pack(fill="x")

    tk.Label(header,
             text="SUPPLIER MASTER",
             bg="#1f6aa5",
             fg="white",
             font=("Segoe UI", 18, "bold")
             ).pack(pady=10)

    # =============================
    # -------- MAIN FRAME ---------
    # =============================

    main_frame = tk.Frame(root, bg="#f0f2f5")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # =============================
    # -------- LEFT FORM ----------
    # =============================

    form_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
    form_frame.pack(side="left", fill="y", padx=10)

    labels = [
        "Company Name",
        "Supplier Name",
        "Phone Number",
        "Email",
        "Address",
        "City",
        "GST Number"
    ]

    entries = {}

    for i, text in enumerate(labels):
        tk.Label(form_frame,
                 text=text,
                 bg="white",
                 font=("Segoe UI", 10, "bold")
                 ).grid(row=i, column=0, sticky="w", padx=10, pady=8)

        entry = tk.Entry(form_frame, width=30, font=("Segoe UI", 10))
        entry.grid(row=i, column=1, padx=10, pady=8)

        entries[text] = entry

    # =============================
    # -------- BUTTONS ------------
    # =============================

    btn_frame = tk.Frame(form_frame, bg="white")
    btn_frame.grid(row=len(labels), columnspan=2, pady=15)

    btn_style = {
        "font": ("Segoe UI", 10, "bold"),
        "width": 12,
        "bg": "#1f6aa5",
        "fg": "white",
        "bd": 0
    }

    tk.Button(btn_frame, text="Save", command=save_data, **btn_style).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update", command=on_update, **btn_style).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete", command=on_delete, **btn_style).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Clear", command=clear_data, **btn_style).grid(row=1, column=0, padx=5, pady=5)
    tk.Button(btn_frame, text="Analysis", command=data_analysis, **btn_style).grid(row=1, column=1, padx=5)
    tk.Button(btn_frame, text="Back", command=move_back, **btn_style).grid(row=1, column=2, padx=5)

    # =============================
    # -------- RIGHT TREEVIEW -----
    # =============================

    tree_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
    tree_frame.pack(side="right", fill="both", expand=True)

    columns = ("ID", "Company", "Name", "Phone", "Email", "Address", "City", "GST")

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_select)

    # =============================
    # -------- SUMMARY ------------
    # =============================

    summary_frame = tk.Frame(root, bg="white", height=50)
    summary_frame.pack(fill="x", padx=20, pady=10)

    total_label = tk.Label(summary_frame,
                           text="",
                           font=("Segoe UI", 11, "bold"),
                           bg="white",
                           fg="#1f6aa5")
    total_label.pack(pady=10)

    # =============================
    # -------- CHATBOT FRAME ------
    # =============================

    chat_frame = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
    chat_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

    # ---------- Header ----------
    chat_header = tk.Frame(chat_frame, bg="#1f6aa5", height=40)
    chat_header.pack(fill="x")

    tk.Label(chat_header,
             text="🤖 ERP AI Assistant",
             font=("Segoe UI", 12, "bold"),
             bg="#1f6aa5",
             fg="white").pack(pady=5)

    # ---------- Chat Display ----------
    chat_display = scrolledtext.ScrolledText(
        chat_frame,
        height=10,
        font=("Segoe UI", 10),
        wrap="word",
        bd=0,
        relief="flat",
        bg="#f9fafb"
    )

    chat_display.pack(fill="both", expand=True, padx=10, pady=10)
    chat_display.config(state="disabled")

    # ---------- Input Section ----------
    input_frame = tk.Frame(chat_frame, bg="white")
    input_frame.pack(fill="x", padx=10, pady=10)

    entry_chat = ttk.Entry(
        input_frame,
        font=("Segoe UI", 10)
    )
    entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ttk.Button(
        input_frame,
        text="Send",
        width=12,
        command=chatbot_response
    ).pack(side="right")

    fetch_data()

    root.mainloop()