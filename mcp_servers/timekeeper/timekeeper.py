from mcp.server.fastmcp import FastMCP
import asyncio
import time
from datetime import datetime
import argparse

mcp = FastMCP("Timekeeper Agent")

@mcp.tool()
async def get_current_time():
    """Get the current local time."""
    return datetime.now().isoformat()

@mcp.tool()
async def wait_for_duration(seconds: int):
    """
    Waits for a specified duration in seconds.
    Useful for creating delays in workflows.
    """
    print(f"Timekeeper: Waiting for {seconds} seconds...")
    await asyncio.sleep(seconds)
    return f"Time is up. Waited for {seconds} seconds."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--port", type=int, default=8002)
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Timekeeper on http://0.0.0.0:{args.port}/sse")
    elif args.transport == "streamable-http":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Timekeeper on http://0.0.0.0:{args.port}/mcp")

    mcp.run(transport=args.transport)
