import asyncio
import os
from mcp.server.fastmcp import FastMCP
from pywizlight import wizlight, PilotBuilder, discovery
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BULB_IP = os.getenv("WIZ_BULB_IP")

mcp = FastMCP("Wiz Bulb Server")

async def get_light(ip_address: str = None):
    """Helper to initialize a light object."""
    ip = ip_address or DEFAULT_BULB_IP
    if not ip:
        raise ValueError("No IP address provided and WIZ_BULB_IP not set in environment")
    return wizlight(ip)

@mcp.tool()
async def discover_bulbs():
    """
    Discover Wiz bulbs on the local network.
    Returns a list of discovered bulbs with their IP and MAC addresses.
    """
    try:
        bulbs = await discovery.discover_lights(broadcast_space="255.255.255.255")
        return [{"ip": b.ip, "mac": b.mac} for b in bulbs]
    except Exception as e:
        return f"Error during discovery: {str(e)}"

@mcp.tool()
async def turn_on(ip_address: str = None, brightness: int = 255):
    """
    Turn on a Wiz bulb.
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    :param brightness: Brightness level (0-255). Default is 255.
    """
    try:
        ip = ip_address or DEFAULT_BULB_IP
        if not ip:
            return "Error: No IP."
        light = wizlight(ip)
        # Explicit pilot builder purely for brightness
        await light.turn_on(PilotBuilder(brightness=brightness))
        return f"Bulb {ip} turned on with brightness {brightness}"
    except Exception as e:
        return f"Error turning on bulb: {str(e)}"

@mcp.tool()
async def turn_off(ip_address: str = None):
    """
    Turn off a Wiz bulb.
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    """
    try:
        light = await get_light(ip_address)
        await light.turn_off()
        ip = ip_address or DEFAULT_BULB_IP
        return f"Bulb {ip} turned off"
    except Exception as e:
        return f"Error turning off bulb: {str(e)}"

@mcp.tool()
async def set_color(r: int, g: int, b: int, ip_address: str = None):
    """
    Set the RGB color of a Wiz bulb.
    :param r: Red component (0-255).
    :param g: Green component (0-255).
    :param b: Blue component (0-255).
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    """
    try:
        ip = ip_address or DEFAULT_BULB_IP
        if not ip:
            return "Error: No IP address provided and WIZ_BULB_IP not set."
            
        light = wizlight(ip)
        # Using PilotBuilder explicitly for RGB
        await light.turn_on(PilotBuilder(rgb=(r, g, b)))
        return f"Bulb {ip} set to color RGB({r}, {g}, {b})"
    except Exception as e:
        return f"Error setting color: {str(e)}"

@mcp.tool()
async def flash_bulb(times: int = 1, color_rgb: tuple[int, int, int] = (255, 0, 0), delay_seconds: float = 0.5):
    """
    Flash the bulb a specified number of times with a specific color.
    :param times: Number of times to flash.
    :param color_rgb: Tuple of (r, g, b) for the flash color. Default Red.
    :param delay_seconds: Time on/off in seconds.
    """
    try:
        ip = DEFAULT_BULB_IP
        if not ip:
            return "Error: WIZ_BULB_IP not set."
            
        light = wizlight(ip)
        
        for i in range(times):
            # Turn ON with color
            await light.turn_on(PilotBuilder(rgb=color_rgb))
            await asyncio.sleep(delay_seconds)
            
            # Turn OFF (or dim) - turning off is clearer for a flash
            await light.turn_off()
            await asyncio.sleep(delay_seconds)
            
        return f"Bulb flashed {times} times."
    except Exception as e:
        return f"Error flashing bulb: {str(e)}"

@mcp.tool()
async def set_warmth(kelvin: int, ip_address: str = None):
    """
    Set the color temperature of a Wiz bulb.
    :param kelvin: Color temperature in Kelvin (2700-6500).
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    """
    try:
        light = await get_light(ip_address)
        await light.turn_on(PilotBuilder(kelvin=kelvin))
        ip = ip_address or DEFAULT_BULB_IP
        return f"Bulb {ip} set to temperature {kelvin}K"
    except Exception as e:
        return f"Error setting warmth: {str(e)}"

