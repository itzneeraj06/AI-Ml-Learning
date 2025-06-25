import os
import json
from config import PARAGRAPH_FILE
from langchain_core.documents import Document
from paragraph_generator import convert_to_paragraph, load_paragraphs, save_paragraphs

def prepare_documents(mongo_docs):
    stored_paragraphs = load_paragraphs() or []
    langchain_docs = []

    for idx, doc in enumerate(mongo_docs):
        metadata = {"collection": doc["_collection"]}
        
        if idx < len(stored_paragraphs):
            paragraph = stored_paragraphs[idx]
        else:
            content = "\n".join([f"{k}: {v}" for k, v in doc.items() if k not in ["_id", "_collection"]])
            # paragraph = convert_to_paragraph(content)
            paragraph = content

            stored_paragraphs.append(paragraph)
            save_paragraphs(stored_paragraphs)
            print(f"✅ Saved paragraph {idx + 1}/{len(mongo_docs)}")

        langchain_docs.append(Document(page_content=paragraph, metadata=metadata))
        
    return langchain_docs
