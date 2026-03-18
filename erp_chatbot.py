import os
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv


def predict_label(query, label_list):
    load_dotenv()

    # -----------------------------
    # Labels
    # -----------------------------
    VALID_LABELS = label_list

    # -----------------------------
    # Pydantic Schema
    # -----------------------------
    class QuestionLabel(BaseModel):
        label:str

    # -----------------------------
    # Model
    # -----------------------------
    model = init_chat_model("google_genai:gemini-2.5-flash-lite")

    structured_model = model.with_structured_output(QuestionLabel)

    # -----------------------------
    # YOUR ORIGINAL PROMPT
    # -----------------------------
    prompt = PromptTemplate(
        input_variables=["question", "labels"],
        template="""
    You are an ERP query classifier.

    Read the question and reply with ONLY one label from the list below.
    Do NOT explain. Do NOT add punctuation. Output the label word only.

    Labels: {labels}

    Examples:
    Question: How many products do we have? → count
    Question: Filter the buyer with city name ? → filter_city
    Question: Find Company name? → find_company
    Question: Show all items in inventory → list
    Question: Search the buyer with name ? → find_buyer
    Question: Which product has the lowest stock? → low_stock
    Question: What is the maximum selling price? → max_sell

    Question: {question} →
    """
    )

    # -----------------------------
    # Chain
    # -----------------------------
    chain = prompt | structured_model 

    # -----------------------------
    # Run Query
    # -----------------------------
    response = chain.invoke({
        "question": f"{query}?",
        "labels": ", ".join(VALID_LABELS) 
    })

    print(label_list)
    if prediction not in label_list:
        prediction = ""

    print(prediction+"Chatbot response")
    return prediction