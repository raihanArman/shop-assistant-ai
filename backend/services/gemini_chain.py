import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from backend.services.vector_store import vectorstore

load_dotenv()

system_message = (
    "You are helpful assistant that helps users find information about products in a shop. "
    "You can answer questions about product details, availability, and recommendations based on user preferences. "
    "If you don't know the answer, you should say I don't know."
)

_llm_instance = None

def get_llm():
    global _llm_instance
    if _llm_instance is None:
        groq_api_key = os.getenv("GROQ_API_KEY")
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        _llm_instance = ChatGroq(
            groq_api_key=groq_api_key,
            model_name=model_name,
            temperature=0.7
        )
    return _llm_instance

def get_relevant_context(query):
    results = vectorstore.similarity_search(query, k=1)
    if results:
        metadata = results[0].metadata
        return (
            f"Product Name: {metadata.get('ProductName')}\n"
            f"Brand: {metadata.get('ProductBrand')}\n"
            f"Price: {metadata.get('Price')}\n"
            f"Gender: {metadata.get('Gender')}\n"
            f"Color: {metadata.get('PrimaryColor')}\n"
            f"Description: {results[0].page_content}"
        )
    return "No relevant search found"

def gen_response(query, history):
    llm = get_llm()
    history.append(f"User:{query}")
    context = get_relevant_context(query)
    prompt = f"{system_message}\n\n" + "\n".join(history) + f"\n\nContext:\n{context}\n\nAssistant:"
    
    response = llm.invoke(prompt)
    if hasattr(response, 'content'):
        response_text = str(response.content).strip()
    elif isinstance(response, str):
        response_text = response.strip()
    else:
        response_text = str(response).strip()

    history.append(f"Assistant:{response_text}")
    return response_text, history