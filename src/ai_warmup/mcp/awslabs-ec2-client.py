import anyio
import os
import shutil
import sys

# --- THE ABSOLUTE ARGUMENT BYPASS ---
# We force uv run to use a modified startup flag that strips out the breaking 
# parameters before the server has a chance to execute its code.
SERVER_COMMAND = "uv"
SERVER_ARGS = [
    "run", 
    "--isolated",
    "--with", "mcp==1.28.1",
    "--with", "awslabs.ec2-mcp-server",
    "python", "-c", 
    "import sys; sys.argv = ['']; import awslabs.ec2_mcp_server.server"
]
# ------------------------------------

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_external_aws_mcp():
    if not shutil.which(SERVER_COMMAND):
        print(f"Error: '{SERVER_COMMAND}' binary not found in your system PATH.")
        return

    server_parameters = StdioServerParameters(
        command=SERVER_COMMAND,
        args=SERVER_ARGS,
        env={
            **os.environ,
            "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
        }
    )

    print("🚀 Launching external AWS server using isolated cache bypass...")
    
    async with stdio_client(server_parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("🔄 Initializing legacy handshake protocol...")
            await session.initialize()
            
            print("\n--- 🔧 External Tools Discovered ---")
            tools_response = await session.list_tools()
            
            if not tools_response.tools:
                print("No tools returned. Check your AWS CLI permissions.")
            else:
                for tool in tools_response.tools:
                    print(f"🔹 Name: {tool.name}")
                    print(f"   About: {tool.description}\n")

if __name__ == "__main__":
    anyio.run(run_external_aws_mcp)
