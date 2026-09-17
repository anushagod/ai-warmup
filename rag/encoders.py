import warnings
# Suppress the specific google-genai AFC warning
warnings.filterwarnings(
    "ignore", 
    message=".*Direct use of automatic function calling.*"
)

import asyncio
import numpy as np

from sentence_transformers import SentenceTransformer, CrossEncoder
from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv("../.env")

# 1. Initialize the embedding and cross-encoder models
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
cross_encoder_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

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

# 3. Define the query sentence for initial retrieval
query = "What a gorgeous, sunny day!"

# 4. Generate embeddings for the corpus and the query
corpus_embeddings = embedding_model.encode(corpus)
query_embedding = embedding_model.encode(query)

# 5. Compute cosine similarities between the query and each sentence in the corpus
cosine_similarities = np.dot(corpus_embeddings, query_embedding) / (
    np.linalg.norm(corpus_embeddings, axis=1) * np.linalg.norm(query_embedding)
)

# 6 & 7. Extract candidates
top_k = 3
candidate_indices = np.argsort(cosine_similarities)[-top_k:][::-1]
candidate_sentences = [corpus[i] for i in candidate_indices]

# 8. Print the most similar sentences
print("Most similar sentences to the query:")
for sentence in candidate_sentences:
    print(sentence)

# 9. Use CrossEncoder to re-rank the candidate sentences
cross_encoder_input = [[query, sentence] for sentence in candidate_sentences]
cross_encoder_scores = cross_encoder_model.predict(cross_encoder_input)
reranked_indices = np.argsort(cross_encoder_scores)[::-1]
final_sentences = [candidate_sentences[i] for i in reranked_indices]

# 10. Print the final re-ranked sentences
print("\nRe-ranked sentences based on CrossEncoder scores:")
for sentence in final_sentences:
    print(sentence)


# =====================================================================
# ADK 2.8 GENERATION BLOCK (All in the same file)
# =====================================================================

# 11. Initialize the LLM agent using ADK 2.8
retrieval_agent = Agent(
    model='gemini-3.6-flash',
    name='retrieval_agent',
    description='Answers user queries based exclusively on retrieved context sentences.',
    instruction='''
    You are a retrieval-augmented generation assistant. Your goal is to answer the user query clearly and briefly. 
    Rely strictly on the provided "Retrieved Context" sentences.
    '''
)

# 12. Prepare the retrieved context for the LLM agent
retrieved_context = "\n".join([f"- {sent}" for sent in final_sentences])

# 13. Define the user query for the LLM agent
user_query = "Can you tell me about the weather today?"

# 14. Create the prompt for the LLM agent
prompt = f"""
User Query: {user_query}
Retrieved Context: {retrieved_context}
Please provide a concise answer based on the retrieved context.
"""

# 15 & 16. Define an asynchronous function to execute via the ADK 2.8 Runner pipeline
async def run_adk_agent():
    # Set up the internal memory tracking needed by ADK 2.8
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name='rag_app', user_id='user_1')
    
    # Initialize the Runner to orchestrate the generation loop
    runner = Runner(
        agent=retrieval_agent,
        app_name='rag_app',
        session_service=session_service
    )
    
    # Convert input text into the ADK compliant Content structure
    content = types.Content(
        role='user',
        parts=[types.Part.from_text(text=prompt)]
    )
    
    print("\nResponse from the LLM agent:")
    
    # Stream the execution events from the runner loop
    async for event in runner.run_async(
        session_id=session.id,  # Fixed: changed session_id to id
        user_id=session.user_id,
        new_message=content
    ):

        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="")
    print()

# Kick off the async event loop execution
asyncio.run(run_adk_agent())
