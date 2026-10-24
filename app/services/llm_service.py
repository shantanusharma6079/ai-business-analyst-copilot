import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    api_key=os.getenv("GROQ_API_KEY")
)

def generate_response(prompt: str):
    response = llm.invoke(prompt)
    return response.content