import pandas as pd 
from rapidfuzz import process
import sqlite3
import erp_chatbot
import re

conn = sqlite3.connect("ERP_Billing.db")

def chatbot_response(user_input):
    df = pd.read_sql_query("""
                            SELECT bill_number, sell_date, b.buyer_company_name ,p.product_name, product_quantity, s.product_price, s.product_gst_rate, gst_amount, total_amount, payment_term
                            FROM sell s
                            LEFT JOIN buyer b ON s.buyer_id = b.buyer_id
                            LEFT JOIN product p ON s.product_id = p. product_id
                            """,conn)
    
    SELL_LABELS = [
        "count", "list_sell",
        
        "total_gst_amount",

        "sell_quantity_analysis","sell_amount_analysis", "payment_term_analysis",
        "find_sell_qty", "find_sell_amount", "find_bill",

        "filter_date", "filter_buyer",

        "product_sales_summary",

        "top_buyer"
    ]

    if user_input == None or user_input == "":
        prediction = ""
    else: 
        prediction = erp_chatbot.predict_label(user_input, SELL_LABELS)

    response = "Sorry, I didn't understand the question."
    
    # ---- Count Prediction ----
    if prediction == "count":
        total = len(df)
        response = f"Total Sellers: {total}"

    # ---- list Prediction ----
    elif prediction == "list_sell":
        if df.empty :
            response = "⚠️ No sales records found."
            return
        
        response = "🧾 Sales Records (Summary):\n\n"

        for i, row in df.iterrows():
            response += (
                f"{i+1}. {row['bill_number']} | "
                f"Qty: {row['product_quantity']} | "
                f"₹{row['total_amount']} | "
                f"{row['payment_term']}\n"
            )
    # ---- GST Amount Prediction ----
    elif prediction == "total_gst_amount":

        if df.empty:
            response = "⚠️ No sales data available."

        else:
            total_gst = df["gst_amount"].sum()
            response = f"💰 Total GST Collected: ₹{total_gst}"

    # ---- Sell Quantity Analysis ----
    elif prediction == "sell_quantity_analysis":

        if df.empty:
            response = "⚠️ No sales data available."

        else:
            # 👉 TOTAL QUANTITY
            if "total" in user_input or "sum" in user_input:
                total_qty = df["product_quantity"].sum()
                response = f"📦 Total Quantity Sold: {total_qty}"

            # 👉 HIGHEST / MAX (single sale)
            elif "max" in user_input or "highest" in user_input:
                row = df.loc[df["product_quantity"].idxmax()]
                response = (
                    f"📈 Highest Quantity Sale:\n"
                    f"🧾 Bill: {row['bill_number']}\n"
                    f"🏢 Buyer: {row['buyer_company_name']}\n"
                    f"📦 Product: {row['product_name']}\n"
                    f"🔢 Quantity: {row['product_quantity']}"
                )

            # 👉 LOWEST / MIN (single sale)
            elif "min" in user_input or "lowest" in user_input:
                row = df.loc[df["product_quantity"].idxmin()]
                response = (
                    f"📉 Lowest Quantity Sale:\n"
                    f"🧾 Bill: {row['bill_number']}\n"
                    f"🏢 Buyer: {row['buyer_company_name']}\n"
                    f"📦 Product: {row['product_name']}\n"
                    f"🔢 Quantity: {row['product_quantity']}"
                )

            # 👉 PRODUCT LEVEL (MOST / LEAST SOLD)
            elif "product" in user_input:

                grouped = df.groupby(["product_name"])["product_quantity"].sum().reset_index()

                if "most" in user_input:
                    row = grouped.loc[grouped["product_quantity"].idxmax()]
                    response = (
                        f"🏆 Most Sold Product:\n"
                        f"📦 Product: {row['product_name']}\n"
                        f"🔢 Total Quantity Sold: {row['product_quantity']}"
                    )

                elif "least" in user_input:
                    row = grouped.loc[grouped["product_quantity"].idxmin()]
                    response = (
                        f"📉 Least Sold Product:\n"
                        f"📦 Product: {row['product_name']}\n"
                        f"🔢 Total Quantity Sold: {row['product_quantity']}"
                    )

                else:
                    response = "⚠️ Please specify most or least product."

            # 👉 DEFAULT
            else:
                response = "⚠️ Please specify: total / max / min / most / least"


    # ---- Sell Amount Analysis ----
    elif prediction == "sell_amount_analysis":

        if df.empty:
            response = "⚠️ No sales data available."

        else:

            # 👉 TOTAL AMOUNT
            if "total" in user_input or "sum" in user_input:
                total_amount = df["total_amount"].sum()
                response = f"💰 Total Sales Amount: ₹{total_amount}"

            # 👉 HIGHEST SALE
            elif "max" in user_input or "highest" in user_input:
                row = df.loc[df["total_amount"].idxmax()]
                response = (
                    f"📈 Highest Sale:\n"
                    f"🧾 Bill: {row['bill_number']}\n"
                    f"🏢 Buyer: {row['buyer_company_name']}\n"
                    f"📦 Product: {row['product_name']}\n"
                    f"🔢 Quantity: {row['product_quantity']}\n"
                    f"💰 Amount: ₹{row['total_amount']}"
                )

            # 👉 LOWEST SALE
            elif "min" in user_input or "lowest" in user_input:
                row = df.loc[df["total_amount"].idxmin()]
                response = (
                    f"📉 Lowest Sale:\n"
                    f"🧾 Bill: {row['bill_number']}\n"
                    f"🏢 Buyer: {row['buyer_company_name']}\n"
                    f"📦 Product: {row['product_name']}\n"
                    f"🔢 Quantity: {row['product_quantity']}\n"
                    f"💰 Amount: ₹{row['total_amount']}"
                )

            # 👉 DEFAULT
            else:
                response = "⚠️ Please specify: total / max / min"

    # ---- Payment Term Analysis ----
    elif prediction == "payment_term_analysis":

        if df.empty:
            response = "⚠️ No sales data available."

        else:
            payment_col = df["payment_term"].astype(str).str.lower()

            # 👉 COUNT SUMMARY
            if "count" in user_input or "summary" in user_input:
                counts = payment_col.value_counts()

                response = "📊 Payment Summary:\n\n"
                for method, count in counts.items():
                    response += f"💳 {method.capitalize()}: {count} transactions\n"

            # 👉 CASH
            elif "cash" in user_input:
                result = df[payment_col == "cash"]

                response = f"💰 Cash Transactions: {len(result)}\n\n"
                for i, row in result.iterrows():
                    response += f"{i+1}. {row['bill_number']} | ₹{row['total_amount']}\n"

            # 👉 ONLINE / UPI
            elif "online" in user_input or "upi" in user_input:
                result = df[payment_col.isin(["online", "upi"])]

                response = f"💳 Online/UPI Transactions: {len(result)}\n\n"
                for i, row in result.iterrows():
                    response += f"{i+1}. {row['bill_number']} | ₹{row['total_amount']}\n"

            # 👉 TOTAL AMOUNT BY PAYMENT TYPE
            elif "total" in user_input:
                grouped = df.groupby("payment_term")["total_amount"].sum()

                response = "💰 Payment-wise Total Amount:\n\n"
                for method, amount in grouped.items():
                    response += f"{method}: ₹{amount}\n"

            # 👉 DEFAULT
            else:
                response = "⚠️ Please specify: cash / online / summary / total"

    # ---- Find Sell Quantity ----
    elif prediction == "find_sell_qty":
    
        if df.empty:
            response = "⚠️ No sales data available."
    
        else:
    
            # 👉 Extract number from user input
            qty_list = re.findall(r'\d+', user_input)
    
            if qty_list:
                qty = int(qty_list[0])

                result = df[df["product_quantity"] == qty]
    
                if not result.empty:
                    response = f"🔍 Sales with Quantity {qty}:\n\n"
    
                    for i, row in result.iterrows():
                        response += (
                            f"{i+1}. 🧾 Bill: {row['bill_number']}\n"
                            f"   🏢 Buyer: {row['buyer_company_name']}\n"
                            f"   📦 Product: {row['product_name']}\n"
                            f"   💰 Amount: ₹{row['total_amount']}\n\n"
                        )
                else:
                    response = f"⚠️ No sales found with quantity {qty}."
    
            else:
                response = "⚠️ Please specify a quantity."
            
    # ---- Find Bill ----
    elif prediction == "find_bill":

        if df.empty:
            response = "⚠️ No sales data available."

        else:

            # 👉 Extract bill number (supports BILL003 or just 3)
            bill_match = re.search(r'bill\s*0*(\d+)', user_input.lower())

            if bill_match:
                bill_number = f"BILL{bill_match.group(1).zfill(3)}"
            else:
                # fallback: find any number
                num = re.findall(r'\d+', user_input)
                if num:
                    bill_number = f"BILL{int(num[0]):03d}"
                else:
                    bill_number = None

            if bill_number:

                result = df[df["bill_number"].str.upper() == bill_number]

                if not result.empty:
                    response = f"🧾 Bill Details: {bill_number}\n\n"

                    for i, row in result.iterrows():
                        response += (
                            f"🏢 Buyer: {row['buyer_company_name']}\n"
                            f"📦 Product: {row['product_name']}\n"
                            f"🔢 Quantity: {row['product_quantity']}\n"
                            f"💵 Price: ₹{row['product_price']}\n"
                            f"🧾 GST: ₹{row['gst_amount']} ({row['product_gstrate']}%)\n"
                            f"💰 Total: ₹{row['total_amount']}\n"
                            f"💳 Payment: {row['payment_term']}\n"
                            f"📅 Date: {row['sell_date']}\n"
                            f"---------------------------------\n"
                        )
                else:
                    response = f"⚠️ No record found for {bill_number}."

            else:
                response = "⚠️ Please provide a valid bill number."
    # ---- Find Sell Amount ----
    elif prediction == "find_sell_amount":

        if df.empty:
            response = "⚠️ No sales data available."

        else:

            # 👉 Extract amount from user input
            amt_list = re.findall(r'\d+', user_input)

            if amt_list:
                amount = int(amt_list[0])

                result = df[df["total_amount"] == amount]

                if not result.empty:
                    response = f"💰 Sales with Amount ₹{amount}:\n\n"

                    for i, row in result.iterrows():
                        response += (
                            f"{i+1}. 🧾 Bill: {row['bill_number']}\n"
                            f"   🏢 Buyer: {row['buyer_company_name']}\n"
                            f"   📦 Product: {row['product_name']}\n"
                            f"   🔢 Qty: {row['product_quantity']}\n"
                            f"   💳 Payment: {row['payment_term']}\n\n"
                        )
                else:
                    response = f"⚠️ No sales found with amount ₹{amount}."

            else:
                response = "⚠️ Please specify an amount."

    # ---- Filter by Date ----
    elif prediction == "filter_date":
    
        if df.empty:
            response = "⚠️ No sales data available."
    
        else:
    
            # 👉 Convert column to datetime
            df["sell_date"] = pd.to_datetime(df["sell_date"], errors="coerce")
    
            # 👉 Extract all dates from user input
            dates = re.findall(r'\d{4}-\d{2}-\d{2}', user_input)
    
            # =========================
            # 👉 BETWEEN DATES
            # =========================
            if "between" in user_input and len(dates) >= 2:
                start_date = pd.to_datetime(dates[0])
                end_date = pd.to_datetime(dates[1])
    
                result = df[
                    (df["sell_date"] >= start_date) &
                    (df["sell_date"] <= end_date)
                ]
    
                response = f"📅 Sales from {start_date.date()} to {end_date.date()}:\n\n"
    
            # =========================
            # 👉 AFTER DATE
            # =========================
            elif "after" in user_input and len(dates) >= 1:
                start_date = pd.to_datetime(dates[0])
    
                result = df[df["sell_date"] > start_date]
    
                response = f"📅 Sales after {start_date.date()}:\n\n"
    
            # =========================
            # 👉 BEFORE DATE
            # =========================
            elif "before" in user_input and len(dates) >= 1:
                end_date = pd.to_datetime(dates[0])
    
                result = df[df["sell_date"] < end_date]
    
                response = f"📅 Sales before {end_date.date()}:\n\n"
    
            # =========================
            # 👉 EXACT DATE
            # =========================
            elif len(dates) == 1:
                exact_date = pd.to_datetime(dates[0])
    
                result = df[df["sell_date"] == exact_date]
    
                response = f"📅 Sales on {exact_date.date()}:\n\n"
    
            else:
                response = "⚠️ Please provide a valid date (YYYY-MM-DD)."
                result = None
    
            # =========================
            # 👉 SHOW RESULT
            # =========================
            if result is not None:
                if not result.empty:
                    for i, row in result.iterrows():
                        response += (
                            f"{i+1}. 🧾 {row['bill_number']} | "
                            f"{row['buyer_company_name']} | "
                            f"{row['product_name']} | "
                            f"Qty: {row['product_quantity']} | "
                            f"₹{row['total_amount']}\n"
                        )
                else:
                    response += "⚠️ No records found."

    # ---- Filter by Buyer ----
    elif prediction == "filter_buyer":
    
        if df.empty:
            response = "⚠️ No sales data available."
    
        else:
    
            # 👉 Get user input in lower
            user_text = user_input.lower()
    
            # 👉 Filter by company name OR buyer name
            result = df[
                df["buyer_company_name"].str.lower().str.contains(user_text) |
                df["buyer_name"].str.lower().str.contains(user_text)
            ]
    
            if not result.empty:
                response = "🏢 Sales for Selected Buyer:\n\n"
    
                for i, row in result.iterrows():
                    response += (
                        f"{i+1}. 🧾 {row['bill_number']} | "
                        f"{row['product_name']} | "
                        f"Qty: {row['product_quantity']} | "
                        f"₹{row['total_amount']} | "
                        f"{row['payment_term']}\n"
                    )
            else:
                response = "⚠️ No sales found for this buyer."
    # ---- Top Buyer ----
    elif prediction == "top_buyer":

        if df.empty:
            response = "⚠️ No sales data available."

        else:
            # 👉 Group directly (no merge needed)
            grouped = df.groupby("buyer_company_name")["total_amount"].sum().reset_index()

            # 👉 Get top buyer
            top = grouped.loc[grouped["total_amount"].idxmax()]

            response = (
                "🏆 Top Buyer:\n\n"
                f"🏢 Company: {top['buyer_company_name']}\n"
                f"💰 Total Purchase: ₹{top['total_amount']}"
            )
    # ---- Product Sales Summary ----
    elif prediction == "product_sales_summary":

        if df.empty:
            response = "⚠️ No sales data available."

        else:
            # 👉 Group by product
            grouped = df.groupby("product_name").agg({
                "product_quantity": "sum",
                "total_amount": "sum"
            }).reset_index()

            # 👉 Sort by revenue (best first)
            grouped = grouped.sort_values(by="total_amount", ascending=False)

            response = "📦 Product Sales Summary:\n\n"

            for i, row in enumerate(grouped.itertuples(index=False), start=1):
                response += (
                    f"{i}. {row.product_name}\n"
                    f"   🔢 Total Qty: {row.product_quantity}\n"
                    f"   💰 Revenue: ₹{row.total_amount}\n\n"
                )
    
    return response