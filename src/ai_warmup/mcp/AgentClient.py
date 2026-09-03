import os
import sys
import asyncio

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()       

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("❌ Error: Missing OpenAI API key in .env file.")
    sys.exit(1)


async def server_call():
    # 1. Point to your local server script
    server_params = StdioServerParameters(
        command="python", 
        args=["./src/ai_warmup/mcp/file-mcp-server.py"]
    )

    print("🤖 Client Agent: Starting and connecting to the MCP Server...")
    
    # 2. Connect to the MCP Server via stdio
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 3. Initialize the session protocol handshake
            await session.initialize()
            print("🤖 Client Agent: Successfully initialized the MCP session.")

            # 4. Discover what tools the server provides
            available_tools = await session.list_tools()
            print("🤖 Client Agent: Available tools:")
            
            # FIXED: Access attributes directly using object dot-notation (.name, .description)
            for tool in available_tools.tools:
                print(f"   - {tool.name}: {tool.description}")

            # 5. Execute the 'list_files' tool call
            print("\n🚀 Agent calling tool: 'list_files' for directory '.'...")
            
            result = await session.call_tool(
                name="list_files",  # Matching the name exposed by your file-manager-server
                arguments={"directory_path": "."}
            )

            # 6. Display the server's response content
            print("\n🖥️ Response received from MCP Server:")
            print(result.content[0].text)


if __name__ == "__main__":
    # Run the async main loop
    asyncio.run(server_call())
