import streamlit as st
from pymongo import MongoClient
import fitz  # PyMuPDF
import docx
from datetime import datetime
import base64


MONGO_URI = st.secrets["mongo_uri"]
client = MongoClient(MONGO_URI)
db = client["aino_db"]
users_collection = db["users"]
agent_collection = db["agents"]


def add_agent(
    username,
    agent_name,
    inputs,
    agent_userTitle,
    agent_instructions,
    deliverables,
    docs,
    opening_statement_client_expectation,
    allow_personal,
    date_time,
):

    
    existing_agent = agent_collection.find_one({"parent": username, "agent_name": agent_name})
    if existing_agent:
        st.error("Use different name")
    else:
        agent_collection.insert_one({
            "parent": username,
            "agent_name": agent_name,
            "inputs": inputs,
            "agent_userTitle": agent_userTitle,
            "agent_instructions": agent_instructions,
            "deliverables": deliverables,
            "docs_store": docs,
            "opening_statement_client_expectation": opening_statement_client_expectation,
            "allow_personal": "yes" if allow_personal else "no",
            "Experience_knowledge_base": [],
            "Social Stats": [],
            "birth_time": date_time,
        })
    

    pass
