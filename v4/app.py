from fastapi import FastAPI,Form,Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from database import load_documents
from document_preparer import prepare_documents
from vectorstore_builder import build_vectorstore
from chatbot_chain import get_chatbot_chain
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

print("⚙️ Loading data...")
documents = load_documents()
print(f"✅ {len(documents)} documents loaded.")

langchain_docs = prepare_documents(documents)
print(f"✅ {len(langchain_docs)} Langchain docs ready.")

vectorstore = build_vectorstore(langchain_docs)
retriever = vectorstore.as_retriever(search_kwargs={"k": 30})
chain = get_chatbot_chain(retriever)

class ChatRequest(BaseModel):
    message: str
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = chain.invoke(request.message)
        return {"response": result["answer"]}
    except Exception as e:
        return {"error": str(e)}
    
@app.post("/webhook", response_class=PlainTextResponse)
async def chat(request: Request):
    form = await request.form()
    user_message = form.get("Body", "")
    sender = form.get("From", "")

    try:
        result = chain.invoke(user_message)
        answer = result["answer"]
    except Exception as e:
        answer = "❌ Internal error: " + str(e)

    # Twilio expects XML response in TwiML format
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{answer}</Message>
</Response>"""
    
    return PlainTextResponse(content=twiml_response, media_type="application/xml") 