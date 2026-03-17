import tkinter as tk
from tkinter import *
from tkinter import ttk
import customer, payment, product, purchase, receive, sell, suplier, stock


def open_dashboard():

    root = tk.Tk()
    root.title("ERP Billing System - Dashboard")
    root.state("zoomed")   # Fullscreen professional look
    root.configure(bg="#f0f2f5")

    # ---------- Styling ----------
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Sidebar.TButton",
                    font=("Segoe UI", 11, "bold"),
                    padding=10,
                    width=20)

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    header_label = Label(
        header,
        text="ERP Billing System Dashboard",
        font=("Segoe UI", 22, "bold"),
        bg="#1f6aa5",
        fg="white"
    )
    header_label.pack(pady=15)

    # ---------- Main Container ----------
    main_frame = Frame(root, bg="#f0f2f5")
    main_frame.pack(fill=BOTH, expand=True)

    # ---------- Sidebar ----------
    sidebar = Frame(main_frame, bg="#2c3e50", width=250)
    sidebar.pack(side=LEFT, fill=Y)

    Label(sidebar,
          text="Navigation",
          font=("Segoe UI", 14, "bold"),
          bg="#2c3e50",
          fg="white").pack(pady=20)

    # ---------- Content Area ----------
    content = Frame(main_frame, bg="#ecf0f1")
    content.pack(side=RIGHT, fill=BOTH, expand=True)

    Label(content,
          text="Welcome to ERP Billing System",
          font=("Segoe UI", 20, "bold"),
          bg="#ecf0f1",
          fg="#2c3e50").pack(pady=50)

    Label(content,
          text="Select a module from the left panel to continue.",
          font=("Segoe UI", 14),
          bg="#ecf0f1",
          fg="#34495e").pack()

    # ---------- Button Function ----------
    def open_module(module_function):
        root.destroy()
        module_function()

    # ---------- Sidebar Buttons ----------
    buttons = [
        ("Supplier", suplier.open_suplier),
        ("Customer", customer.open_customer),
        ("Product", product.open_product),
        ("Purchase", purchase.open_purchase),
        ("Sell", sell.open_sell),
        ("Payment", payment.open_payment),
        ("Receive", receive.open_receive),
        ("Stock", stock.open_stock),
    ]

    for text, command in buttons:
        btn = Button(sidebar,
                     text=text,
                     font=("Segoe UI", 11, "bold"),
                     bg="#34495e",
                     fg="white",
                     activebackground="#1abc9c",
                     activeforeground="white",
                     relief=FLAT,
                     width=20,
                     pady=10,
                     command=lambda cmd=command: open_module(cmd))
        btn.pack(pady=5)

    # ---------- Footer ----------
    footer = Frame(root, bg="#1f6aa5", height=30)
    footer.pack(fill=X)

    Label(footer,
          text="Developed by Mahendra Suthar | ERP Billing System",
          font=("Segoe UI", 9),
          bg="#1f6aa5",
          fg="white").pack(pady=5)

    root.mainloop()