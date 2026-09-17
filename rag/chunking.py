import numpy as np
from sentence_transformers import SentenceTransformer   

#1 Initialize the embedding llm model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

#2 Chinking startegy function
def chunk_text(text, chunk_size=150, chunk_overlap=30):
    """
    Splits a long string into smaller text chunks based on character count.
    Includes an overlap so context isn't lost at the boundaries.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move the window forward by chunk size minus the overlap
        start += (chunk_size - chunk_overlap)
    return chunks

#3 define long text to be chunked
long_document = (
    "Artificial intelligence and machine learning are transforming modern industries at a rapid pace. "
    "Deep learning models require massive amounts of data to train effectively, allowing them to spot complex patterns. "
    "Natural language processing helps computers understand human text, making things like translation possible. "
    "Computer vision allows machines to process images, which is essential for self-driving cars and medical imaging."
)

#4 Chunk the long document
chunks = chunk_text(long_document, chunk_size=150, chunk_overlap=30)

#5 print the resulting chunks
print("--- Chunking Results ---")
print(f"Original text length: {len(long_document)} characters.")
print(f"Broken down into {len(chunks)} chunks:\n")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: \"{chunk}\" (Len: {len(chunk)})")
print("-" * 50 + "\n")  

#6 Define the query sentence
query = "How do computers understand human text?"

#7 Generate embeddings for the chunks and the query
chunk_embeddings = embedding_model.encode(chunks)
query_embedding = embedding_model.encode([query])[0]

#8 Compute cosine similarities between the query and each chunk
cosine_similarities = np.dot(chunk_embeddings, query_embedding) / (np.linalg.norm(chunk_embeddings, axis=1) * np.linalg.norm(query_embedding))  

# 9 Retrieve the most similar 3 chunks from the corpus
# (Adjusted to look for up to 3 chunks, or fewer if total chunks < 3)
most_similar_indices = np.argsort(cosine_similarities)[-3:][::-1]
most_similar_chunks = [chunks[i] for i in most_similar_indices]     

# 10 Print the most similar chunks
print("Most similar chunks to the query:")
for chunk in most_similar_chunks:
    print(f"\"{chunk}\"")