import asyncio
from google.adk.agents import Agent
from google.adk.tools import google_search, AgentTool
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-3.5-flash"
APP_NAME = "my_app"
USER_ID = "user_1"
SESSION_ID = "session"

web_search = Agent(
    name="web_search_agent",
    model=GEMINI_MODEL,
    description="You are a helpful agent that can answer questions using web search.",
    tools=[google_search],
)

root_agent = Agent(
    name="root_agent",
    model=GEMINI_MODEL,
    description="You are a helpful research assistant. You can use web search to answer",
    tools=[AgentTool(web_search)],
)

# Agent Runner
runner = InMemoryRunner(
    agent=root_agent,
    app_name=APP_NAME   
)


# create session for the runner
def create_session():
     session = asyncio.run(runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID
    ))
     return session;

print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# Define a convenience function to query the root_agent
def query_root_agent(session_id: str, prompt: str):
    print("** User:", prompt)
    response = runner.run(new_message=types.Content(
            role="user",
            parts=[types.Part(text=prompt)]), user_id=USER_ID, session_id=session_id)
    for message in response:
        if message.content.parts and message.content.parts[0].text:
            print(f'** {message.author}: {message.content.parts[0].text}')
            print()

# call the runner
session = create_session()
query_root_agent(session.id, "What is the capital of France?")
query_root_agent(session.id, "What is the capital of USA?")
