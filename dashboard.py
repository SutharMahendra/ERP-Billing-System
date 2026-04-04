import tkinter as tk
from tkinter import *
from tkinter import ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import customer, payment, product, purchase, receive, sell, suplier, stock

conn = sqlite3.connect("ERP_Billing.db")
cursor = conn.cursor()

# ─── Color Palette ──────────────────────────────────────────────────────────
C_BG        = "#0f1117"   # near-black page background
C_SIDEBAR   = "#161b22"   # sidebar background
C_CARD      = "#1c2230"   # card / panel background
C_ACCENT    = "#00d4aa"   # teal-green primary accent
C_ACCENT2   = "#4f8ef7"   # blue secondary accent
C_ACCENT3   = "#f7a94f"   # amber tertiary accent
C_ACCENT4   = "#f7604f"   # coral / red accent
C_TEXT      = "#e8eaf0"   # primary text
C_MUTED     = "#7a8499"   # muted / label text
C_HEADER    = "#12192b"   # header strip
C_BORDER    = "#2a3345"   # subtle border / divider
C_HOVER     = "#00b894"   # sidebar button hover

# ─── Chart style ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  C_CARD,
    "axes.facecolor":    C_CARD,
    "axes.edgecolor":    C_BORDER,
    "axes.labelcolor":   C_MUTED,
    "xtick.color":       C_MUTED,
    "ytick.color":       C_MUTED,
    "text.color":        C_TEXT,
    "grid.color":        C_BORDER,
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "font.family":       "Segoe UI",
})

CHART_COLORS = [C_ACCENT, C_ACCENT2, C_ACCENT3, C_ACCENT4,
                "#b44fff", "#ff6eb4", "#43e8d8", "#ffda63"]


