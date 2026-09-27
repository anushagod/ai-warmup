from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import BuiltInCodeExecutor

root_agent = Agent(
    model='gemini-3.5-flash',
    name='code_agent',
    description='A helpful code assistant.',
    instruction='You are a helpful code assistant.',
    tools=[BuiltInCodeExecutor],
)