@mcp.tool()
async def get_status(ip_address: str = None):
    """
    Get the current status (on/off, brightness, color) of a Wiz bulb.
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    """
    try:
        light = await get_light(ip_address)
        state = await light.updateState()
        return {
            "on": state.get_state(),
            "brightness": state.get_brightness(),
            "rgb": state.get_rgb(),
            "temp": state.get_colortemp(),
            "mac": light.mac
        }
    except Exception as e:
        return f"Error getting status: {str(e)}"

@mcp.tool()
async def breathing(r: int = 255, g: int = 255, b: int = 255, ip_address: str = None, speed: int = 100, brightness: int = 255):
    """
    Start the breathing (Pulse) effect on the bulb with a specific color.
    :param r: Red component (0-255).
    :param g: Green component (0-255).
    :param b: Blue component (0-255).
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    :param speed: The speed of the effect (10-200). Default is 100.
    :param brightness: Brightness level (0-255). Default is 255.
    """
    try:
        light = await get_light(ip_address)
        # Scene 31 is the 'Pulse' effect which looks like breathing
        await light.turn_on(PilotBuilder(rgb=(r, g, b), scene=31, speed=speed, brightness=brightness))
        ip = ip_address or DEFAULT_BULB_IP
        return f"Bulb {ip} set to breathing effect (Pulse) with color RGB({r}, {g}, {b}) and speed {speed}"
    except Exception as e:
        return f"Error setting breathing effect: {str(e)}"

@mcp.tool()
async def strobe(ip_address: str = None, speed: int = 100, brightness: int = 255):
    """
    Start a strobe effect on the bulb using the built-in 'Party' scene.
    This effect cycles through colors rapidly.
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    :param speed: The speed of the strobe (10-200). Default is 100.
    :param brightness: Brightness level (0-255). Default is 255.
    """
    try:
        light = await get_light(ip_address)
        # Scene 4 is 'Party' which provides a multi-color strobe effect.
        await light.turn_on(PilotBuilder(scene=4, speed=speed, brightness=brightness))
        ip = ip_address or DEFAULT_BULB_IP
        return f"Bulb {ip} set to strobe effect (Party scene) with speed {speed}"
    except Exception as e:
        return f"Error setting strobe effect: {str(e)}"

@mcp.tool()
async def manual_strobe(r: int = 255, g: int = 255, b: int = 255, ip_address: str = None, hz: float = 5.0, duration_seconds: float = 10.0):
    """
    Start a manual strobe effect with a specific color.
    Note: High frequencies may be limited by network latency.
    :param r: Red component (0-255).
    :param g: Green component (0-255).
    :param b: Blue component (0-255).
    :param ip_address: The IP address of the bulb. Defaults to WIZ_BULB_IP env var.
    :param hz: Frequency of the strobe in Hertz (flashes per second). Default 5.0.
    :param duration_seconds: Total duration of the strobe effect. Default 10.0.
    """
    try:
        light = await get_light(ip_address)
        ip = ip_address or DEFAULT_BULB_IP
        period = 1.0 / hz / 2.0
        num_cycles = int(duration_seconds * hz)
        
        for _ in range(num_cycles):
            await light.turn_on(PilotBuilder(rgb=(r, g, b)))
            await asyncio.sleep(period)
            await light.turn_off()
            await asyncio.sleep(period)
            
        return f"Manual strobe effect completed on {ip}"
    except Exception as e:
        return f"Error with manual strobe effect: {str(e)}"

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Wiz Bulb MCP Server on http://0.0.0.0:{args.port}/sse")
    elif args.transport == "streamable-http":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Wiz Bulb MCP Server on http://0.0.0.0:{args.port}/mcp")

    mcp.run(transport=args.transport)
