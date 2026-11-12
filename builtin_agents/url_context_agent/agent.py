from google.adk.agents.llm_agent import Agent
from google.adk.tools.url_context_tool import url_context

root_agent = Agent(
    model='gemini-3.5-flash',
    name='web_reader_agent',
    description='A helpful assistant for user questions.',
    instruction="Read the provided URLs and answer the user's questions based on their content.",
    tools=[url_context],
)
