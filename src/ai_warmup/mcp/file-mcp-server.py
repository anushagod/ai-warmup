import os
from fastmcp import FastMCP

#1. initialize the MCP server
mcp = FastMCP("file-manager-server")

#2. define the tools for the MCP server
#tool1: List files in a directory
@mcp.tool()
def list_files(directory_path: str = ".") -> str:
    """
    Lists all files and folders inside the specified directory path.
    Defaults to the current directory ('.') if no path is provided.
    """
    try:
        if not os.path.exists(directory_path):
            return f"Error: Path '{directory_path}' does not exist."
            
        items = os.listdir(directory_path)
        if not items:
            return f"The directory '{directory_path}' is empty."
            
        # Format the items cleanly for the LLM
        lines = [f"Contents of {os.path.abspath(directory_path)}:"]
        for item in sorted(items):
            prefix = "📁" if os.path.isdir(os.path.join(directory_path, item)) else "📄"
            lines.append(f"{prefix} {item}")
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

# 3. Tool 2: View File Content
@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Reads and returns the text content of a specific file.
    Use this when you need to inspect what is written inside a file.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
            
        if os.path.isdir(file_path):
            return f"Error: '{file_path}' is a directory. Use list_files to read it."
            
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        return f"--- Content of {file_path} ---\n{content}\n--- End of File ---"
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
#4. run mcp
if __name__ == "__main__":
    mcp.run()
