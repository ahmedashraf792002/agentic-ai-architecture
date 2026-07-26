from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)

response = llm.invoke("Hello my Name Ahmed")

print(response.content)
