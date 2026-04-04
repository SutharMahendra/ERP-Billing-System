from tkinter import *
from tkinter import ttk

def dashboard():

    root = Tk()
    root.title("ERP Billing System - Dashboard")
    root.state("zoomed")
    root.configure(bg="#f0f2f5")

    # ---------- Header ----------
    header = Frame(root, bg="#1f6aa5", height=70)
    header.pack(fill=X)

    Label(header,
          text="ERP Billing System Dashboard",
          font=("Segoe UI", 22, "bold"),
          bg="#1f6aa5",
          fg="white").pack(pady=15)

    # ---------- Main ----------
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

    buttons = [
        "Supplier", "Customer", "Product", "Purchase",
        "Sell", "Payment", "Receive", "Stock"
    ]

    for text in buttons:
        Button(sidebar,
               text=text,
               font=("Segoe UI", 11, "bold"),
               bg="#34495e",
               fg="white",
               activebackground="#1abc9c",
               relief=FLAT,
               width=20,
               pady=10).pack(pady=5)

    # ---------- Content ----------
    content = Frame(main_frame, bg="#ecf0f1")
    content.pack(side=RIGHT, fill=BOTH, expand=True)

    # ---------- KPI SECTION ----------
    kpi_frame = Frame(content, bg="#ecf0f1")
    kpi_frame.pack(pady=20)

    def create_card(parent, title):
        card = Frame(parent, bg="white", width=200, height=80, bd=1, relief="solid")
        card.pack_propagate(False)

        Label(card, text=title,
              font=("Segoe UI", 10, "bold"),
              bg="white",
              fg="#555").pack(anchor="w", padx=10, pady=5)

        Label(card, text="0",
              font=("Segoe UI", 22, "bold"),
              bg="white",
              fg="#1f6aa5").pack(anchor="center")

        return card

    titles = [
        "Total Supplier", "Total Customer", "Total Product", "Total Stock",
        "Total Sell", "Total Purchase", "Total Payment", "Total Receive"
    ]

    row = 0
    col = 0

    for i, title in enumerate(titles):
        card = create_card(kpi_frame, title)
        card.grid(row=row, column=col, padx=15, pady=15)

        col += 1
        if col == 4:
            col = 0
            row += 1

    # ---------- ANALYTICS SECTION ----------
    analytics = Frame(content, bg="#ecf0f1")
    analytics.pack(fill=BOTH, expand=True, padx=20)

    def create_box(parent, title):
        box = Frame(parent, bg="white", bd=1, relief="solid")
        Label(box, text=title,
              font=("Segoe UI", 12, "bold"),
              bg="white",
              fg="#2c3e50").pack(anchor="w", padx=10, pady=10)

        Label(box,
              text="(Graph / Data will appear here)",
              bg="white",
              fg="#888").pack(pady=30)

        return box

    # Row 1
    box1 = create_box(analytics, "Sell vs Purchase")
    box1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    box2 = create_box(analytics, "Payment vs Receive")
    box2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Row 2
    box3 = create_box(analytics, "Top Buyers")
    box3.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    box4 = create_box(analytics, "Product Revenue")
    box4.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    analytics.grid_rowconfigure(0, weight=1)
    analytics.grid_rowconfigure(1, weight=1)
    analytics.grid_columnconfigure(0, weight=1)
    analytics.grid_columnconfigure(1, weight=1)

    # ---------- SMART INSIGHTS ----------
    insight_frame = Frame(content, bg="white", bd=1, relief="solid")
    insight_frame.pack(fill=X, padx=20, pady=10)

    Label(insight_frame,
          text="Smart Insights",
          font=("Segoe UI", 14, "bold"),
          bg="white",
          fg="#2c3e50").pack(anchor="w", padx=10, pady=10)

    Label(insight_frame,
          text="• Your sales increased by 20% this month.\n"
               "• Top buyer contributes 35% of revenue.\n"
               "• Stock levels are stable.",
          font=("Segoe UI", 11),
          bg="white",
          fg="#555",
          justify=LEFT).pack(anchor="w", padx=10, pady=10)

    # ---------- Footer ----------
    footer = Frame(root, bg="#1f6aa5", height=30)
    footer.pack(fill=X)

    Label(footer,
          text="Developed by Mahendra Suthar | ERP Billing System",
          font=("Segoe UI", 9),
          bg="#1f6aa5",
          fg="white").pack(pady=5)

    root.mainloop()


# Run
dashboard()