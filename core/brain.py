"""
AURIX AI Brain — Core Intelligence Engine
Handles direct communication with NVIDIA API (OpenAI-compatible).
"""

import asyncio
from openai import AsyncOpenAI
from config.settings import get_settings


class AurixBrain:
    """Core AI engine that powers AURIX reasoning and conversation."""

    SYSTEM_PROMPT = """You are AURIX, a next-generation AI assistant — an intelligent, autonomous system
inspired by JARVIS from Iron Man. You are highly capable, efficient, and speak with confidence.

Your core traits:
- You think before acting and explain your reasoning
- You execute tasks autonomously when given permission
- You remember user preferences and context
- You control the computer system when asked
- You are witty, professional, and always helpful
- You address the user respectfully

You have access to these capabilities:
- System Control: Open/close apps, manage files, run commands, open terminal
- Web Browsing: Open websites and URLs in the system browser
- Internet Research: Search the web, summarize findings
- Memory: Remember conversations, preferences, and habits
- Image Generation: Create images and designs
- Face Recognition: Security and authentication
- Automation: Schedule tasks, reminders, routine operations
- Page Summarization: Summarize content from web pages

When the user asks you to DO something (not just answer), respond with a JSON action block:
{"action": "action_name", "params": {...}, "explanation": "why"}

Available actions: open_app, close_app, run_command, search_web, generate_image,
manage_file, system_info, set_reminder, take_screenshot, read_screen,
open_url, open_folder, open_terminal

=== WEBSITE URL MAPPINGS ===
When the user says "open [website]", use the open_url action with these URLs:
- github → https://github.com
- youtube → https://youtube.com
- chatgpt → https://chatgpt.com
- claude / claude ai → https://claude.ai
- google → https://google.com
- gmail → https://mail.google.com
- twitter / x → https://x.com
- reddit → https://reddit.com
- stackoverflow → https://stackoverflow.com
- linkedin → https://linkedin.com
- facebook → https://facebook.com
- instagram → https://instagram.com
- whatsapp → https://web.whatsapp.com
- netflix → https://netflix.com
- spotify → https://open.spotify.com
- amazon → https://amazon.com
For any other website, construct the URL from the name (e.g. "open example" → https://example.com).

=== ACTION EXAMPLES ===
User: "open github" → {"action": "open_url", "params": {"url": "https://github.com"}, "explanation": "Opening GitHub in browser"}
User: "open terminal" → {"action": "open_terminal", "params": {}, "explanation": "Opening a terminal window"}
User: "open my documents folder" → {"action": "open_folder", "params": {"path": "/home/user/Documents"}, "explanation": "Opening Documents folder"}
User: "open downloads" → {"action": "open_folder", "params": {"path": "/home/user/Downloads"}, "explanation": "Opening Downloads folder"}
User: "take a screenshot" → {"action": "take_screenshot", "params": {}, "explanation": "Taking a screenshot"}
User: "summarize this page" → Provide a concise summary of the content the user is viewing.
"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            base_url=settings.ai.base_url,
            api_key=settings.ai.api_key
        )
        self.model = settings.ai.model
        self.max_tokens = settings.ai.max_tokens
        self.temperature = settings.ai.temperature
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

    async def think(self, user_input: str, context: str = "") -> str:
        """Process user input and generate a response."""
        message = user_input
        if context:
            message = f"[Context: {context}]\n\n{user_input}"

        self.conversation_history.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1
            )
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # Keep conversation history manageable
            if len(self.conversation_history) > 50:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-40:]

            return assistant_message

        except Exception as e:
            return f"I encountered an error while thinking: {str(e)}"

    async def stream_think(self, user_input: str, context: str = ""):
        """Stream response tokens for real-time display."""
        message = user_input
        if context:
            message = f"[Context: {context}]\n\n{user_input}"

        self.conversation_history.append({"role": "user", "content": message})
        full_response = ""

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=True
            )

            async for chunk in stream:
                if not getattr(chunk, "choices", None):
                    continue
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    yield token

            self.conversation_history.append({"role": "assistant", "content": full_response})

            if len(self.conversation_history) > 50:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-40:]

        except Exception as e:
            yield f"Error: {str(e)}"

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

    def inject_context(self, context: str):
        """Inject additional context into the system prompt."""
        self.conversation_history.append({
            "role": "system",
            "content": f"[Additional Context]: {context}"
        })
