from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel,RunnableBranch,RunnableLambda

load_dotenv()

# -------->simple chain
# prompt=PromptTemplate(
#     template="summarize in simple terms {topic}",
#     input_variables=['topic']
# )
# model = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
# parser=StrOutputParser()
# chain=prompt|model|parser
# result=chain.invoke({'topic':'git'})
# print(result)

# ------------>call multiple model at a time using model (sequential chain)
# prompt1=PromptTemplate(
#     template='define {topic} in details and make it easy to understand',
#     input_variables=['topic']
# )
# prompt2=PromptTemplate(
#     template='make 5 bullet point on {ot}',
#     input_variables=['ot']
# )

# model =ChatGoogleGenerativeAI(model='gemini-2.0-flash')
# parser=StrOutputParser()
# chain=prompt1|model|parser|prompt2|model|parser
# res=chain.invoke({'topic':'tvs apache'})
# print(res)

# -------------->parallel chain 
# model1 = ChatGoogleGenerativeAI(model='gemini-2.0-flash')
# model2 = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

# prompt1=PromptTemplate(
#     template="write the short note on the topic {topic} and summarize in simple terms",
#     input_variables=['topic']
# )
# prompt2=PromptTemplate(
#     template="write 5imp question on the {topic}",
#     input_variables=['topic']
# )
# prompt3=PromptTemplate(
#     template="merge the privided note {notes} and {quiz} in a single one",
#     input_variables=['notes','quiz']
# )

# parser=StrOutputParser()

# parallelChain=RunnableParallel({
#     'notes':prompt1|model1|parser,
#     'quiz':prompt2|model2|parser,    
# })

# mergeChain=prompt3|model1|parser
# parallel= parallelChain|mergeChain
# result=parallel.invoke({'topic':'git'})
# print(result) 
 
# ------------>conditional chain
model =ChatGoogleGenerativeAI(model='gemini-2.0-flash')
prompt1=PromptTemplate(
    template='classify the sentiment of the following feedback text into positive or negative {feedback}. if you are unable to get sentiment of confuse looks mixed sentiment simply say unable to answer',
    input_variables=['feedback']
)
parser=StrOutputParser()
chain=prompt1|model|parser
res=chain.invoke({'feedback':"thankyou for your support"})
print(res)

prompt2=PromptTemplate(
    template='write an appropriate response to this positive feedback {feedback}',
    input_variables=['feedback']
)
prompt3=PromptTemplate(
    template='write an appropriate response to this negative feedback {feedback}',
    input_variables=['feedback']
)

chainBranch=RunnableBranch(
    (lambda x:x=="Positive",prompt2|model|parser),
    (lambda x:x=='Negative',prompt3|model|parser),
    RunnableLambda(lambda x: "Unable to answer")
)
feedbackAnswer = chain | chainBranch
print(feedbackAnswer.invoke({'feedback':"i am very happy"}))
