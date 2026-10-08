import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone, ServelessSpec
from langchain_pinecone import PineconeVectorStore

load_dotenv()

# init embedding model
embedding_model=GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# init pinecone
pc=Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index=pc.Index('shop-catalog')

# init vectorstore
vectorstore=PineconeVectorStore(
    index=index,
    embedding=embedding_model,
    text_key="description"
)