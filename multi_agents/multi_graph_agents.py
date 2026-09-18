import random
from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END

#1 Define the Shared State (Agent Memory)
class UnifiedState(TypedDict):
    # Sequential variables
    topic: str
    
    # Parallel variables
    facts_data: List[str]
    trends_data: List[str]
    
    # Looping variables
    combined_summary: str
    quality_score: float
    review_attempts: int

#2 Define the Agent Functions
# Sequential Node
def single_supervisor_agent(state: UnifiedState):
    print("\n[Node 1: Supervisor] Initializing master workflow...")
    return {
        "topic": "Autonomous Electric Vehicles",
        "review_attempts": 0
    }
# State after single_supervisor_agent finishes:
#{
#    "topic": "Autonomous Electric Vehicles",  #<-- Automatically added/merged
#    "facts_data": [],                          #<-- Initialized empty list
#    "trends_data": [],                         #<-- Initialized empty list
#    "combined_summary": "",                    #<-- Initialized empty string
#    "quality_score": 0.0,                      #<-- Initialized to zero
#    "review_attempts": 0                       #<-- Initialized to zero

# Parallel Nodes
def facts_research_agent(state: UnifiedState):
    print(f"[Node 2A: Facts Agent] Collecting physical metrics for: {state['topic']}...")
    return {"facts_data": ["Solid-state battery tech active", "0-60 mph dropped under 2 seconds"]}

# state after facts_research_agent finishes:
#{
#    "topic": "Autonomous Electric Vehicles",
#    "facts_data": ["Solid-state battery tech active", "0-60 mph dropped under 2 seconds"],  #<-- Automatically added/merged
#    "trends_data": [],                          #<-- Initialized empty list
#    "combined_summary": "",                    #<-- Initialized empty string
#    "quality_score": 0.0,                      #<-- Initialized to zero
#    "review_attempts": 0                       #<-- Initialized to zero    

def trends_research_agent(state: UnifiedState):
    print(f"[Node 2B: Trends Agent] Analyzing market velocity for: {state['topic']}...")
    return {"trends_data": ["Fleet adoption up 40%", "High consumer demand in urban centers"]}

# state after trends_research_agent finishes:
#{
#    "topic": "Autonomous Electric Vehicles",
#    "facts_data": ["Solid-state battery tech active", "0-60 mph dropped    under 2 seconds"],  #<-- Automatically added/merged
#    "trends_data": ["Fleet adoption up 40%", "High consumer demand in urban centers"],  #<-- Automatically added/merged
#    "combined_summary": "",                    #<-- Initialized empty string
#    "quality_score": 0.0,                      #<-- Initialized to zero
#    "review_attempts": 0                       #<-- Initialized to zero        

# Looping Node
def synthesizer_agent(state: UnifiedState):
    print("[Node 3: Synthesizer] Blending multi-agent data streams into a draft summary...")
    facts = ", ".join(state.get("facts_data", []))
    trends = ", ".join(state.get("trends_data", []))
    
    # In a loop, this dynamically overwrites with an upgraded version
    return {"combined_summary": f"Report on {state['topic']}. Milestones: [{facts}]. Market: [{trends}]."}

# state after synthesizer_agent finishes:
#{
#    "topic": "Autonomous Electric Vehicles",
#    "facts_data": ["Solid-state battery tech active", "0-60 mph dropped under 2 seconds"],
#    "trends_data": ["Fleet adoption up 40%", "High consumer demand in urban centers"],
#    "combined_summary": "Report on Autonomous Electric Vehicles. Milestones: [Solid-state battery tech active, 0-60 mph dropped under 2 seconds]. Market: [Fleet adoption up 40%, High consumer demand in urban centers].",  #<-- Automatically added/merged
#    "quality_score": 0.0,                      #<-- Initialized to zero
#    "review_attempts": 0                       #<-- Initialized to zero    

def quality_reviewer_agent(state: UnifiedState):
    current_attempts = state.get("review_attempts", 0) + 1
    
    # Simulate a score that improves if it forces a rewrite
    score = random.uniform(0.6, 0.8) if current_attempts < 2 else 0.95
    print(f"[Node 4: Reviewer] Testing document quality (Attempt #{current_attempts}). Score: {round(score, 2)}")
    
    return {"quality_score": score, "review_attempts": current_attempts}

