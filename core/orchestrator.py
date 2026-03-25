"""
AURIX Agent Orchestrator — Routes tasks to the appropriate agent.
"""

import json
import re
from typing import Optional
from core.brain import AurixBrain
from core.agents.task_agent import TaskAgent
from core.agents.research_agent import ResearchAgent
from core.agents.memory_agent import MemoryAgent
from core.agents.system_agent import SystemAgent


class AgentOrchestrator:
    """
    Central orchestrator that coordinates all AURIX agents.
    Receives user input, uses the AI brain to decide which agent to use,
    and executes the appropriate action.
    """

    def __init__(self):
        self.brain = AurixBrain()
        self.task_agent = TaskAgent()
        self.research_agent = ResearchAgent()
        self.memory_agent = MemoryAgent()
        self.system_agent = SystemAgent()

    async def process(self, user_input: str) -> dict:
        """Process user input through the full pipeline."""
        # 1. Recall relevant memories for context
        context = ""
        try:
            recall_result = self.memory_agent.recall(user_input, n_results=3)
            if recall_result.get("success") and recall_result.get("memories"):
                memories = recall_result["memories"]
                context_parts = [m["content"] for m in memories if m.get("relevance", 0) > 0.3]
                if context_parts:
                    context = "Relevant memories:\n" + "\n".join(f"- {c}" for c in context_parts)
        except Exception:
            pass

        # 2. Get AI response
        ai_response = await self.brain.think(user_input, context=context)

        # 3. Check if response contains an action
        action = self._extract_action(ai_response)

        result = {
            "response": ai_response,
            "action_taken": False,
            "action_result": None
        }

        if action:
            # 4. Route to appropriate agent
            action_result = await self._route_action(action)
            result["action_taken"] = True
            result["action_result"] = action_result

            # 5. Get AI to summarize the action result
            summary_prompt = f"I executed the action '{action.get('action')}'. Result: {json.dumps(action_result)[:1000]}. Please summarize what happened for the user in a natural way."
            result["response"] = await self.brain.think(summary_prompt)

        # 6. Store conversation in memory
        try:
            self.memory_agent.store_memory(
                f"User: {user_input}\nAURIX: {result['response'][:500]}",
                category="conversation"
            )
        except Exception:
            pass

        return result

    async def stream_process(self, user_input: str):
        """Process user input with streaming response."""
        # Recall context
        context = ""
        try:
            recall_result = self.memory_agent.recall(user_input, n_results=3)
            if recall_result.get("success") and recall_result.get("memories"):
                memories = recall_result["memories"]
                context_parts = [m["content"] for m in memories if m.get("relevance", 0) > 0.3]
                if context_parts:
                    context = "Relevant memories:\n" + "\n".join(f"- {c}" for c in context_parts)
        except Exception:
            pass

        # Stream response
        full_response = ""
        async for token in self.brain.stream_think(user_input, context=context):
            full_response += token
            yield {"type": "token", "content": token}

        # Check for action in complete response
        action = self._extract_action(full_response)
        if action:
            yield {"type": "action_start", "action": action.get("action")}
            action_result = await self._route_action(action)
            yield {"type": "action_result", "result": action_result}

        # Store in memory
        try:
            self.memory_agent.store_memory(
                f"User: {user_input}\nAURIX: {full_response[:500]}",
                category="conversation"
            )
        except Exception:
            pass

    async def _route_action(self, action: dict) -> dict:
        """Route an action to the appropriate agent."""
        action_type = action.get("action", "")

        # Task Agent actions
        if action_type in ["run_command", "open_app", "close_app", "manage_file",
                          "open_url", "open_folder", "open_terminal"]:
            return await self.task_agent.execute(action)

        # Research Agent actions
        if action_type in ["search_web", "research_topic"]:
            return await self.research_agent.execute(action)

        # Memory Agent actions
        if action_type in ["remember", "recall"]:
            return await self.memory_agent.execute(action)

        # System Agent actions
        if action_type in ["system_info", "take_screenshot", "set_volume",
                          "set_brightness", "lock_screen", "list_processes", "kill_process"]:
            return await self.system_agent.execute(action)

        return {"success": False, "error": f"No agent found for action: {action_type}"}

    def _extract_action(self, response: str) -> Optional[dict]:
        """Extract JSON action block from AI response."""
        try:
            # Look for JSON blocks in the response
            patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
                r'(\{"action":\s*"[^"]+?".*?\})',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, response, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if "action" in data:
                            return data
                    except json.JSONDecodeError:
                        continue
            return None
        except Exception:
            return None

    async def get_system_stats(self) -> dict:
        """Get live system stats for the HUD."""
        return await self.system_agent.get_live_stats()

    async def quick_search(self, query: str) -> dict:
        """Quick web search."""
        return await self.research_agent._search_web({"query": query})

    async def get_memory_stats(self) -> dict:
        """Get memory system statistics."""
        return self.memory_agent.get_memory_stats()
