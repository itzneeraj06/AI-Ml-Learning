import os
import json
import time
from datetime import date
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from tenacity import retry, wait_fixed, stop_after_attempt
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize LLM model
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

# MongoDB connection
client = MongoClient("mongodb+srv://neerajchouhan:ddPgxhoueTJHcith@cluster0.h0byp.mongodb.net/")
db = client["visitorTesting"]
collection_names = db.list_collection_names()

# Reference mapping for ObjectId fields
reference_mapping = {
    'companyId': 'users',
    'visitor': 'visitors',
    'employee': 'users',
    'reference': 'users',
    'relatedTo': 'users',
    'subscriptionId': 'subscriptions',
    'visitHistory': 'visits',
    'createdBy': 'users',
    'passId': 'passes',
    'appointmentId': 'appointments'
}

# File to store generated paragraphs
paragraphs_file = "generatedParagraphsFormatNew.json"

def save_paragraphs_to_file(paragraphs):
    with open(paragraphs_file, 'w', encoding='utf-8') as f:
        json.dump(paragraphs, f, ensure_ascii=False, indent=2)
    print("✅ Paragraphs saved to file.")

def load_paragraphs_from_file():
    if os.path.exists(paragraphs_file):
        with open(paragraphs_file, 'r') as f:
            paragraphs = json.load(f)
        return paragraphs
    return None

@retry(wait=wait_fixed(5), stop=stop_after_attempt(2))
def convert_doc_to_paragraph(doc):
    prompt = f"""
    You are a data formatter. Convert the following JSON object into a meaningful, readable paragraph:

    {doc}

    Return only the paragraph.
    """
    res = model.invoke(prompt)
    print(res)
    time.sleep(2)
    return res

def resolve_references_once(document):
    resolved_doc = {}
    for key, value in document.items():
        if isinstance(value, ObjectId) and key in reference_mapping:
            ref_collection = reference_mapping[key]
            referenced_doc = db[ref_collection].find_one({'_id': value})
            if referenced_doc:
                referenced_doc.pop('_id', None)
                cleaned_ref_doc = {
                    k: v for k, v in referenced_doc.items() if not isinstance(v, ObjectId)
                }
                new_key = key.replace('_id', '')
                resolved_doc[new_key] = cleaned_ref_doc
        else:
            resolved_doc[key] = value
    return resolved_doc

def load_data_from_mongodb():
    all_data = []
    for collection_name in collection_names:
        collection = db[collection_name]
        documents = list(collection.find({}))
        for doc in documents:
            doc["_collection"] = collection_name
            resolved_doc = resolve_references_once(doc)
            all_data.append(resolved_doc)
    return all_data

documents = load_data_from_mongodb()
print(f"✅ Total documents loaded (with resolved references): {len(documents)}")

stored_paragraphs = load_paragraphs_from_file()

def prepare_langchain_docs(mongo_docs):
    if stored_paragraphs is None:
        langchain_docs = []
        paragraphs = []
        for doc in mongo_docs:
            metadata = {"collection": doc["_collection"]}
            content = "\n".join([f"{k}: {v}" for k, v in doc.items() if k not in ["_id", "_collection"]])
            paragraph = convert_doc_to_paragraph(content)
            paragraphs.append(paragraph.content)
            langchain_docs.append(Document(page_content=paragraph.content, metadata=metadata))
        save_paragraphs_to_file(paragraphs)
        print(f"✅ Generated {len(paragraphs)} paragraphs.")
        return langchain_docs
    else:
        langchain_docs = []
        for idx, doc in enumerate(mongo_docs):
            metadata = {"collection": doc["_collection"]}
            paragraph = stored_paragraphs[idx]
            langchain_docs.append(Document(page_content=paragraph, metadata=metadata))
        print("✅ Loaded paragraphs from file.")
        return langchain_docs

langchain_documents = prepare_langchain_docs(documents)
print(f"✅ Langchain Documents prepared: {len(langchain_documents)}")

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)
docs_split = splitter.split_documents(langchain_documents)
print(f"✅ Total chunks created: {len(docs_split)}")

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = FAISS.from_documents(docs_split, embedding=embedding)
vectorstore.save_local('./embedding')
print("✅ Vectorstore created and saved successfully")

retriever = vectorstore.as_retriever(search_kwargs={"k": 50})

# Custom Prompt Template
custom_template = """
You are a smart assistant for answering queries about the Visitor Management System (SAAS).

Guidelines:
1. Always respond clearly and meaningfully.
2. Never show ObjectIds, passwords, internal links, or file paths.
3. If asked who created you, answer: Samyotech Software Solutions Pvt. Ltd.
4. Today’s date is {today_date}.
5. If no info is available, reply: 'No relevant information found'.

System Context:
- This is a SAAS-based Visitor Management System.
- All user roles (superAdmin, admin, employees) are in one `user` table.
- Data is filtered using `companyId`.

Context:
{context}

Question:
{question}
"""

prompt = PromptTemplate(
    template=custom_template,
    input_variables=["context", "question", "today_date"]
)

today = str(date.today())

chain = RetrievalQA.from_chain_type(
    llm=model,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt.partial(today_date=today)}
)
print("✅ RetrievalQA Chain is ready.")

if __name__ == "__main__":
    print("\nAsk me anything (type 'exit' to quit)\n")
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        result = chain.invoke({"query": query})
        print("Bot:", result['result'])
