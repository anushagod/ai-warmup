from google.adk.agents.llm_agent import Agent

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

# The instruction must be a plain string
SYSTEM_PROMPT = "Answer user questions to the best of your knowledge."

root_agent = Agent(
    model='gemini-3.6-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=SYSTEM_PROMPT,
    tools=[get_current_time]
)
