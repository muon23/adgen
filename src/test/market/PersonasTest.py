import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add project root to path to import modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "main"))

from market.Personas import Personas


class PersonasTest(unittest.TestCase):
    """Unit tests for the Personas class and Persona nested class."""

    def test_persona_init(self):
        """Test Persona initialization."""
        persona = Personas.Persona(
            persona_id="TEST001",
            label="Test Persona",
            market_affinity={"MARKET1": 0.5, "MARKET2": 0.5},
            prevalence=1.0,
            properties={"type": "test", "demographic_context": "Test demographics"}
        )

        self.assertEqual(persona.persona_id, "TEST001")
        self.assertEqual(persona.label, "Test Persona")
        self.assertEqual(persona.market_affinity, {"MARKET1": 0.5, "MARKET2": 0.5})
        self.assertEqual(persona.prevalence, 1.0)
        self.assertEqual(persona.properties, {"type": "test", "demographic_context": "Test demographics"})

    def test_persona_init_default_properties(self):
        """Test Persona initialization with default empty properties."""
        persona = Personas.Persona(
            persona_id="TEST002",
            label="Test Persona 2",
            market_affinity={},
            prevalence=0.5
        )

        self.assertEqual(persona.properties, {})

    def test_persona_from_dict_with_all_fields(self):
        """Test Persona.from_dict with all fields."""
        data = {
            "persona_id": "DICT001",
            "label": "Dict Persona",
            "prevalence": 1.0,
            "market_affinity": [
                {"market_id": "MARKET1", "weight": 0.7},
                {"market_id": "MARKET2", "weight": 0.3}
            ],
            "type": "test_type",
            "demographic_context": "Test demographics",
            "primary_motivation": "Test motivation"
        }

        persona = Personas.Persona.from_dict(data)

        self.assertEqual(persona.persona_id, "DICT001")
        self.assertEqual(persona.label, "Dict Persona")
        self.assertEqual(persona.prevalence, 1.0)
        self.assertEqual(persona.market_affinity, {"MARKET1": 0.7, "MARKET2": 0.3})
        self.assertEqual(persona.properties["type"], "test_type")
        self.assertEqual(persona.properties["demographic_context"], "Test demographics")
        self.assertEqual(persona.properties["primary_motivation"], "Test motivation")

    def test_persona_from_dict_with_missing_core_fields(self):
        """Test Persona.from_dict with missing core fields."""
        data = {
            "type": "test_type"
        }

        persona = Personas.Persona.from_dict(data)

        self.assertEqual(persona.persona_id, "")
        self.assertEqual(persona.label, "")
        self.assertEqual(persona.prevalence, 0.0)
        self.assertEqual(persona.market_affinity, {})
        self.assertEqual(persona.properties["type"], "test_type")

    def test_persona_from_dict_with_empty_market_affinity(self):
        """Test Persona.from_dict with empty market_affinity."""
        data = {
            "persona_id": "EMPTY001",
            "label": "Empty Market",
            "prevalence": 1.0,
            "market_affinity": []
        }

        persona = Personas.Persona.from_dict(data)

        self.assertEqual(persona.market_affinity, {})

    def test_persona_from_dict_with_invalid_market_affinity(self):
        """Test Persona.from_dict with invalid market_affinity format."""
        data = {
            "persona_id": "INVALID001",
            "label": "Invalid Market",
            "prevalence": 1.0,
            "market_affinity": "not a list"
        }

        persona = Personas.Persona.from_dict(data)

        self.assertEqual(persona.market_affinity, {})

    def test_persona_from_json(self):
        """Test Persona.from_json."""
        json_str = json.dumps({
            "persona_id": "JSON001",
            "label": "JSON Persona",
            "prevalence": 0.8,
            "market_affinity": [
                {"market_id": "MARKET1", "weight": 1.0}
            ],
            "type": "json_type"
        })

        persona = Personas.Persona.from_json(json_str)

        self.assertEqual(persona.persona_id, "JSON001")
        self.assertEqual(persona.label, "JSON Persona")
        self.assertEqual(persona.prevalence, 0.8)
        self.assertEqual(persona.market_affinity, {"MARKET1": 1.0})
        self.assertEqual(persona.properties["type"], "json_type")

    def test_persona_to_json(self):
        """Test Persona.to_json."""
        persona = Personas.Persona(
            persona_id="TOJSON001",
            label="ToJSON Persona",
            market_affinity={"MARKET1": 0.6, "MARKET2": 0.4},
            prevalence=1.0,
            properties={
                "type": "tojson_type",
                "demographic_context": "ToJSON demographics"
            }
        )

        json_str = persona.to_json()
        parsed = json.loads(json_str)

        self.assertEqual(parsed["persona_id"], "TOJSON001")
        self.assertEqual(parsed["label"], "ToJSON Persona")
        self.assertEqual(parsed["prevalence"], 1.0)
        self.assertEqual(len(parsed["market_affinity"]), 2)
        self.assertEqual(parsed["type"], "tojson_type")
        self.assertEqual(parsed["demographic_context"], "ToJSON demographics")

        # Check market_affinity is a list
        market_dict = {item["market_id"]: item["weight"] for item in parsed["market_affinity"]}
        self.assertEqual(market_dict, {"MARKET1": 0.6, "MARKET2": 0.4})

    def test_persona_getattr(self):
        """Test Persona.__getattr__ for accessing properties."""
        persona = Personas.Persona(
            persona_id="GETATTR001",
            label="GetAttr Persona",
            market_affinity={},
            prevalence=1.0,
            properties={"type": "getattr_type", "primary_motivation": "Test motivation"}
        )

        self.assertEqual(persona.type, "getattr_type")
        self.assertEqual(persona.primary_motivation, "Test motivation")

    def test_persona_getattr_attributeerror(self):
        """Test Persona.__getattr__ raises AttributeError for missing attribute."""
        persona = Personas.Persona(
            persona_id="ATTRERROR001",
            label="AttrError Persona",
            market_affinity={},
            prevalence=1.0
        )

        with self.assertRaises(AttributeError):
            _ = persona.nonexistent_key

    def test_persona_core_fields_not_via_getattr(self):
        """Test that core fields are accessed normally, not via __getattr__."""
        persona = Personas.Persona(
            persona_id="CORE001",
            label="Core Persona",
            market_affinity={"MARKET1": 1.0},
            prevalence=0.8
        )

        # Core fields should be accessed directly
        self.assertEqual(persona.persona_id, "CORE001")
        self.assertEqual(persona.label, "Core Persona")
        self.assertEqual(persona.prevalence, 0.8)
        self.assertEqual(persona.market_affinity, {"MARKET1": 1.0})

    def test_persona_round_trip(self):
        """Test round-trip conversion: dict -> Persona -> JSON -> Persona."""
        original_data = {
            "persona_id": "ROUND001",
            "label": "Round Trip Persona",
            "prevalence": 0.9,
            "market_affinity": [
                {"market_id": "MARKET1", "weight": 0.5},
                {"market_id": "MARKET2", "weight": 0.5}
            ],
            "type": "round_type",
            "demographic_context": "Round demographics"
        }

        # Create persona from dict
        persona = Personas.Persona.from_dict(original_data)

        # Convert to JSON and back
        json_str = persona.to_json()
        restored = Personas.Persona.from_json(json_str)

        self.assertEqual(persona.persona_id, restored.persona_id)
        self.assertEqual(persona.label, restored.label)
        self.assertEqual(persona.prevalence, restored.prevalence)
        self.assertEqual(persona.market_affinity, restored.market_affinity)
        self.assertEqual(persona.properties, restored.properties)

    def test_personas_init(self):
        """Test Personas initialization."""
        personas = Personas()

        self.assertEqual(len(personas), 0)
        self.assertEqual(len(personas.persona), 0)

    def test_personas_load_single_persona(self):
        """Test loading a single persona."""
        test_data = {
            "personas": [
                {
                    "persona_id": "LOAD001",
                    "label": "Load Persona",
                    "prevalence": 1.0,
                    "market_affinity": [
                        {"market_id": "MARKET1", "weight": 1.0}
                    ],
                    "type": "load_type"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            personas = Personas()
            personas.load(temp_file)

            self.assertEqual(len(personas), 1)
            persona = personas.get("LOAD001")
            self.assertIsNotNone(persona)
            self.assertEqual(persona.label, "Load Persona")
            self.assertEqual(persona.properties["type"], "load_type")
        finally:
            Path(temp_file).unlink()

    def test_personas_load_multiple_personas(self):
        """Test loading multiple personas."""
        test_data = {
            "personas": [
                {
                    "persona_id": "MULTI001",
                    "label": "Multi Persona 1",
                    "prevalence": 1.0,
                    "market_affinity": []
                },
                {
                    "persona_id": "MULTI002",
                    "label": "Multi Persona 2",
                    "prevalence": 0.5,
                    "market_affinity": []
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            personas = Personas()
            personas.load(temp_file)

            self.assertEqual(len(personas), 2)
            self.assertIsNotNone(personas.get("MULTI001"))
            self.assertIsNotNone(personas.get("MULTI002"))
        finally:
            Path(temp_file).unlink()

    def test_personas_load_duplicate_override(self):
        """Test that loading duplicate persona_id overrides previous."""
        test_data1 = {
            "personas": [
                {
                    "persona_id": "DUP001",
                    "label": "Original Label",
                    "prevalence": 1.0,
                    "market_affinity": []
                }
            ]
        }

        test_data2 = {
            "personas": [
                {
                    "persona_id": "DUP001",
                    "label": "Overridden Label",
                    "prevalence": 0.5,
                    "market_affinity": []
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f1:
            json.dump(test_data1, f1)
            temp_file1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f2:
            json.dump(test_data2, f2)
            temp_file2 = f2.name

        try:
            personas = Personas()
            personas.load(temp_file1)
            self.assertEqual(personas.get("DUP001").label, "Original Label")

            personas.load(temp_file2)
            self.assertEqual(len(personas), 1)  # Still only one persona
            self.assertEqual(personas.get("DUP001").label, "Overridden Label")
            self.assertEqual(personas.get("DUP001").prevalence, 0.5)
        finally:
            Path(temp_file1).unlink()
            Path(temp_file2).unlink()

    def test_personas_load_empty_file(self):
        """Test loading from file with empty personas list."""
        test_data = {"personas": []}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            personas = Personas()
            personas.load(temp_file)
            self.assertEqual(len(personas), 0)
        finally:
            Path(temp_file).unlink()

    def test_personas_load_missing_personas_key(self):
        """Test loading from file without 'personas' key."""
        test_data = {"other_key": "value"}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            personas = Personas()
            personas.load(temp_file)
            self.assertEqual(len(personas), 0)
        finally:
            Path(temp_file).unlink()

    def test_personas_of(self):
        """Test Personas.of classmethod."""
        test_data = {
            "personas": [
                {
                    "persona_id": "OF001",
                    "label": "Of Persona",
                    "prevalence": 1.0,
                    "market_affinity": []
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            personas = Personas.of(temp_file)

            self.assertEqual(len(personas), 1)
            self.assertIsNotNone(personas.get("OF001"))
        finally:
            Path(temp_file).unlink()

    def test_personas_get_existing(self):
        """Test getting an existing persona."""
        persona = Personas.Persona(
            persona_id="GET001",
            label="Get Persona",
            market_affinity={},
            prevalence=1.0
        )

        personas = Personas()
        personas.persona["GET001"] = persona

        retrieved = personas.get("GET001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.persona_id, "GET001")

    def test_personas_get_nonexistent(self):
        """Test getting a nonexistent persona."""
        personas = Personas()

        retrieved = personas.get("NONEXISTENT")
        self.assertIsNone(retrieved)

    def test_personas_len(self):
        """Test Personas.__len__."""
        personas = Personas()
        self.assertEqual(len(personas), 0)

        personas.persona["P001"] = Personas.Persona(
            persona_id="P001",
            label="Persona 1",
            market_affinity={},
            prevalence=1.0
        )
        self.assertEqual(len(personas), 1)

        personas.persona["P002"] = Personas.Persona(
            persona_id="P002",
            label="Persona 2",
            market_affinity={},
            prevalence=1.0
        )
        self.assertEqual(len(personas), 2)

    def test_personas_iter(self):
        """Test Personas.__iter__."""
        personas = Personas()
        personas.persona["I001"] = Personas.Persona(
            persona_id="I001",
            label="Iter Persona 1",
            market_affinity={},
            prevalence=1.0
        )
        personas.persona["I002"] = Personas.Persona(
            persona_id="I002",
            label="Iter Persona 2",
            market_affinity={},
            prevalence=1.0
        )

        persona_ids = {p.persona_id for p in personas}
        self.assertEqual(persona_ids, {"I001", "I002"})

    def test_personas_contains(self):
        """Test Personas.__contains__."""
        personas = Personas()
        personas.persona["C001"] = Personas.Persona(
            persona_id="C001",
            label="Contains Persona",
            market_affinity={},
            prevalence=1.0
        )

        self.assertIn("C001", personas)
        self.assertNotIn("C002", personas)

    def test_personas_load_real_file(self):
        """Test loading from the actual personas_random_diverse_y.json file."""
        json_file = Path(__file__).parent.parent.parent.parent / "data" / "personas_random_diverse_y.json"

        if json_file.exists():
            personas = Personas.of(str(json_file))

            self.assertGreater(len(personas), 0)

            # Check first persona
            first_id = list(personas.persona.keys())[0]
            first = personas.get(first_id)
            self.assertIsNotNone(first)
            self.assertIsNotNone(first.persona_id)
            self.assertIsNotNone(first.label)
            self.assertIsInstance(first.market_affinity, dict)
            self.assertIsInstance(first.prevalence, float)


if __name__ == '__main__':
    unittest.main()