def open_dashboard():

    root = tk.Tk()
    root.title("ERP Billing System")
    root.state("zoomed")
    root.configure(bg=C_BG)

    # ═══════════════════════════════════════════════════════════════════════
    # DATA LOADERS
    # ═══════════════════════════════════════════════════════════════════════

    def safe_scalar(query):
        """Execute a query and return a single scalar, defaulting to 0."""
        try:
            cursor.execute(query)
            val = cursor.fetchone()[0]
            return val if val is not None else 0
        except Exception:
            return 0

    def load_kpi_data():
        return {
            "suppliers": safe_scalar("SELECT COUNT(seller_id) FROM seller"),
            "customers": safe_scalar("SELECT COUNT(buyer_id) FROM buyer"),
            "products":  safe_scalar("SELECT COUNT(product_id) FROM product"),
            "stock": safe_scalar("""
                SELECT IFNULL(SUM(pur.product_quantity),0)
                       - IFNULL(SUM(s.product_quantity),0)
                FROM product pro
                LEFT JOIN purchase pur ON pro.product_id = pur.product_id
                LEFT JOIN sell s       ON pro.product_id = s.product_id
            """),
            "sell":     safe_scalar("SELECT SUM(product_quantity) FROM sell"),
            "purchase": safe_scalar("SELECT SUM(product_quantity) FROM purchase"),
            "payment":  safe_scalar("SELECT SUM(amount) FROM payment"),
            "receive":  safe_scalar("SELECT SUM(amount) FROM receive"),
        }

    def load_top_buyers(n=6):
        try:
            df = pd.read_sql_query("""
                SELECT b.buyer_company_name, SUM(s.total_amount) AS total
                FROM sell s
                LEFT JOIN buyer b ON b.buyer_id = s.buyer_id
                GROUP BY b.buyer_company_name
                ORDER BY total DESC
                LIMIT ?
            """, conn, params=(n,))
            return df
        except Exception:
            return pd.DataFrame(columns=["buyer_company_name", "total"])

    def load_top_sellers(n=6):
        try:
            df = pd.read_sql_query("""
                SELECT se.seller_company_name, SUM(p.total_amount) AS total
                FROM purchase p
                LEFT JOIN seller se ON se.seller_id = p.seller_id
                GROUP BY se.seller_company_name
                ORDER BY total DESC
                LIMIT ?
            """, conn, params=(n,))
            return df
        except Exception:
            return pd.DataFrame(columns=["seller_company_name", "total"])

    def load_top_products(n=6):
        try:
            df = pd.read_sql_query("""
                SELECT pr.product_name, SUM(s.product_quantity) AS qty_sold
                FROM sell s
                LEFT JOIN product pr ON pr.product_id = s.product_id
                GROUP BY pr.product_name
                ORDER BY qty_sold DESC
                LIMIT ?
            """, conn, params=(n,))
            return df
        except Exception:
            return pd.DataFrame(columns=["product_name", "qty_sold"])

    def load_cashflow():
        """Monthly payment vs receive comparison."""
        try:
            pay_df = pd.read_sql_query("""
                SELECT strftime('%Y-%m', payment_date) AS month,
                       SUM(amount) AS payment
                FROM payment
                GROUP BY month
                ORDER BY month
            """, conn)
            rec_df = pd.read_sql_query("""
                SELECT strftime('%Y-%m', receive_date) AS month,
                       SUM(amount) AS receive
                FROM receive
                GROUP BY month
                ORDER BY month
            """, conn)
            df = pd.merge(pay_df, rec_df, on="month", how="outer").fillna(0)
            df = df.tail(6)   # last 6 months
            return df
        except Exception:
            return pd.DataFrame(columns=["month", "payment", "receive"])

    # ═══════════════════════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════════════════════

    header = Frame(root, bg=C_HEADER, height=64)
    header.pack(fill=X)
    header.pack_propagate(False)

    # Logo dot
    canvas_dot = Canvas(header, width=36, height=36, bg=C_HEADER, highlightthickness=0)
    canvas_dot.pack(side=LEFT, padx=(20, 6), pady=14)
    canvas_dot.create_oval(4, 4, 32, 32, fill=C_ACCENT, outline="")

    Label(header,
          text="ERP Billing System",
          font=("Segoe UI", 18, "bold"),
          bg=C_HEADER, fg=C_TEXT).pack(side=LEFT, pady=14)

    Label(header,
          text="Dashboard",
          font=("Segoe UI", 11),
          bg=C_HEADER, fg=C_MUTED).pack(side=LEFT, padx=(8, 0), pady=17)

    # Refresh button in header
    def refresh_all():
        update_kpis()
        rebuild_charts()

    Button(header,
           text="⟳  Refresh",
           font=("Segoe UI", 10, "bold"),
           bg=C_ACCENT, fg=C_BG,
           activebackground=C_HOVER, activeforeground=C_BG,
           relief=FLAT, padx=16, pady=6,
           command=refresh_all
           ).pack(side=RIGHT, padx=20, pady=14)

    # ═══════════════════════════════════════════════════════════════════════
    # MAIN CONTAINER
    # ═══════════════════════════════════════════════════════════════════════

    main_frame = Frame(root, bg=C_BG)
    main_frame.pack(fill=BOTH, expand=True)

    # ─── SIDEBAR ──────────────────────────────────────────────────────────

    sidebar = Frame(main_frame, bg=C_SIDEBAR, width=220)
    sidebar.pack(side=LEFT, fill=Y)
    sidebar.pack_propagate(False)

    Label(sidebar, text="MODULES",
          font=("Segoe UI", 9, "bold"),
          bg=C_SIDEBAR, fg=C_MUTED).pack(pady=(24, 8), padx=20, anchor=W)

    nav_buttons = {}

    def make_nav_button(parent, text, icon, command):
        frm = Frame(parent, bg=C_SIDEBAR, cursor="hand2")
        frm.pack(fill=X, padx=10, pady=2)

        indicator = Frame(frm, bg=C_SIDEBAR, width=4)
        indicator.pack(side=LEFT, fill=Y)

        inner = Frame(frm, bg=C_SIDEBAR, padx=10, pady=10)
        inner.pack(side=LEFT, fill=BOTH, expand=True)

        lbl = Label(inner,
                    text=f"  {icon}  {text}",
                    font=("Segoe UI", 10, "bold"),
                    bg=C_SIDEBAR, fg=C_TEXT,
                    anchor=W)
        lbl.pack(fill=X)

        def on_enter(e):
            frm.config(bg="#1f2937")
            inner.config(bg="#1f2937")
            lbl.config(bg="#1f2937")
            indicator.config(bg=C_ACCENT)

        def on_leave(e):
            frm.config(bg=C_SIDEBAR)
            inner.config(bg=C_SIDEBAR)
            lbl.config(bg=C_SIDEBAR)
            indicator.config(bg=C_SIDEBAR)

        for widget in (frm, inner, lbl):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e, cmd=command: (root.destroy(), cmd()))

        nav_buttons[text] = (frm, indicator, inner, lbl)

    nav_items = [
        ("Supplier",  "📦", suplier.open_suplier),
        ("Customer",  "👥", customer.open_customer),
        ("Product",   "🏷️",  product.open_product),
        ("Purchase",  "🛒", purchase.open_purchase),
        ("Sell",      "💰", sell.open_sell),
        ("Payment",   "💳", payment.open_payment),
        ("Receive",   "📥", receive.open_receive),
        ("Stock",     "🏗️",  stock.open_stock),
    ]

    for text, icon, cmd in nav_items:
        make_nav_button(sidebar, text, icon, cmd)

    # footer in sidebar
    Frame(sidebar, bg=C_BORDER, height=1).pack(fill=X, padx=16, pady=(20, 10))
    Label(sidebar,
          text="Mahendra Suthar\nERP v1.0",
          font=("Segoe UI", 8),
          bg=C_SIDEBAR, fg=C_MUTED,
          justify=CENTER).pack(pady=(0, 16))

    # ─── CONTENT ──────────────────────────────────────────────────────────

    content = Frame(main_frame, bg=C_BG)
    content.pack(side=RIGHT, fill=BOTH, expand=True)

    # Scrollable canvas for content
    content_canvas = Canvas(content, bg=C_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(content, orient=VERTICAL, command=content_canvas.yview)
    content_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=RIGHT, fill=Y)
    content_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    inner_content = Frame(content_canvas, bg=C_BG)
    content_canvas.create_window((0, 0), window=inner_content, anchor="nw")

    def on_configure(e):
        content_canvas.configure(scrollregion=content_canvas.bbox("all"))

    inner_content.bind("<Configure>", on_configure)

    def _on_mousewheel(e):
        content_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    content_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ─── KPI ROW ──────────────────────────────────────────────────────────

    kpi_row = Frame(inner_content, bg=C_BG)
    kpi_row.pack(fill=X, padx=20, pady=(20, 0))

    kpi_cfg = [
        ("Suppliers",  "📦", C_ACCENT,  "suppliers"),
        ("Customers",  "👥", C_ACCENT2, "customers"),
        ("Products",   "🏷️",  C_ACCENT3, "products"),
        ("Stock Qty",  "📊", "#b44fff", "stock"),
        ("Units Sold", "💰", C_ACCENT,  "sell"),
        ("Purchased",  "🛒", C_ACCENT2, "purchase"),
        ("Payment ₹",  "💳", C_ACCENT3, "payment"),
        ("Receive ₹",  "📥", C_ACCENT4, "receive"),
    ]

    kpi_labels = {}

    for i, (title, icon, color, key) in enumerate(kpi_cfg):
        card = Frame(kpi_row, bg=C_CARD,
                     highlightbackground=C_BORDER,
                     highlightthickness=1)
        card.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
        kpi_row.columnconfigure(i, weight=1)

        # top accent strip
        Frame(card, bg=color, height=3).pack(fill=X)

        # icon + title
        top = Frame(card, bg=C_CARD)
        top.pack(fill=X, padx=12, pady=(10, 0))

        Label(top, text=icon, font=("Segoe UI", 16),
              bg=C_CARD, fg=color).pack(side=LEFT)

        Label(top, text=title,
              font=("Segoe UI", 8, "bold"),
              bg=C_CARD, fg=C_MUTED).pack(side=RIGHT)

        # value
        val_lbl = Label(card, text="—",
                        font=("Segoe UI", 20, "bold"),
                        bg=C_CARD, fg=C_TEXT)
        val_lbl.pack(padx=12, pady=(4, 12), anchor=W)

        kpi_labels[key] = val_lbl

    def update_kpis():
        data = load_kpi_data()
        for key, lbl in kpi_labels.items():
            val = data.get(key, 0)
            if key in ("payment", "receive"):
                lbl.config(text=f"₹{val:,.0f}")
            else:
                lbl.config(text=f"{val:,}")

    # ─── SECTION TITLE ────────────────────────────────────────────────────

    Label(inner_content,
          text="Analytics Overview",
          font=("Segoe UI", 14, "bold"),
          bg=C_BG, fg=C_TEXT).pack(anchor=W, padx=26, pady=(20, 4))

    Label(inner_content,
          text="Live data from your ERP database",
          font=("Segoe UI", 9),
          bg=C_BG, fg=C_MUTED).pack(anchor=W, padx=26, pady=(0, 12))

    # ─── CHART GRID ───────────────────────────────────────────────────────

    chart_outer = Frame(inner_content, bg=C_BG)
    chart_outer.pack(fill=BOTH, expand=True, padx=14, pady=(0, 20))

    # We'll keep references to canvases so we can destroy & rebuild
    chart_refs = {}

    def make_chart_card(parent, row, col, title, subtitle):
        card = Frame(parent, bg=C_CARD,
                     highlightbackground=C_BORDER,
                     highlightthickness=1)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        parent.rowconfigure(row, weight=1)

        hdr = Frame(card, bg=C_CARD)
        hdr.pack(fill=X, padx=16, pady=(14, 4))

        Label(hdr, text=title,
              font=("Segoe UI", 11, "bold"),
              bg=C_CARD, fg=C_TEXT).pack(side=LEFT)
        Label(hdr, text=subtitle,
              font=("Segoe UI", 8),
              bg=C_CARD, fg=C_MUTED).pack(side=RIGHT)

        Frame(card, bg=C_BORDER, height=1).pack(fill=X, padx=16)
        body = Frame(card, bg=C_CARD)
        body.pack(fill=BOTH, expand=True, padx=4, pady=4)
        return body

    # ── Chart 1: Top Buyers (Horizontal Bar) ──────────────────────────────
    def draw_top_buyers(parent):
        df = load_top_buyers()
        fig = Figure(figsize=(5.2, 3.6), dpi=96, tight_layout=True)
        ax = fig.add_subplot(111)

        if df.empty or df["total"].sum() == 0:
            ax.text(0.5, 0.5, "No data yet",
                    ha="center", va="center", color=C_MUTED, fontsize=12)
            ax.axis("off")
        else:
            colors = CHART_COLORS[:len(df)]
            bars = ax.barh(df["buyer_company_name"], df["total"],
                           color=colors, height=0.55, edgecolor="none")
            ax.set_xlabel("Total Sales (₹)", fontsize=8)
            ax.xaxis.grid(True)
            ax.set_axisbelow(True)
            ax.spines[["top", "right", "left"]].set_visible(False)
            # value labels
            for bar, val in zip(bars, df["total"]):
                ax.text(bar.get_width() + bar.get_width() * 0.02,
                        bar.get_y() + bar.get_height() / 2,
                        f"₹{val:,.0f}",
                        va="center", fontsize=7.5, color=C_TEXT)
            ax.tick_params(axis="y", labelsize=8)
            ax.tick_params(axis="x", labelsize=7)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return canvas

    # ── Chart 2: Top Sellers (Vertical Bar) ───────────────────────────────
    def draw_top_sellers(parent):
        df = load_top_sellers()
        fig = Figure(figsize=(5.2, 3.6), dpi=96, tight_layout=True)
        ax = fig.add_subplot(111)

        if df.empty or df["total"].sum() == 0:
            ax.text(0.5, 0.5, "No data yet",
                    ha="center", va="center", color=C_MUTED, fontsize=12)
            ax.axis("off")
        else:
            colors = CHART_COLORS[:len(df)]
            ax.bar(df["seller_company_name"], df["total"],
                   color=colors, edgecolor="none", width=0.55)
            ax.set_ylabel("Total Purchased (₹)", fontsize=8)
            ax.yaxis.grid(True)
            ax.set_axisbelow(True)
            ax.spines[["top", "right"]].set_visible(False)
            plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=7.5)
            ax.tick_params(axis="y", labelsize=7)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return canvas

    # ── Chart 3: Top Products (Donut) ─────────────────────────────────────
    def draw_top_products(parent):
        df = load_top_products()
        fig = Figure(figsize=(5.2, 3.6), dpi=96, tight_layout=True)
        ax = fig.add_subplot(111)

        if df.empty or df["qty_sold"].sum() == 0:
            ax.text(0.5, 0.5, "No data yet",
                    ha="center", va="center", color=C_MUTED, fontsize=12)
            ax.axis("off")
        else:
            colors = CHART_COLORS[:len(df)]
            wedges, texts, autotexts = ax.pie(
                df["qty_sold"],
                labels=df["product_name"],
                colors=colors,
                autopct="%1.1f%%",
                pctdistance=0.78,
                wedgeprops=dict(width=0.55, edgecolor=C_CARD, linewidth=2),
                startangle=90,
                textprops={"fontsize": 7.5, "color": C_TEXT}
            )
            for at in autotexts:
                at.set_fontsize(7)
                at.set_color(C_BG)
            ax.set_title("Qty Sold Share", fontsize=9, color=C_MUTED, pad=6)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return canvas

    # ── Chart 4: Cash Flow — Payment vs Receive (Line) ────────────────────
    def draw_cashflow(parent):
        df = load_cashflow()
        fig = Figure(figsize=(5.2, 3.6), dpi=96, tight_layout=True)
        ax = fig.add_subplot(111)

        if df.empty or len(df) == 0:
            ax.text(0.5, 0.5, "No data yet",
                    ha="center", va="center", color=C_MUTED, fontsize=12)
            ax.axis("off")
        else:
            x = range(len(df))
            labels = df["month"].tolist()

            ax.plot(x, df["payment"], color=C_ACCENT4, marker="o",
                    linewidth=2, markersize=5, label="Payment Out")
            ax.fill_between(x, df["payment"], alpha=0.12, color=C_ACCENT4)

            ax.plot(x, df["receive"], color=C_ACCENT, marker="s",
                    linewidth=2, markersize=5, label="Received In")
            ax.fill_between(x, df["receive"], alpha=0.12, color=C_ACCENT)

            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=7.5)
            ax.yaxis.grid(True)
            ax.set_axisbelow(True)
            ax.spines[["top", "right"]].set_visible(False)
            ax.tick_params(axis="y", labelsize=7)
            ax.legend(fontsize=7.5, framealpha=0,
                      labelcolor=C_TEXT, loc="upper left")
            ax.set_title("Monthly Cash Flow (₹)", fontsize=9,
                         color=C_MUTED, pad=6)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        return canvas

    def rebuild_charts():
        # Destroy old chart widgets if any
        for ref in chart_refs.values():
            try:
                ref.get_tk_widget().destroy()
            except Exception:
                pass
        chart_refs.clear()

        # Destroy and recreate chart grid
        for w in chart_outer.winfo_children():
            w.destroy()

        b1 = make_chart_card(chart_outer, 0, 0,
                             "🏆 Top Buyers", "by total sales amount")
        b2 = make_chart_card(chart_outer, 0, 1,
                             "🏅 Top Suppliers", "by total purchase amount")
        b3 = make_chart_card(chart_outer, 1, 0,
                             "🔥 Top Products", "by quantity sold")
        b4 = make_chart_card(chart_outer, 1, 1,
                             "📈 Cash Flow", "payment vs receive (last 6 months)")

        chart_refs["buyers"]   = draw_top_buyers(b1)
        chart_refs["sellers"]  = draw_top_sellers(b2)
        chart_refs["products"] = draw_top_products(b3)
        chart_refs["cashflow"] = draw_cashflow(b4)

    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════

    footer = Frame(root, bg=C_HEADER, height=30)
    footer.pack(fill=X, side=BOTTOM)
    footer.pack_propagate(False)

    Label(footer,
          text="Developed by Mahendra Suthar  ·  ERP Billing System  ·  All rights reserved",
          font=("Segoe UI", 8),
          bg=C_HEADER, fg=C_MUTED).pack(pady=7)

    # ═══════════════════════════════════════════════════════════════════════
    # INITIAL RENDER
    # ═══════════════════════════════════════════════════════════════════════

    update_kpis()
    rebuild_charts()

    root.mainloop()