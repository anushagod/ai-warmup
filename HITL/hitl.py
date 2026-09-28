import asyncio
from google.genai import types
from google.adk import Workflow
from google.adk.events import RequestInput
from google.adk.runners import InMemoryRunner
from google.adk.workflow import START

# 1. Define nodes for the graph
def step1():
    yield RequestInput(
        message="Please enter a number to double: "
    )

def step2(node_input):
    if isinstance(node_input, dict):
        value = node_input.get("response") or next(iter(node_input.values()))
    else:
        value = node_input

    return f"The doubled result is: {int(value) * 2}"

# 2. Define the workflow
root_agent = Workflow(
    name="HITL_Workflow",
    edges=[(START, step1, step2)]
)

APP_NAME = "HITL_Workflow"
USER_ID = "user_1"
SESSION_ID = "session"

runner = InMemoryRunner(
    agent=root_agent,
    app_name=APP_NAME   
)

# 3. Execution Main loop
async def main():
    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    print("--> Sending 'start' message to runner...")
    current_payload = types.Content(role="user", parts=[types.Part(text="start")])
    while True:
        has_more_steps = False
        async for event in runner.run_async(
            new_message=current_payload, 
            user_id=USER_ID, 
            session_id=SESSION_ID
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call and part.function_call.name == "adk_request_input":
                        call_id = part.function_call.id
                        prompt_msg = part.function_call.args.get("message", "Please enter a number to double: ")
                        print(f"\n[System Prompt]: {prompt_msg}")
                        user_input = input("Your Input >> ")
                        current_payload = types.Content(
                            role="user",
                            parts=[
                                types.Part(
                                    function_response=types.FunctionResponse(
                                        name="adk_request_input",
                                        id=call_id,
                                        response={"response": user_input}
                                    )
                                )
                            ]
                        )
                        has_more_steps = True
                        break
            
            # Print output directly when step2 completes its final execution frames
            if event.output:
                print(f"\n[Result]: {event.output}")
        
        if not has_more_steps:
            break

    print("\n--> Workflow execution completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
