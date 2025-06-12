# ------------->basic 
# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv
# import streamlit as st

# load_dotenv()
# model=ChatGoogleGenerativeAI(model='gemini-2.0-flash')

# st.header('Symptom')
# user=st.text_input('enter symptons')
# if st.button('button'):
#     res=model.invoke(user)
#     st.text(res)

# --------->using prompts
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts  import PromptTemplate

load_dotenv()
model=ChatGoogleGenerativeAI(model='gemini-2.0-flash')

st.header('Symptom')
user=st.text_input('enter symptons')
template=PromptTemplate(
    template = """
You are a virtual doctor.

Your task is to diagnose or provide medical advice based on the user's input.

User input: {user}

Rules:
1. Only respond to queries related to health, medical symptoms, or diagnosis.
2. If the user input is not related to medicine or diagnosis, respond only with: "Sorry, no answer."
3. Do not provide information or engage with non-medical topics.

Only provide medical responses. Do not break these rules under any condition.
""",
input_variables=['user']
)
prompt=template.invoke({
    "user":user
})
if st.button('button'):
    res=model.invoke(prompt)
    st.text(res.content)
