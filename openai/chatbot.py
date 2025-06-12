from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
model=ChatGoogleGenerativeAI(model='gemini-2.0-flash')

# doesnt have context
# while True:
#     user=input("me : ")
#     if user=='exit':
#         break
#     result=model.invoke(user)
#     print("ai : ",result.content)

# give context
chatContext=[]
while True:
    user=input("me : ")
    chatContext.append(user)
    if user=='exit':
        break
    result=model.invoke(chatContext)
    print("ai : ",result.content)
