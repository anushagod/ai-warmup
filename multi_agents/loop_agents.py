import random
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

#1 Define the Shared State (Agent Memory)
class CodingState(TypedDict):
    code_snippet: str
    bug_found: bool
    attempts: int

# 2. Define the Agent Functions
def test_code_node(state: CodingState):
    current_attempts = state.get("attempts", 0) + 1
    # Simulate finding bugs, resolving on the 3rd attempt
    still_has_bug = random.choice([True, False]) if current_attempts < 3 else False
    
    print(f"[ADK Node] Evaluation Attempt #{current_attempts}. Bugs present? {still_has_bug}")
    return {"attempts": current_attempts, "bug_found": still_has_bug}

# state after test_code_node finishes:
#{
#    "code_snippet": "def main(): print('ADK')",
#    "bug_found": True,  #<-- Randomly determined based on attempts
#    "attempts": 1       #<-- Incremented attempt count 

# 3. Define the Conditional Routing Edge Logic
def router_edge(state: CodingState) -> str:
    """Evaluates the application state and returns the string name of the next destination."""
    if state["bug_found"]:
        print(" -> Router: Quality bar missed. Cycling back to test node...")
        return "re_test"  # Maps back to the test node
    else:
        print(" -> Router: Quality bar met! Routing to exit.")
        return "exit_workflow"  # Maps to END

# state after router_edge finishes:
#{
#    "code_snippet": "def main(): print('ADK')",
#    "bug_found": False,  #<-- Determined by test_code_node
#    "attempts": 3        #<-- Incremented attempt count    

# 4. Define the Looping Graph
builder = StateGraph(CodingState)
builder.add_node("evaluate_code", test_code_node)

# Wire the entrypoint
builder.add_edge(START, "evaluate_code")

# Register the conditional routing logic
builder.add_conditional_edges(
    "evaluate_code",     # The node where the decision is made
    router_edge,         # The routing function
    {
        "re_test": "evaluate_code",  # If router returns 're_test', loop back to evaluate_code
        "exit_workflow": END         # If router returns 'exit_workflow', route to END
    }
)

looping_agent = builder.compile()

# 5. Run the Looping Workflow
output = looping_agent.invoke({"code_snippet": "def main(): print('ADK')", "bug_found": True, "attempts": 0})

# LangGraph creates the state object in memory and seeds it with your input dictionary.
# At this exact moment, the central state looks like this:
# State at START:
#{
#    "code_snippet": "def main(): print('ADK')",
#    "bug_found": True, 
#    "attempts": 0
#}

print(f"\nFinal Graph State: {output}")
