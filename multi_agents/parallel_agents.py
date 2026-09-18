from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END

#1. Define the Shared State (Agent Memory)
class MarketplaceState(TypedDict):
    product_id: str
    reviews: List[str]
    competitor_price: str

# 2. Define Independent Nodes
def fetch_reviews_node(state: MarketplaceState):
    print("[ADK Parallel Node A] Pulling customer reviews...")
    return {"reviews": ["Excellent build quality.", "Battery life is brief."]}

# state after fetch_reviews_node finishes:
#{
#    "product_id": "XYZ123",
#    "reviews": ["Excellent build quality.", "Battery life is brief."],  #<-- Automatically added/merged
#    "competitor_price": "" 

def fetch_pricing_node(state: MarketplaceState):
    print("[ADK Parallel Node B] Scraping competitor prices...")
    return {"competitor_price": "$89.99"}

# state after fetch_pricing_node finishes:
#{
#    "product_id": "XYZ123",       
#    "reviews": ["Excellent build quality.", "Battery life is brief."],
#    "competitor_price": "$89.99"  #<-- Automatically added/merged
#}  

def aggregate_summary_node(state: MarketplaceState):
    """This node acts as the Fan-In Join Block. It runs only after BOTH parallel tasks finish."""
    print("[ADK Aggregator Node] Compiling parallel findings...")
    summary = f"Product {state['product_id']} costs {state['competitor_price']} with {len(state['reviews'])} reviews collected."
    return {"product_id": f"{state['product_id']} (Processed: {summary})"}

# state after aggregate_summary_node finishes:
#{
#    "product_id": "XYZ123 (Processed: Product XYZ123 costs $89.99 with 2 reviews collected.)",  #<-- Automatically added/merged
#    "reviews": ["Excellent build quality.", "Battery life is brief."],
#    "competitor_price": "$89.99"
#}

# 3. Define Parallel Graph
builder = StateGraph(MarketplaceState)

builder.add_node("get_reviews", fetch_reviews_node)
builder.add_node("get_pricing", fetch_pricing_node)
builder.add_node("aggregator", aggregate_summary_node)

# Create parallel branching (Fan-out) from START
builder.add_edge(START, "get_reviews")
builder.add_edge(START, "get_pricing")

# Route both paths to the same node (Fan-in / Join)
builder.add_edge("get_reviews", "aggregator")
builder.add_edge("get_pricing", "aggregator")

builder.add_edge("aggregator", END)

parallel_agents_graph = builder.compile()

#4 Run the parallel graph
initial_state = {"product_id": "XYZ123", "reviews": [], "competitor_price": ""}
output = parallel_agents_graph.invoke(initial_state)   

# LangGraph creates the state object in memory and seeds it with your input dictionary. 
# At this exact moment, the central state looks like this:
# State at START:
#{
#    "product_id": "XYZ123",
#    "reviews": [],
#    "competitor_price": ""
#}

#5 Print the final state after execution
print("\nFinal State after Parallel Execution:")
print(f"Product ID: {output['product_id']}")    