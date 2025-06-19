from pymongo import MongoClient
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.faiss import FAISS
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

load_dotenv()

# step1--->connect db and load data
client = MongoClient("mongodb+srv://neerajchouhan:replace@cluster0.h0byp.mongodb.net/")
db = client["visitorTesting"]

collection_names = db.list_collection_names()

def load_data_from_mongodb():
    all_data = []
    for collection_name in collection_names:
        collection = db[collection_name]
        documents = list(collection.find({}))
        for doc in documents:
            doc["_collection"] = collection_name  
            all_data.append(doc)
    return all_data

documents = load_data_from_mongodb()
print(f"Total documents loaded: {len(documents)}")
# print(f"Total documents loaded: {(documents)}")


# step2------>format data
def prepare_langchain_docs(mongo_docs):
    langchain_docs = []
    for doc in mongo_docs:
        metadata = {"collection": doc["_collection"], "_id": str(doc["_id"])}
        content = "\n".join([f"{k}: {v}" for k, v in doc.items() if k not in ["_id", "_collection"]])
        langchain_docs.append(Document(page_content=content, metadata=metadata))
    return langchain_docs

langchain_documents = prepare_langchain_docs(documents)
print(f"Langchain Documents prepared: {len(langchain_documents)}")
# print(f"Langchain Documents prepared: {(langchain_documents)}")


# --------->split data into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
docs_split = splitter.split_documents(langchain_documents)
print(f"Total chunks created: {len(docs_split)}")
# print(f"Total chunks created: {(docs_split)}")

# ---------->convert chunks into embedding
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# -------->this part only for testing
# texts = [doc.page_content for doc in docs_split]
# embeddings = embedding.embed_documents(texts)
# print(f"✅ Total embeddings created: {len(embeddings)}")
# print("✅ Sample embedding vector (first document):", embeddings[0])

# -------->create and store embedding
# chroma not working 
# vectorstore = Chroma.from_documents(documents=docs_split,embedding=embedding,persist_directory='./aaa')

# use faiss
vectorstore = FAISS.from_documents(documents=docs_split,embedding=embedding)
vectorstore.save_local('./embedding')
print("Vectorstore created and persisted successfully")

# ---------->load llm
retriever = vectorstore.as_retriever()
model=ChatGoogleGenerativeAI(model='gemini-2.0-flash')

chain=RetrievalQA.from_chain_type(
    llm=model,
    retriever=retriever,
    return_source_documents=True
)
print("RetrievalQA Chain is ready.")

if __name__ == "__main__":
    print("Ask me anything (type 'exit' to quit)")
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        result = chain.invoke(query)
        print("Bot:", result["result"])
