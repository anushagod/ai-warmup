import numpy as np
from sentence_transformers import SentenceTransformer

#1 Initialize the embedding llm model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Define your dataset (the set of sentences to search through)
corpus = [
    "The weather is beautiful and sunny today.",
    "A quick brown fox jumps over the lazy dog.",
    "Artificial intelligence and machine learning are transforming industries.",
    "I love cooking Italian food, especially pasta.",
    "It is a lovely, bright day outside.",
    "Deep learning models require a lot of data to train.",
    "Spaghetti and meatballs is a classic dish.",
    "There is no rain in the forecast for today, just clear skies."
]

# 3. Define the query sentence
query = "What a gorgeous, sunny day!"

# 4. Generate embeddings for the corpus and the query
corpus_embeddings = embedding_model.encode(corpus)
query_embedding = embedding_model.encode([query])[0]        

# 5. Compute cosine similarities between the query and each sentence in the corpus
cosine_similarities = np.dot(corpus_embeddings, query_embedding) / (np.linalg.norm(corpus_embeddings, axis=1) * np.linalg.norm(query_embedding))        

# 6. Find the index of the most similar sentence
most_similar_index = np.argmax(cosine_similarities)

# 7. Retrieve the most similar 3 sentence from the corpus
most_similar_indices = np.argsort(cosine_similarities)[-3:][::-1]
most_similar_sentences = [corpus[i] for i in most_similar_indices]

# 8. Print the most similar sentences
print("Most similar sentences to the query:")
for sentence in most_similar_sentences:
    print(sentence)