# state after quality_reviewer_agent finishes:
#{
#    "topic": "Autonomous Electric Vehicles",
#    "facts_data": ["Solid-state battery tech active", "0-60 mph dropped    under 2 seconds"],
#    "trends_data": ["Fleet adoption up 40%", "High consumer demand in urban centers"],
#    "combined_summary": "Report on Autonomous Electric Vehicles. Milestones: [Solid-state battery tech active, 0-60 mph dropped under 2 seconds]. Market: [Fleet adoption up 40%, High consumer demand in urban centers].",
#    "quality_score": 0.95,  #<-- Randomly determined based on attempts
#    "review_attempts": 2       #<-- Incremented attempt count  

# 3. DEFINE THE CONDITIONAL ROUTING EDGE
def quality_router_edge(state: UnifiedState) -> str:
    """Evaluates the reviewer agent metrics to loop or exit."""
    if state["quality_score"] >= 0.85:
        print(" -> Router: Quality standard met! Sending to exit.")
        return "accept_and_end"
    else:
        print(" -> Router: Quality threshold missed. Redirecting to Synthesizer for rewriting...")
        return "reject_and_retry"

# state after quality_router_edge finishes:
#{
#    "topic": "Autonomous Electric Vehicles",
#    "facts_data": ["Solid-state battery tech active", "0-60 mph dropped under 2 seconds"],
#    "trends_data": ["Fleet adoption up 40%", "High consumer demand in urban centers"],
#    "combined_summary": "Report on Autonomous Electric Vehicles. Milestones: [Solid-state battery tech active, 0-60 mph dropped under 2 seconds]. Market: [Fleet adoption up 40%, High consumer demand in urban centers].",
#    "quality_score": 0.95,  #<-- Randomly determined based on attempts
#    "review_attempts": 2       #<-- Incremented attempt count  

# 4. Define the Multi-Graph Workflow
builder = StateGraph(UnifiedState)

# Register all nodes
builder.add_node("supervisor", single_supervisor_agent)
builder.add_node("facts_agent", facts_research_agent)
builder.add_node("trends_agent", trends_research_agent)
builder.add_node("synthesizer", synthesizer_agent)
builder.add_node("reviewer", quality_reviewer_agent)

# Step A: Sequential entry
builder.add_edge(START, "supervisor")

# Step B: Parallel Fan-Out (Multi-Agent Research)
builder.add_edge("supervisor", "facts_agent")
builder.add_edge("supervisor", "trends_agent")

# Step C: Parallel Fan-In (Join at the Synthesizer)
builder.add_edge("facts_agent", "synthesizer")
builder.add_edge("trends_agent", "synthesizer")

# Step D: Move to Reviewer
builder.add_edge("synthesizer", "reviewer")

# Step E: Evaluate Loop
builder.add_conditional_edges(
    "reviewer",
    quality_router_edge,
    {
        "reject_and_retry": "synthesizer",  # Loops backwards to synthesize a new draft
        "accept_and_end": END               # Finishes the program
    }
)

# Compile the application
orchestrator_graph = builder.compile()

# 5. EXECUTE THE SYSTEM
if __name__ == "__main__":
    # Fire up the composite graph with empty initial arguments
    final_output = orchestrator_graph.invoke({})

# State at Start
#{
#    "topic": "Autonomous Electric Vehicles",
#    "facts_data": [],
#    "trends_data": [],
#    "combined_summary": "",
#    "quality_score": 0.0,
#    "review_attempts": 0
#}

# State at END (after all loops and merges)
#{
#   "topic": "Autonomous Electric Vehicles",
#  "facts_data": ["Solid-state battery tech active", "0-60 mph dropped under 2 seconds"],
#  "trends_data": ["Fleet adoption up 40%", "High consumer demand in urban centers"],
#  "combined_summary": "Report on Autonomous Electric Vehicles. Milestones: [Solid-state battery tech active, 0-60 mph dropped under 2 seconds]. Market: [Fleet adoption up 40%, High consumer demand in urban centers].",
#  "quality_score": 0.95,
# "review_attempts": 2
#}
    
    print("\n==========================================")
    print("FINAL WORKFLOW OUTPUT SCHEMA:")
    print(f"Total Review Passes: {final_output['review_attempts']}")
    print(f"Final Accepted Document: {final_output['combined_summary']}")