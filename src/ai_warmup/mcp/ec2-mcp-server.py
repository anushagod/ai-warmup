import boto3
from botocore.exceptions import ClientError
from fastmcp import FastMCP 
import asyncio

#1. Initialize the FastMCP server
mcp = FastMCP("EC2 MCP Server")

#2. Define tools for the MCP server
@mcp.tool()
async def list_instances() -> list:
    ec2 = boto3.client("ec2")
    try:
        instances = ec2.describe_instances()
        return [str(instances)]
    except ClientError as e:
        return [f"Error describing EC2 instances: {e}"]

#3. Launch EC2 instance tool
@mcp.tool()
async def launch_ec2_instance(image_id: str, instance_type: str = "t2.micro") -> str:
    """Launches an Amazon EC2 instance using boto3."""
    ec2_client = boto3.client("ec2")
    try:
        response = ec2_client.run_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1
        )
        instance_id = response["Instances"][0]["InstanceId"]
        return f"Successfully launched EC2 instance: {instance_id}"
    except ClientError as e:
        return f"AWS Error: {e.response['Error']['Message']}"

if __name__ == "__main__":
    # Run as an HTTP/SSE server instead of standard input/output (stdio)
    # mcp.run(transport="sse")
    mcp.run(transport="streamable-http")