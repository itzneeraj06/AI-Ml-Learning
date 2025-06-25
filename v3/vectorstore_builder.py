from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS

def build_vectorstore(documents, save_path='./embedding'):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # vectorstore = FAISS.from_documents(chunks, embedding=embedding)
    vectorstore = FAISS.from_documents(documents, embedding=embedding)
    vectorstore.save_local(save_path)
    return vectorstore
