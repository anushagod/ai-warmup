from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. Define the Shared State (Agent Memory)
# Every key used inside the functions must be declared here!
class SharedState(TypedDict):
    raw_text: str          # Fixed: Added this key because it's passed in initial_state
    cleaned_text: str      # Fixed: Added this key because agent1 produces it and agent2 uses it
    final_text: str        # Fixed: Added this key to match your print statement at the end

# 2. Define the Agent Functions
def agent1(state: SharedState):
    print("[ADK Node 1] Cleaning whitespace...")
    # This dictionary payload will be cleanly merged into SharedState
    return {"cleaned_text": state["raw_text"].strip()}

# State after agent1 finishes:
#{
#    "raw_text": "   hello from sequential adk   ",
#    "cleaned_text": "hello from sequential adk"  # <-- Automatically added/merged
#}

def agent2(state: SharedState):
    print("[ADK Node 2] Converting to uppercase...")
    # This dictionary payload will be cleanly merged into SharedState
    return {"final_text": state["cleaned_text"].upper()}

# State after agent2 finishes:
#{
#    "raw_text": "   hello from sequential adk   ",
#    "cleaned_text": "hello from sequential adk",
#    "final_text": "HELLO FROM SEQUENTIAL ADK"  # <-- Automatically added/merged
#}

# 3. Define Sequential Graph
builder = StateGraph(SharedState)

# Register the nodes in the graph
builder.add_node("clean_text", agent1)
builder.add_node("uppercase_text", agent2)

# Define explicit linear paths (Edges)
builder.add_edge(START, "clean_text")
builder.add_edge("clean_text", "uppercase_text")
builder.add_edge("uppercase_text", END)

# Compile into an executable application
sequential_graph = builder.compile()

# 4. Execute the Graph
initial_state = {"raw_text": "   hello from sequential adk   "}
output = sequential_graph.invoke(initial_state)

# LangGraph creates the state object in memory and seeds it with your input dictionary. 
# At this exact moment, the central state looks like this:
# State at START:
#{
#    "raw_text": "   hello from sequential adk   "
#}

print(f"\nFinal Result: {output['final_text']}")
