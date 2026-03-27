import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

embedding_model=SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.EphemeralClient()
collection = chroma_client.get_or_create_collection("document")

def ingest_document(filepath:str):
    import pypdf
    with open(filepath,"rb") as f:
        reader = pypdf.PdfReader(f)
        pages = [page.extract_text() for page in reader.pages]
    
    for i, page_text in enumerate(pages):
        if not page_text:
            continue
        embedding = embedding_model.encode(page_text).tolist()
        collection.add(
                documents=[page_text],
                embeddings=[embedding],
                ids=[f"{filepath}_page_{i}"]
            )
    


def search_context(query:str, n_results: int=5)->list:
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings = [query_embedding],
        n_results=n_results
    )
    return results["documents"][0]

if __name__ == "__main__":
    ingest_document("documents/annual_report_2024.pdf")
    chunks = search_context("What are the key risks?")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)




