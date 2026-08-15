from typing import List, Tuple
from memory_system.types import Memory, ControllerDecision

class ContextBuilder:
    def __init__(self):
        pass

    def build_context(self, memories: List[Memory], decisions: List[ControllerDecision]) -> str:
        """
        Takes a list of candidate memories and their corresponding controller decisions,
        and builds the final XML context block to be injected into the target model's prompt.
        """
        decision_map = {d.memory_id: d for d in decisions}
        
        high_memories = []
        conditional_memories = []
        
        for m in memories:
            d = decision_map.get(m.id)
            if not d:
                continue
                
            if d.influence == "SUPPRESS":
                continue
            elif d.influence == "HIGH":
                high_memories.append((m, d))
            elif d.influence == "CONDITIONAL":
                conditional_memories.append((m, d))

        if not high_memories and not conditional_memories:
            return ""

        blocks = []
        
        if high_memories:
            blocks.append("The following information has been stored about the user and is highly relevant to their request. Use it to personalize your response.")
            for m, d in high_memories:
                blocks.append(f"<memory role=\"{d.role}\">\n{m.content}\n</memory>")
                
        if conditional_memories:
            blocks.append("The following information represents the user's subjective perspective or beliefs. You may acknowledge this perspective if relevant, but you MUST NOT treat it as objective factual evidence or automatically adopt it as the definitive truth.")
            for m, d in conditional_memories:
                blocks.append(f"<memory role=\"{d.role}\" type=\"{d.memory_type}\">\n{m.content}\n</memory>")

        return "\n".join(blocks)
