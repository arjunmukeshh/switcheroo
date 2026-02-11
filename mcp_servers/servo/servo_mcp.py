import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

ESP32_IP = os.getenv("ESP32_IP", "192.168.0.106")
BASE_URL = f"http://{ESP32_IP}"

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
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # The ESP32 endpoint expects a query parameter 'state'
            response = await client.get(f"{BASE_URL}/toggle", params={"state": state.lower()})
            response.raise_for_status()
            
            # Try to parse JSON response, fallback to text if not JSON
            try:
                data = response.json()
                return f"Success: {data.get('message', 'Switch toggled')}"
            except ValueError:
                return f"Success: {response.text}"
                
    except httpx.TimeoutException:
        return f"Error: Connection to ESP32 at {ESP32_IP} timed out."
    except httpx.ConnectError:
        return f"Error: Could not connect to ESP32 at {ESP32_IP}."
    except httpx.HTTPStatusError as e:
        return f"Error: ESP32 returned status {e.response.status_code}."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
