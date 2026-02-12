import os
import asyncio
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Note: In the gateway, we don't strictly need CHAT_ID since we respond to incoming messages,
# but we can use it to restrict access to only the user.
ALLOWED_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

ARCHESTRA_AGENT_ID = os.getenv("ARCHESTRA_AGENT_ID")
ARCHESTRA_API_KEY = os.getenv("ARCHESTRA_API_KEY")
ARCHESTRA_BASE_URL = os.getenv("ARCHESTRA_BASE_URL", "http://localhost:9000")

async def forward_to_archestra(text: str):
    """
    Sends a message to the Archestra A2A agent and waits for the response.
    """
    url = f"{ARCHESTRA_BASE_URL}/v1/a2a/{ARCHESTRA_AGENT_ID}"
    headers = {
        "Authorization": f"Bearer {ARCHESTRA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "message": {
                "parts": [{"kind": "text", "text": text}]
            },
            "wait": True  # Enable synchronous waiting for the agent's response
        }
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            print(f"Gateway: Sending to Archestra: {text}")
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            print(f"Gateway: Archestra Raw Response: {data}")
            
            # Log to file for debugging
            with open("gateway_debug.log", "a") as f:
                f.write(f"\n--- Response ---\n{data}\n")
            
            if "result" in data:
                result = data["result"]
                
                # Check if 'result' IS the message object (has 'parts')
                if "parts" in result:
                    parts = result.get("parts", [])
                    reply_text = "".join([p.get("text", "") for p in parts if p.get("kind") == "text"])
                    return reply_text
                    
                # Fallback: Check if it's nested under 'message' or 'messages'
                elif "message" in result:
                     parts = result["message"].get("parts", [])
                     reply_text = "".join([p.get("text", "") for p in parts if p.get("kind") == "text"])
                     return reply_text
                     
                elif "messages" in result:
                    # Previous logic for list of messages
                    messages = result["messages"]
                    assistant_replies = [m for m in messages if m.get("role") == "agent" or m.get("role") == "assistant"]
                    if assistant_replies:
                        last_reply = assistant_replies[-1]
                        parts = last_reply.get("parts", [])
                        reply_text = "".join([p.get("text", "") for p in parts if p.get("kind") == "text"])
                        return reply_text
            
            return "Archestra processed the message but returned no text reply."
            
        except httpx.HTTPStatusError as e:
            return f"Archestra API Error: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"Gateway Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Callback for incoming Telegram messages.
    """
    user_text = update.message.text
    chat_id = str(update.effective_chat.id)
    
    # Optional Security: Only respond to the authorized user
    if ALLOWED_CHAT_ID and chat_id != str(ALLOWED_CHAT_ID):
        print(f"Gateway: Unauthorized access attempt from Chat ID {chat_id}")
        return

    if not user_text:
        return

    # Send a typing indicator or "Processing..." message if needed
    placeholder_msg = await update.message.reply_text("Thinking...")

    # Forward to Archestra
    reply_from_archestra = await forward_to_archestra(user_text)

    # Send the reply back to Telegram
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=placeholder_msg.message_id,
        text=reply_from_archestra
    )

if __name__ == "__main__":
    if not BOT_TOKEN or not ARCHESTRA_AGENT_ID or not ARCHESTRA_API_KEY:
        print("Error: Missing environment variables. Check .env file.")
        exit(1)

    print(f"Starting Telegram-Archestra Gateway Bot...")
    print(f"Target Agent: {ARCHESTRA_AGENT_ID}")

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Listen for all text messages
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(text_handler)
    
    application.run_polling()
