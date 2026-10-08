from google.adk.agents.llm_agent import Agent
from fastapi import FastAPI


# 1. Define a dummy tool to test your "Tool Trajectory" in evals
def check_order_status(order_id: str) -> str:
    """Checks the delivery status of a specific order ID."""
    if order_id == "12345":
        return "Shipped. Arriving tomorrow via FedEx."
    return "Order ID not found."

root_agent = Agent(
    model='gemini-3.5-flash',
    name='SupportAgent',
    description='A helpful customer support assistant.',
    instruction='You are a helpful customer support assistant. Always use tools to check order statuses.',
    tools=[check_order_status],
)

app = FastAPI()

@app.post("/chat")
async def chat(user_message: str):
    response = await root_agent.run(user_message)
    return {"response": response.text}