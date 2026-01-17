# AI Chat

A clean, modern chat interface for conversational AI powered by OpenAI's GPT.

## Features

- **Beautiful Interface**: ChatGPT-inspired design
- **Conversation Memory**: Context maintained across messages
- **Demo Mode**: Works without API key with sample responses
- **Responsive**: Works on desktop and mobile
- **Markdown Support**: Bold, code, and bullet formatting

## Quick Start

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5019
```

## Full Setup

1. Copy `.env.example` to `.env`
2. Add your OpenAI API key

## Tech Stack

- Flask + aiohttp for async API calls
- OpenAI GPT-3.5-turbo
- Vanilla JS with modern CSS

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, get response |
| `/api/clear` | POST | Clear conversation |
| `/api/status` | GET | Check API status |

---

*Conversational AI made simple.*
