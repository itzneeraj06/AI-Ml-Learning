from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint,HuggingFacePipeline
from dotenv import load_dotenv
load_dotenv()

# ------>use model from servers directly
# llm=HuggingFaceEndpoint(
#     repo_id='TinyLlama/TinyLlama-1.1B-Chat-v1.0',
#     task='text-generation',
#     pipeline_kwargs=dict(
#         temperature=0.5,
#         max_new_tokens=100
#     )
#     )
# model=ChatHuggingFace(llm)
# result=model.invoke('pm of india')
# print(result)

# -------> load model locally
llm=HuggingFacePipeline.from_model_id(
    model_id='TinyLlama/TinyLlama-1.1B-Chat-v1.0',
    task='text-generation',
    pipeline_kwargs=dict(
        temperature=0.5,
        max_new_tokens=100
    )
)
model=ChatHuggingFace(llm)
result=model.invoke('india')
print(result)