import json
import os
import time
from tenacity import retry, wait_fixed, stop_after_attempt
from config import PARAGRAPH_FILE
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

@retry(wait=wait_fixed(5), stop=stop_after_attempt(2))
def convert_to_paragraph(doc_text):
    prompt = f"""
    You are a data formatter. Convert the following JSON object into a meaningful, readable paragraph:

    {doc_text}

    Return only the paragraph.
    """
    result = model.invoke(prompt)
    time.sleep(3)
    return result.content

def save_paragraphs(paragraphs):
    with open(PARAGRAPH_FILE, 'w', encoding='utf-8') as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)

def load_paragraphs():
    if os.path.exists(PARAGRAPH_FILE):
        with open(PARAGRAPH_FILE, 'r',encoding='utf-8') as f:
            return json.load(f)
    return None
