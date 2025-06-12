from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# LLaMA 2 model via Ollama
llm = Ollama(model="llama2")

# Basic prompt
prompt = PromptTemplate(
    input_variables=["question"],
    template="Answer the following question clearly:\n{question}"
)

# LLMChain setup
chain = LLMChain(llm=llm, prompt=prompt)

# Terminal input
if __name__ == "__main__":
    print("Ask a question (type 'exit' to quit):")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = chain.run(question=user_input)
        print("LLaMA2:", response)