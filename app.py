#!/usr/bin/env python3
"""
AI Chat - Clean Conversational AI Interface
Chat with OpenAI's GPT models through a beautiful interface
"""

import os
import asyncio
import aiohttp
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ai-chat-dev-key")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEMO_MODE = not OPENAI_API_KEY

# Store conversation history (in-memory, would use database in production)
conversations = {}


class ChatBot:
    """Simple chatbot wrapper for OpenAI."""

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"
        self.system_prompt = """You are a helpful, friendly AI assistant.
        You give clear, concise answers and have a warm conversational tone.
        If you don't know something, you say so honestly."""

    async def chat(self, messages: list) -> str:
        """Send messages to OpenAI and get response."""
        if DEMO_MODE:
            return self._demo_response(messages[-1]["content"] if messages else "")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": self.system_prompt}
                        ] + messages,
                        "temperature": 0.7,
                        "max_tokens": 500,
                    },
                ) as resp:
                    data = await resp.json()
                    if "error" in data:
                        return f"Error: {data['error'].get('message', 'Unknown error')}"
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error: {str(e)}"

    def _demo_response(self, user_message: str) -> str:
        """Generate demo responses."""
        user_lower = user_message.lower()

        if any(g in user_lower for g in ["hello", "hi", "hey"]):
            return "Hello! 👋 I'm your AI assistant. I'm running in demo mode right now, but I can still show you how the interface works. What would you like to chat about?"

        if "how are you" in user_lower:
            return "I'm doing great, thanks for asking! As an AI, I don't have feelings in the human sense, but I'm functioning well and ready to help you. What's on your mind?"

        if any(w in user_lower for w in ["help", "can you", "what can"]):
            return """I can help with lots of things! In full mode (with an API key), I can:

• Answer questions on almost any topic
• Help with writing and editing
• Explain complex concepts
• Have conversations about ideas
• Assist with problem-solving

Right now I'm in demo mode, so my responses are pre-written. Add an OpenAI API key to unlock the full experience!"""

        if any(w in user_lower for w in ["code", "programming", "python"]):
            return """I love talking about code! In full mode, I can:

• Explain programming concepts
• Help debug code
• Suggest improvements
• Write code snippets
• Discuss best practices

This is demo mode, but with an API key I can actually help you write and understand code!"""

        if "weather" in user_lower:
            return "I'm an AI assistant, not a weather service! But I'd be happy to chat about climate, meteorology, or recommend ways to check the weather. What interests you?"

        if any(w in user_lower for w in ["thank", "thanks"]):
            return "You're welcome! Happy to help. Is there anything else you'd like to know?"

        if "?" in user_message:
            return f"That's a great question! In full mode, I'd give you a detailed answer about that. Right now I'm running in demo mode without an OpenAI API key, so my responses are limited. Add OPENAI_API_KEY to your .env file for the full AI experience!"

        return f"I understand you're saying: \"{user_message}\"\n\nThis is a demo response. With an OpenAI API key, I'd provide a thoughtful, contextual reply. The interface you're seeing works exactly the same way - just add your API key to unlock full AI capabilities!"


bot = ChatBot()


@app.route("/")
def index():
    """Main chat interface."""
    return render_template("index.html", demo_mode=DEMO_MODE)


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages."""
    data = request.get_json()
    user_message = data.get("message", "").strip()
    conversation_id = data.get("conversation_id", "default")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    # Get or create conversation
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Add user message
    conversations[conversation_id].append(
        {"role": "user", "content": user_message}
    )

    # Get AI response
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        response = loop.run_until_complete(bot.chat(conversations[conversation_id]))
    finally:
        loop.close()

    # Add assistant response
    conversations[conversation_id].append(
        {"role": "assistant", "content": response}
    )

    # Keep conversation manageable (last 20 messages)
    if len(conversations[conversation_id]) > 20:
        conversations[conversation_id] = conversations[conversation_id][-20:]

    return jsonify({
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "demo_mode": DEMO_MODE,
    })


@app.route("/api/clear", methods=["POST"])
def clear_conversation():
    """Clear conversation history."""
    data = request.get_json()
    conversation_id = data.get("conversation_id", "default")

    if conversation_id in conversations:
        conversations[conversation_id] = []

    return jsonify({"success": True})


@app.route("/api/status")
def status():
    """API status."""
    return jsonify({
        "status": "operational",
        "demo_mode": DEMO_MODE,
        "model": bot.model if not DEMO_MODE else "demo",
    })


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  🤖 AI Chat")
    print("=" * 50)
    if DEMO_MODE:
        print("⚠️  Running in DEMO MODE")
        print("   Add OPENAI_API_KEY to .env for full AI")
    else:
        print("✅ OpenAI connected")
    print(f"\n🌐 Open http://localhost:5019")
    print("=" * 50 + "\n")

    app.run(debug=True, port=5019)
