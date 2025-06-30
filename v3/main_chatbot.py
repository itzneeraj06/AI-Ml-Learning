from database import load_documents
from document_preparer import prepare_documents
from vectorstore_builder import build_vectorstore
from chatbot_chain import get_chatbot_chain
import gradio as gr

if __name__ == "__main__":
    print("⚙️ Loading data...")
    documents = load_documents()
    print(f"✅ {len(documents)} documents loaded.")

    langchain_docs = prepare_documents(documents)
    print(f"✅ {len(langchain_docs)} Langchain docs ready.")
    
    vectorstore = build_vectorstore(langchain_docs)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 30})

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

    gr.ChatInterface(chat_with_bot, title="🍽️ Restaurant POS Chatbot").launch()
