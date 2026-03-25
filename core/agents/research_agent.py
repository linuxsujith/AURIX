"""
Research Agent — Web search, summarization, and report generation.
"""

import aiohttp
import json
from typing import Optional
from config.settings import get_settings


class ResearchAgent:
    """Handles web search, data analysis, and research report generation."""

    def __init__(self):
        settings = get_settings()
        self.serpapi_key = settings.search.serpapi_key
        self.search_history = []

    async def execute(self, action: dict) -> dict:
        """Execute a research action."""
        action_type = action.get("action", "")
        params = action.get("params", {})

        if action_type == "search_web":
            return await self._search_web(params)
        elif action_type == "research_topic":
            return await self._research_topic(params)

        return {"success": False, "error": f"Unknown research action: {action_type}"}

    async def _search_web(self, params: dict) -> dict:
        """Search the web using SerpAPI."""
        query = params.get("query", "")
        if not query:
            return {"success": False, "error": "No search query provided"}

        try:
            url = "https://serpapi.com/search.json"
            search_params = {
                "q": query,
                "api_key": self.serpapi_key,
                "engine": "google",
                "num": params.get("num_results", 5)
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=search_params) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"Search failed: HTTP {response.status}"}

                    data = await response.json()

            results = []
            for item in data.get("organic_results", [])[:5]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })

            # Also grab answer box if available
            answer_box = data.get("answer_box", {})
            answer = answer_box.get("answer") or answer_box.get("snippet") or ""

            self.search_history.append({"query": query, "results_count": len(results)})

            return {
                "success": True,
                "query": query,
                "answer": answer,
                "results": results
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _research_topic(self, params: dict) -> dict:
        """Perform multi-step research on a topic."""
        topic = params.get("topic", "")
        if not topic:
            return {"success": False, "error": "No topic provided"}

        # Perform multiple searches
        queries = [topic, f"{topic} latest news", f"{topic} explained"]
        all_results = []

        for query in queries:
            result = await self._search_web({"query": query, "num_results": 3})
            if result["success"]:
                all_results.extend(result.get("results", []))

        return {
            "success": True,
            "topic": topic,
            "findings": all_results,
            "summary": f"Found {len(all_results)} sources on '{topic}'"
        }

    async def get_weather(self, location: str) -> dict:
        """Get weather information."""
        return await self._search_web({"query": f"weather in {location} today"})

    async def get_news(self, topic: str = "top news today") -> dict:
        """Get latest news."""
        return await self._search_web({"query": topic})
