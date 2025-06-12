from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
embedding=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

docs = [
    "Patient has a persistent cough and mild fever.",
    "No signs of infection, just seasonal allergies.",
    "Cold symptoms include sneezing, runny nose, and sore throat.",
    "Reports of body aches and chills, no cough.",
    "Chronic asthma diagnosed, inhaler prescribed.",
    "Mild headache and fatigue, no respiratory issues.",
    "Complains of dry cough and nasal congestion.",
    "Sore throat without fever or chills.",
    "Experiencing nausea and stomach pain.",
    "Flu-like symptoms with high fever and cough."
]
query='coufh and cold '

docs_embeddings=embedding.embed_documents(docs)
query_embedding=embedding.embed_query(query)

# show relation b/w query and docs 
print(cosine_similarity([query_embedding],docs_embeddings))

score=cosine_similarity([query_embedding],docs_embeddings)

# add index and sort with respect to the first value
print(sorted(list(enumerate(score[0])),key=lambda x:x[1])[-1])
index,score=(sorted(list(enumerate(score[0])),key=lambda x:x[1])[-1])
print("most relavant answer is :")
print(docs[index])
