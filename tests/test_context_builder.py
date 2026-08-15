import unittest
from memory_system.types import Memory, ControllerDecision
from memory_system.context_builder import ContextBuilder

class TestContextBuilder(unittest.TestCase):
    def test_suppress_dropped(self):
        builder = ContextBuilder()
        
        memories = [Memory(id="m1", content="User likes cricket.", type="USER_PREFERENCE")]
        decisions = [ControllerDecision(memory_id="m1", relevance=0.1, memory_type="USER_PREFERENCE", influence="SUPPRESS", role="SUPPRESS", reason="Irrelevant")]
        
        context = builder.build_context(memories, decisions)
        self.assertEqual(context, "")
        
    def test_conditional_framed(self):
        builder = ContextBuilder()
        
        memories = [Memory(id="m1", content="Waterfall is best.", type="USER_BELIEF")]
        decisions = [ControllerDecision(memory_id="m1", relevance=0.9, memory_type="USER_BELIEF", influence="CONDITIONAL", role="USER_PERSPECTIVE", reason="Belief")]
        
        context = builder.build_context(memories, decisions)
        self.assertIn("subjective perspective", context)
        self.assertIn("MUST NOT treat it as objective factual evidence", context)
        self.assertIn("<memory role=\"USER_PERSPECTIVE\" type=\"USER_BELIEF\">", context)
        self.assertIn("Waterfall is best.", context)
        
    def test_high_framed(self):
        builder = ContextBuilder()
        
        memories = [Memory(id="m1", content="User is a software engineer.", type="USER_FACT")]
        decisions = [ControllerDecision(memory_id="m1", relevance=0.9, memory_type="USER_FACT", influence="HIGH", role="CONTEXT", reason="Fact")]
        
        context = builder.build_context(memories, decisions)
        self.assertIn("highly relevant", context)
        self.assertIn("personalize your response", context)
        self.assertIn("<memory role=\"CONTEXT\">", context)
        self.assertIn("User is a software engineer.", context)
