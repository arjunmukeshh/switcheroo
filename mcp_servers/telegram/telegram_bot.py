from mcp.server.fastmcp import FastMCP
import httpx
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Telegram Agent")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

@mcp.tool()
async def telegram_send(message: str):
    """
    Send a message to the user via Telegram.
    :param message: The text to send.
    """
    if not BOT_TOKEN or not CHAT_ID:
        return "Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in environment."

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return f"Message sent to Telegram: {message}"
        except Exception as e:
            return f"Failed to send Telegram message: {str(e)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "streamable-http"])
    parser.add_argument("--port", type=int, default=8005)
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Telegram Agent on http://0.0.0.0:{args.port}/sse")
    elif args.transport == "streamable-http":
        mcp.settings.port = args.port
        mcp.settings.host = "0.0.0.0"
        mcp.settings.transport_security = None
        print(f"Starting Telegram Agent on http://0.0.0.0:{args.port}/mcp")

    mcp.run(transport=args.transport)
