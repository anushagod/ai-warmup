import os
import sys  
import json
import asyncio

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from litellm import completion

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ Error: Missing OpenAI API key in .env file.")
    sys.exit(1)

async def run_agent_loop(model_name: str, user_prompt: str):
    # 1. Connect to the running SSE MCP Server (ensure your server script is running!)
    async with streamable_http_client("http://localhost:8000/mcp") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize connection with the MCP server
            await session.initialize()
            
            # 2. Fetch available tools dynamically from the server
            mcp_tools_response = await session.list_tools()
            
            # Format MCP tools into the precise function schema OpenAI expects
            openai_formatted_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema  # ✅ Fixed property name
                    }
                }
                for tool in mcp_tools_response.tools
            ]

            print(f"🤖 [Agent]: Initializing task -> '{user_prompt}'")
            
            # 3. Send prompt and structural tools to OpenAI via LiteLLM
            messages = [{"role": "user", "content": user_prompt}]
            response = completion(
                model=model_name,
                messages=messages,
                tools=openai_formatted_tools
            )

            response_message = response.choices[0].message
            
            # 4. Agent Loop: Check if OpenAI requested a tool call
            if response_message.tool_calls:
                # Format response_message properly as a dict for LiteLLM conversation history
                messages.append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in response_message.tool_calls
                    ]
                })
                
                # Execute each requested tool call
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = tool_call.function.arguments  # JSON string
                    tool_call_id = tool_call.id

                    print(f"🔌 [Agent]: OpenAI requested tool '{tool_name}' with args: {tool_input}")

                    # Convert string arguments into a dictionary for the MCP Python session
                    arguments_dict = json.loads(tool_input)

                    # 5. Execute the local python tool via the MCP Session
                    tool_result = await session.call_tool(tool_name, arguments=arguments_dict)
                    
                    # Extract pure text safely from the MCP TextContent object list
                    extracted_text = tool_result.content[0].text
                    print(f"📦 [Agent]: Tool output received: {extracted_text}")

                    # 6. Append the actual execution results back to OpenAI's conversation tree
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": extracted_text
                    })

                # 7. Feed execution data back to OpenAI to get the final natural wording
                final_response = completion(
                    model=model_name,
                    messages=messages,
                    tools=openai_formatted_tools
                )
                print(f"\n💬 [OpenAI Final Answer]: {final_response.choices[0].message.content}")
            else:
                # If OpenAI resolved the query directly without calling infrastructure
                print(f"\n💬 [OpenAI Final Answer]: {response_message.content}")

if __name__ == "__main__":
    prompt = "Hey! Please spin up a t2.micro instance using AMI ami-0c7217cdde317cfec"
    asyncio.run(run_agent_loop("openai/gpt-4o", prompt))
