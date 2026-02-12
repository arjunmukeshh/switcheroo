import os
import time
import socket
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange

load_dotenv()

# Configuration
ESP32_HOSTNAME = "switcheroo.local."
ESP32_IP = os.getenv("ESP32_IP") 

class ESP32Listener:
    def __init__(self):
        self.address = None

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            self.address = socket.inet_ntoa(info.addresses[0])
            print(f"Discovered ESP32 at {self.address}")

    def update_service(self, zeroconf, type, name):
        pass

mcp = FastMCP("Servo Switch Controller")

@mcp.tool()
async def toggle_switch(state: str):
    """
    Toggle the physical wall switch via the ESP32 servo controller.
    :param state: The desired state, either 'on' or 'off'.
    Returns a message indicating the result of the operation.
    """
    if state.lower() not in ["on", "off"]:
        return "Error: State must be 'on' or 'off'"
    
    # Simple logic: Try ENV first, then default. 
    # Skipping blocking mDNS for now to ensure speed and reliability.
    ip = os.getenv("ESP32_IP", "192.168.0.101")
    
    base_url = f"http://{ip}"
    print(f"Attempting to toggle switch {state} at {base_url}...")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # The ESP32 endpoint expects a query parameter 'state'
            # Note: Using string concatenation for the URL to avoid any params encoding issues
            full_url = f"{base_url}/toggle?state={state.lower()}"
            print(f"HTTP Request: GET {full_url}")
            
            response = await client.get(full_url)
            print(f"Response: {response.text}")
            response.raise_for_status()
            
            # Try to parse JSON response, fallback to text if not JSON
            try:
                data = response.json()
                return f"Success: {data.get('message', 'Switch toggled')} (IP: {ip})"
            except ValueError:
                return f"Success: {response.text} (IP: {ip})"
                
    except httpx.TimeoutException:
        return f"Error: Connection to ESP32 at {ip} timed out."
    except httpx.ConnectError:
        return f"Error: Could not connect to ESP32 at {ip}."
    except httpx.HTTPStatusError as e:
        return f"Error: ESP32 returned status {e.response.status_code}."
    except Exception as e:
        return f"Error: {str(e)}"

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--port", type=int, default=5432)
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Servo MCP Server on http://0.0.0.0:{args.port}/sse")
    elif args.transport == "streamable-http":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Servo MCP Server on http://0.0.0.0:{args.port}/mcp")

    mcp.run(transport=args.transport)
