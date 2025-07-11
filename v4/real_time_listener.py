from pymongo import MongoClient
from config import MONGO_URI, PARAGRAPH_FILE
from database import resolve_references_once
from langchain_core.documents import Document
import json
import os
from vectorstore_builder import build_vectorstore
import requests

client = MongoClient(MONGO_URI)
db = client["pos-samyotech-in"]
print("running.....")

def load_paragraphs():
    try:
        with open(PARAGRAPH_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_paragraphs(paragraphs):
    with open(PARAGRAPH_FILE, 'w', encoding='utf-8') as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)

langchain_docs = []
with db.watch() as stream:
    for change in stream:
        if change["operationType"] == "insert":
            # print("Change detected:-----------------", change["fullDocument"])
            print("Change detected..........")
            new_doc = change["fullDocument"]
            resolved_doc = resolve_references_once(new_doc)
            
            stored_paragraphs = load_paragraphs()
            
            for doc in [resolved_doc]:
                try:
                    metadata = {"collection": doc["_collection"]}
                except (TypeError, KeyError):
                    metadata = {"collection": None}

                if isinstance(doc, dict):
                    content = "\n".join([
                        f"{k}: {v}" for k, v in doc.items()
                        if k not in ["_id", "_collection"]
                    ])
                else:
                    content = f'{doc}'

                paragraph = content
                stored_paragraphs.append(paragraph)
                save_paragraphs(stored_paragraphs)
                # langchain_docs.append(Document(page_content=paragraph, metadata=metadata))
                build_vectorstore([Document(page_content=paragraph, metadata=metadata)],append=True)
                try:
                    response = requests.post("http://localhost:5001/reload")
                    print("✅ Chatbot reload triggered:", response.json())
                except Exception as e:
                    print("❌ Failed to trigger chatbot reload:", str(e))
                