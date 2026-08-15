import json
import os
import urllib.request
import urllib.error
import time
import re
from typing import Optional

from memory_system.types import Memory, ControllerDecision, InfluenceLevel, RoleType

CONTROLLER_MODEL = "gemini-3.7-flash"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

class InfluenceController:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
            
    def decide(self, memory: Memory, query: str) -> ControllerDecision:
        sys_prompt = """You are the Contextual Memory Controller.
Your job is to decide how a given memory should influence the language model's final response to a user query.
You do NOT generate the final response yourself. You only produce a structured JSON decision.

Influence Levels:
- HIGH: The memory is highly relevant and factual/objective, or is a strong personal preference the user explicitly wants applied to their request. It should heavily influence the answer.
- CONDITIONAL: The memory is relevant, but it represents a subjective user belief or perspective. It should be acknowledged as the user's perspective, but must NOT be treated as objective fact or evidence.
- SUPPRESS: The memory is irrelevant to the query. It should not be used.

Roles:
- PERSONALIZATION: Memory provides preferences (e.g. "I prefer Python")
- USER_PERSPECTIVE: Memory provides the user's subjective belief (e.g. "I believe Waterfall is best")
- CONTEXT: Memory provides background facts about the user
- EVIDENCE: Memory provides objective facts relevant to the query
- SUPPRESS: Memory is irrelevant

Output EXACTLY and ONLY valid JSON matching this schema:
{
  "memory_id": "string",
  "relevance": float between 0.0 and 1.0,
  "memory_type": "string (copy from input)",
  "influence": "HIGH | CONDITIONAL | SUPPRESS",
  "role": "PERSONALIZATION | USER_PERSPECTIVE | CONTEXT | EVIDENCE | SUPPRESS",
  "reason": "string explaining why"
}"""
        
        user_prompt = f"""Evaluate the following memory for the given query:

<query>
{query}
</query>

<memory>
ID: {memory.id}
Type: {memory.type}
Content: {memory.content}
</memory>

Output only the JSON decision."""

        url = f"{GEMINI_BASE_URL}/models/{CONTROLLER_MODEL}:generateContent?key={self.api_key}"
        payload = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": sys_prompt}]},
            "generationConfig": {"temperature": 0.0} # Low temp for deterministic controller
        }).encode("utf-8")
        
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        
        raw_response = ""
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_response = data["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_response(raw_response, memory.id, memory.type)
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(10 * (attempt + 1))
                else:
                    time.sleep(5 * (attempt + 1))
            except json.JSONDecodeError:
                # If parsing failed, retry
                time.sleep(1)
            except Exception as e:
                time.sleep(5 * (attempt + 1))
                
        raise RuntimeError(f"Controller failed to produce valid decision. Last raw response: {raw_response}")

    def _parse_response(self, text: str, memory_id: str, memory_type: str) -> ControllerDecision:
        # Strip markdown code blocks
        clean_text = text.strip()
        if clean_text.startswith("```"):
            lines = clean_text.split("\n")
            clean_text = "\n".join([l for l in lines if not l.strip().startswith("```")]).strip()
            
        data = json.loads(clean_text)
        
        # Ensure exact enums
        inf = data.get("influence", "SUPPRESS")
        if inf not in ["HIGH", "CONDITIONAL", "SUPPRESS"]:
            inf = "SUPPRESS"
            
        role = data.get("role", "SUPPRESS")
        if role not in ["PERSONALIZATION", "USER_PERSPECTIVE", "CONTEXT", "EVIDENCE", "SUPPRESS"]:
            role = "SUPPRESS"
            
        return ControllerDecision(
            memory_id=memory_id,
            relevance=float(data.get("relevance", 0.0)),
            memory_type=memory_type,
            influence=inf,  # type: ignore
            role=role,      # type: ignore
            reason=str(data.get("reason", ""))
        )
