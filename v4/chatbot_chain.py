from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from custom_prompt import get_prompt

def get_chatbot_chain(retriever):
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    model = ChatGoogleGenerativeAI(model='gemini-2.0-flash',temperature=0)

    chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": get_prompt()}
    )
    return chain
