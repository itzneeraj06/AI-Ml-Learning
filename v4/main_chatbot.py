from database import load_documents
from document_preparer import prepare_documents
from vectorstore_builder import build_vectorstore
from chatbot_chain import get_chatbot_chain
import gradio as gr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
import os
from fastapi import FastAPI
import uvicorn
from threading import Thread

if __name__ == "__main__":
    print("⚙️ Loading data...")
    documents = load_documents()
    print(f"✅ {len(documents)} documents loaded.")

    langchain_docs = prepare_documents(documents)
    print(f"✅ {len(langchain_docs)} Langchain docs ready.")
    
    vectorstore = build_vectorstore(langchain_docs)
    
    def reloadStore():
        # print("call every time confirms")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        embeddingStore = FAISS.load_local('./embedding', embeddings, allow_dangerous_deserialization=True)
        return embeddingStore
        
    retriever = reloadStore().as_retriever(search_kwargs={"k": 30})

    chain = get_chatbot_chain(retriever)

    print("\n🤖 Ask me anything about the POS Restaurant System! (type 'exit' to quit)\n")
    # while True:
    #     query = input("You: ")
    #     if query.lower() == "exit":
    #         break
    #     response = chain.invoke({"question": query})
    #     print("Bot:", response["answer"])
    def chat_with_bot(message,history):
        try:
            result = chain.invoke(message)
            return result["answer"]
        except Exception as e:
            return f"❌ Error: {str(e)}"

    app = FastAPI()
    @app.post("/reload")
    def trigger_reload():
            reloadStore()
            return {"status": "✅ Reloaded Successfully"}

    def run_fastapi():
            uvicorn.run(app, host="127.0.0.1", port=5001, log_level="error")

    Thread(target=run_fastapi, daemon=True).start()
    gr.ChatInterface(chat_with_bot).launch()