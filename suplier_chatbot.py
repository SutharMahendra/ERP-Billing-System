import pandas as pd 
from rapidfuzz import process
import sqlite3
import erp_chatbot
import re

conn = sqlite3.connect("ERP_Billing.db")

def chatbot_response(user_query):

        df = pd.read_sql_query("SELECT * FROM seller", conn)

        user_input = user_query

        SELLER_LABELS = [
            # basic
            "count", "list",
            # field search
            "find_phone","find_company","find_seller"
            # filters
            "filter_city", "filter_company",
            # count
            "count_with_gst", "count_without_gst",
        ]

        if user_input == None or user_input == "":
            prediction = ""
        else: 
            prediction = erp_chatbot.predict_label(user_input, SELLER_LABELS)

        response = "Sorry, I didn't understand the question."
        
        print(prediction)
        
        # ---- Count Prediction ----
        if prediction == "count":
            total_seller = len(df)
            response = f"Total Sellers: {total_seller}"

        # ---- List Prediction ----
        elif prediction == "list":

            # Decide what to list
            if "company" in user_input:
                names = df["seller_company_name"].dropna().astype(str).tolist()
                response = "🏢 Company Names:\n\n"
            else:
                names = df["seller_name"].dropna().astype(str).tolist()
                response = "👤 Buyer Names:\n\n"

            # Add numbering
            for i, name in enumerate(names, start=1):
                response += f"{i}. {name}\n"

        # ---- find phone No Prediction ----
        elif prediction == "find_phone":
            number = re.findall(r'\d+', user_input)

            if number:
                phone = number[0]  

                result = df[df["seller_phone_no"].astype(str) == phone]

                if not result.empty:
                    company_name = result.iloc[0]["seller_company_name"]

                    response = (
                        f"📞 Phone Number: {phone}\n"
                        f"🏢 Company: {company_name}"
                    )
                else:
                    response = f"❌ No seller found with phone number {phone}"
            else:
                response = "⚠️ Please enter a valid phone number"

        # ---- find company name Prediction ----
        elif prediction == "find_company":
        
            # Step 1: Get all company names
            company_list = df["seller_company_name"].astype(str).tolist()

            # Step 2: Match user input with company names
            match = process.extractOne(user_input, company_list)

            if match:
                company_name = match[0]

                # Step 3: Get matching rows
                result = df[df["seller_company_name"] == company_name]

                if not result.empty:
                    response = f"🏢 Company Found: {company_name}\n\n"

                    for _, row in result.iterrows():
                        response += (
                            f"👤 Seller: {row['seller_name']}\n"
                            f"📞 Phone: {row['seller_phone_no']}\n"
                            f"📧 Email: {row['seller_email']}\n"
                            f"📍 City: {row['seller_city']}\n"
                            f"🧾 GST: {row['seller_gst_number']}\n"
                            "----------------------\n"
                        )
                else:
                    response = f"❌ No data found for company {company_name}"

            else:
                response = "❌ Company not found"

        # ---- find seller Prediction ----
        elif prediction == "find_seller":

           # Step 1: Clean user input (remove extra words)
           clean_input = re.sub(
               r"(find|search|get|seller|details|of|is|available)",
               "",
               user_input.lower()
           ).strip()

           # Step 2: Get all seller names
           seller_list = df["seller_name"].astype(str).tolist()

           # Step 3: Fuzzy match
           match = process.extractOne(clean_input, seller_list)

           if match:
               seller_name = match[0]

               # Step 4: Get matching data
               result = df[df["seller_name"] == seller_name]

               if not result.empty:
                   response = f"👤 Seller Found: {seller_name}\n\n"

                   for _, row in result.iterrows():
                       response += (
                           f"🏢 Company: {row['seller_company_name']}\n"
                           f"📞 Phone: {row['seller_phone_no']}\n"
                           f"📧 Email: {row['seller_email']}\n"
                           f"📍 City: {row['seller_city']}\n"
                           f"🧾 GST: {row['seller_gst_number']}\n"
                           "----------------------\n"
                       )
               else:
                   response = f"❌ No data found for seller {seller_name}"

           else:
               response = "❌ Buyer not found"

        # ---- Filter City name Prediction ----
        elif prediction == "filter_city":
        
            # Step 1: Get all cities from dataframe
            city_list = df["seller_city"].astype(str).unique().tolist()

            # Step 2: Clean user input
            clean_input = re.sub(
                r"(show|list|sellers|from|in|who|are|the)",
                "",
                user_input.lower()
            ).strip()

            # Step 3: Match city using fuzzy matching
            match = process.extractOne(clean_input, city_list)

            if match and match[1] > 70:
                city = match[0]

                # Step 4: Filter data
                result = df[df["seller_city"] == city]

                if not result.empty:
                    response = f"📍 Sellers from {city}:\n\n"

                    for _, row in result.iterrows():
                        response += (
                            f"👤 {row['seller_name']} "
                            f"(🏢 {row['seller_company_name']})\n"
                        )
                else:
                    response = f"❌ No sellers found in {city}"
            else:
                response = "⚠️ City not recognized"
        
        #---- count seller which dont have gst number ----
        elif prediction == "count_without_gst":
        
            # Filter rows where GST is empty or null
            result = df[
                df["seller_gst_number"].isna() |
                (df["seller_gst_number"].astype(str).str.strip() == "")
            ]

            count = len(result)

            response = f"📊 Buyers without GST: {count}"
            
        #---- count seller which dont have gst number ----
        elif prediction == "count_with_gst":
            # Filter rows where GST is NOT empty
            result = df[
                df["seller_gst_number"].notna() &
                (df["seller_gst_number"].astype(str).str.strip() != "")
            ]

            count = len(result)

            response = f"📊 Buyers with GST: {count}"
        
        print(response)
        return response