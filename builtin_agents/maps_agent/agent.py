from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_maps_grounding

root_agent = Agent(
    model='gemini-3.8-flash', 
    name="maps_agent",
    description="An AI agent capable of looking up local businesses, places, and spatial details using Google Maps data.",
    instruction='Answer user questions to the best of your knowledge.',
    tools=[google_maps_grounding], 
)
