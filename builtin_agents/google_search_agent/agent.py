from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

root_agent = Agent(
    model='gemini-3.5-flash',
    name='google_search_agent',
    description='A helpful google search assistant.',
    instruction='You are a helpful google search assistant.',
    tools=[google_search],
)
