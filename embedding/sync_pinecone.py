import sys
import os
import time
import pandas as pd
from dotenv import load_dotenv 
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm
from langchain_huggingface import HuggingFaceEmbeddings

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.db.mysql import get_db_connection


load_dotenv()

# Pinecone configuration
api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

spec = ServerlessSpec(
    cloud='aws',
    region='us-east-1'
)

index_name = 'shop-catalog'
existing_indexes = [idx.name for idx in pc.list_indexes()]

# Check if index already exists and verify dimension
if index_name in existing_indexes:
    idx_info = pc.describe_index(index_name)
    if idx_info.dimension != 384:
        print(f"Deleting index '{index_name}' (existing dimension {idx_info.dimension} != 384)...")
        pc.delete_index(index_name)
        time.sleep(5)
        existing_indexes = [idx.name for idx in pc.list_indexes()]

if index_name not in existing_indexes:
    print(f"Creating index '{index_name}' with dimension 384...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='cosine',
        spec=spec
    )

    while not pc.describe_index(index_name).status['ready']:
        print(f"Waiting for index {index_name} to be ready...")
        time.sleep(5)


# Connect to the index
index = pc.Index(index_name)

# Embedding model
embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def fetch_data(cursor):
    query = "SELECT * FROM products"
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    return df

def sync_with_pinecone(data):
    batch_size = 100
    total_batches = (len(data) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(data), batch_size), desc="Processing Batches", unit='batch', total=total_batches):
        i_end = min(len(data), i + batch_size)
        batch = data.iloc[i:i_end]

        # Unique IDs
        ids = [str(row['ProductID']) for _, row in batch.iterrows()]

        # Combine text fields for embedding
        texts = [
            f"{row['Description']} {row['ProductName']} {row['ProductBrand']} {row['Gender']} {row['Price']} {row['PrimaryColor']}"
            for _, row in batch.iterrows()
        ]

        # Embed texts
        embeds = embed_model.embed_documents(texts)

        # Metadata
        metadata = [
            {
                'ProductName': str(row['ProductName']) if pd.notna(row['ProductName']) else '',
                'ProductBrand': str(row['ProductBrand']) if pd.notna(row['ProductBrand']) else '',
                'Gender': str(row['Gender']) if pd.notna(row['Gender']) else '',
                'Price': float(row['Price']) if pd.notna(row['Price']) else 0.0,
                'PrimaryColor': str(row['PrimaryColor']) if pd.notna(row['PrimaryColor']) else '',
                'Description': str(row['Description']) if pd.notna(row['Description']) else ''
            }
            for _, row in batch.iterrows()
        ]

        # Upsert vectors
        vectors = list(zip(ids, embeds, metadata))
        index.upsert(vectors=vectors)

def main():
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    try:
        data = fetch_data(cursor)
        print(f"Fetched {len(data)} products from MySQL.")
        sync_with_pinecone(data)
        print("Pinecone synchronization complete.")
    finally:
        cursor.close()
        db_connection.close()

if __name__ == '__main__':
    main()