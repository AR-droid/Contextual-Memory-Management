import json
import unittest
from unittest.mock import patch, MagicMock

from memory_system.types import Memory
from memory_system.controller import InfluenceController

class TestController(unittest.TestCase):
    def test_parse_valid_json(self):
        controller = InfluenceController(api_key="mock")
        
        mock_json = '''
        ```json
        {
            "memory_id": "m1",
            "relevance": 0.95,
            "memory_type": "USER_BELIEF",
            "influence": "CONDITIONAL",
            "role": "USER_PERSPECTIVE",
            "reason": "It's a subjective belief."
        }
        ```
        '''
        
        decision = controller._parse_response(mock_json, "m1", "USER_BELIEF")
        
        self.assertEqual(decision.memory_id, "m1")
        self.assertEqual(decision.relevance, 0.95)
        self.assertEqual(decision.memory_type, "USER_BELIEF")
        self.assertEqual(decision.influence, "CONDITIONAL")
        self.assertEqual(decision.role, "USER_PERSPECTIVE")
        self.assertEqual(decision.reason, "It's a subjective belief.")

    def test_parse_invalid_enum_fallback(self):
        controller = InfluenceController(api_key="mock")
        
        mock_json = '''
        {
            "memory_id": "m1",
            "relevance": 0.95,
            "memory_type": "USER_BELIEF",
            "influence": "UNKNOWN_INF",
            "role": "UNKNOWN_ROLE",
            "reason": "It's a subjective belief."
        }
        '''
        
        decision = controller._parse_response(mock_json, "m1", "USER_BELIEF")
        
        # Should fallback to SUPPRESS for unknown enums
        self.assertEqual(decision.influence, "SUPPRESS")
        self.assertEqual(decision.role, "SUPPRESS")

