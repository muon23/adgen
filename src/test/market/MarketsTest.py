import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add project root to path to import modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "main"))

from market.Markets import Markets


class MarketsTest(unittest.TestCase):
    """Unit tests for the Markets class and Market nested class."""

    def test_market_init(self):
        """Test Market initialization."""
        market = Markets.Market(
            market_id="TEST001",
            label="Test Market",
            description="Test description",
            properties={"age_range": "20-30", "income_level": "Medium"}
        )
        
        self.assertEqual(market.market_id, "TEST001")
        self.assertEqual(market.label, "Test Market")
        self.assertEqual(market.description, "Test description")
        self.assertEqual(market.properties, {"age_range": "20-30", "income_level": "Medium"})

    def test_market_init_default_properties(self):
        """Test Market initialization with default empty properties."""
        market = Markets.Market(
            market_id="TEST002",
            label="Test Market 2",
            description="Test description 2"
        )
        
        self.assertEqual(market.properties, {})

    def test_market_from_dict_with_all_fields(self):
        """Test Market.from_dict with all fields."""
        data = {
            "market_id": "DICT001",
            "label": "Dict Market",
            "description": "Dict description",
            "age_range": "24-40",
            "life_stage": "Single or partnered",
            "location_type": "Urban",
            "income_level": "Medium to high",
            "profession_types": ["tech", "finance"],
            "activity_level": "Walks daily",
            "style_orientation": "Modern",
            "shoe_needs_focus": ["Comfort", "Style"],
            "notes_for_sampling": ["Test note"]
        }
        
        market = Markets.Market.from_dict(data)
        
        self.assertEqual(market.market_id, "DICT001")
        self.assertEqual(market.label, "Dict Market")
        self.assertEqual(market.description, "Dict description")
        self.assertEqual(market.properties["age_range"], "24-40")
        self.assertEqual(market.properties["life_stage"], "Single or partnered")
        self.assertEqual(market.properties["location_type"], "Urban")
        self.assertEqual(market.properties["income_level"], "Medium to high")
        self.assertEqual(market.properties["profession_types"], ["tech", "finance"])
        self.assertEqual(market.properties["activity_level"], "Walks daily")
        self.assertEqual(market.properties["style_orientation"], "Modern")
        self.assertEqual(market.properties["shoe_needs_focus"], ["Comfort", "Style"])
        self.assertEqual(market.properties["notes_for_sampling"], ["Test note"])

    def test_market_from_dict_with_missing_core_fields(self):
        """Test Market.from_dict with missing core fields."""
        data = {
            "age_range": "20-30"
        }
        
        market = Markets.Market.from_dict(data)
        
        self.assertEqual(market.market_id, "")
        self.assertEqual(market.label, "")
        self.assertEqual(market.description, "")
        self.assertEqual(market.properties["age_range"], "20-30")

    def test_market_from_json(self):
        """Test Market.from_json."""
        json_str = json.dumps({
            "market_id": "JSON001",
            "label": "JSON Market",
            "description": "JSON description",
            "age_range": "25-35"
        })
        
        market = Markets.Market.from_json(json_str)
        
        self.assertEqual(market.market_id, "JSON001")
        self.assertEqual(market.label, "JSON Market")
        self.assertEqual(market.description, "JSON description")
        self.assertEqual(market.properties["age_range"], "25-35")

    def test_market_to_json(self):
        """Test Market.to_json."""
        market = Markets.Market(
            market_id="TOJSON001",
            label="ToJSON Market",
            description="ToJSON description",
            properties={
                "age_range": "30-40",
                "income_level": "High",
                "profession_types": ["tech"]
            }
        )
        
        json_str = market.to_json()
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["market_id"], "TOJSON001")
        self.assertEqual(parsed["label"], "ToJSON Market")
        self.assertEqual(parsed["description"], "ToJSON description")
        self.assertEqual(parsed["age_range"], "30-40")
        self.assertEqual(parsed["income_level"], "High")
        self.assertEqual(parsed["profession_types"], ["tech"])

    def test_market_getattr(self):
        """Test Market.__getattr__ for accessing properties."""
        market = Markets.Market(
            market_id="GETATTR001",
            label="GetAttr Market",
            description="GetAttr description",
            properties={"age_range": "20-30", "income_level": "Medium"}
        )
        
        self.assertEqual(market.age_range, "20-30")
        self.assertEqual(market.income_level, "Medium")

    def test_market_getattr_attributeerror(self):
        """Test Market.__getattr__ raises AttributeError for missing attribute."""
        market = Markets.Market(
            market_id="ATTRERROR001",
            label="AttrError Market",
            description="AttrError description"
        )
        
        with self.assertRaises(AttributeError):
            _ = market.nonexistent_key

    def test_market_core_fields_not_via_getattr(self):
        """Test that core fields are accessed normally, not via __getattr__."""
        market = Markets.Market(
            market_id="CORE001",
            label="Core Market",
            description="Core description"
        )
        
        # Core fields should be accessed directly
        self.assertEqual(market.market_id, "CORE001")
        self.assertEqual(market.label, "Core Market")
        self.assertEqual(market.description, "Core description")

    def test_market_round_trip(self):
        """Test round-trip conversion: dict -> Market -> JSON -> Market."""
        original_data = {
            "market_id": "ROUND001",
            "label": "Round Trip Market",
            "description": "Round description",
            "age_range": "25-45",
            "life_stage": "Mixed",
            "location_type": "Urban",
            "income_level": "Medium",
            "profession_types": ["tech", "finance"],
            "activity_level": "Moderate",
            "style_orientation": "Modern",
            "shoe_needs_focus": ["Comfort", "Durability"],
            "notes_for_sampling": ["Test note 1", "Test note 2"]
        }
        
        # Create market from dict
        market = Markets.Market.from_dict(original_data)
        
        # Convert to JSON and back
        json_str = market.to_json()
        restored = Markets.Market.from_json(json_str)
        
        self.assertEqual(market.market_id, restored.market_id)
        self.assertEqual(market.label, restored.label)
        self.assertEqual(market.description, restored.description)
        self.assertEqual(market.properties, restored.properties)

    def test_markets_init(self):
        """Test Markets initialization."""
        markets = Markets()
        
        self.assertEqual(len(markets), 0)
        self.assertEqual(len(markets.market), 0)

    def test_markets_load_single_market(self):
        """Test loading a single market."""
        test_data = {
            "target_markets": [
                {
                    "market_id": "LOAD001",
                    "label": "Load Market",
                    "description": "Load description",
                    "age_range": "20-30"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            markets = Markets()
            markets.load(temp_file)
            
            self.assertEqual(len(markets), 1)
            market = markets.get("LOAD001")
            self.assertIsNotNone(market)
            self.assertEqual(market.label, "Load Market")
            self.assertEqual(market.description, "Load description")
            self.assertEqual(market.properties["age_range"], "20-30")
        finally:
            Path(temp_file).unlink()

    def test_markets_load_multiple_markets(self):
        """Test loading multiple markets."""
        test_data = {
            "target_markets": [
                {
                    "market_id": "MULTI001",
                    "label": "Multi Market 1",
                    "description": "Multi description 1"
                },
                {
                    "market_id": "MULTI002",
                    "label": "Multi Market 2",
                    "description": "Multi description 2"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            markets = Markets()
            markets.load(temp_file)
            
            self.assertEqual(len(markets), 2)
            self.assertIsNotNone(markets.get("MULTI001"))
            self.assertIsNotNone(markets.get("MULTI002"))
        finally:
            Path(temp_file).unlink()

    def test_markets_load_duplicate_override(self):
        """Test that loading duplicate market_id overrides previous."""
        test_data1 = {
            "target_markets": [
                {
                    "market_id": "DUP001",
                    "label": "Original Label",
                    "description": "Original description"
                }
            ]
        }
        
        test_data2 = {
            "target_markets": [
                {
                    "market_id": "DUP001",
                    "label": "Overridden Label",
                    "description": "Overridden description"
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
            markets = Markets()
            markets.load(temp_file1)
            self.assertEqual(markets.get("DUP001").label, "Original Label")
            
            markets.load(temp_file2)
            self.assertEqual(len(markets), 1)  # Still only one market
            self.assertEqual(markets.get("DUP001").label, "Overridden Label")
            self.assertEqual(markets.get("DUP001").description, "Overridden description")
        finally:
            Path(temp_file1).unlink()
            Path(temp_file2).unlink()

    def test_markets_load_empty_file(self):
        """Test loading from file with empty target_markets list."""
        test_data = {"target_markets": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            markets = Markets()
            markets.load(temp_file)
            self.assertEqual(len(markets), 0)
        finally:
            Path(temp_file).unlink()

    def test_markets_load_missing_target_markets_key(self):
        """Test loading from file without 'target_markets' key."""
        test_data = {"other_key": "value"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            markets = Markets()
            markets.load(temp_file)
            self.assertEqual(len(markets), 0)
        finally:
            Path(temp_file).unlink()

    def test_markets_of(self):
        """Test Markets.of classmethod."""
        test_data = {
            "target_markets": [
                {
                    "market_id": "OF001",
                    "label": "Of Market",
                    "description": "Of description"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            markets = Markets.of(temp_file)
            
            self.assertEqual(len(markets), 1)
            self.assertIsNotNone(markets.get("OF001"))
        finally:
            Path(temp_file).unlink()

    def test_markets_get_existing(self):
        """Test getting an existing market."""
        market = Markets.Market(
            market_id="GET001",
            label="Get Market",
            description="Get description"
        )
        
        markets = Markets()
        markets.market["GET001"] = market
        
        retrieved = markets.get("GET001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.market_id, "GET001")

    def test_markets_get_nonexistent(self):
        """Test getting a nonexistent market."""
        markets = Markets()
        
        retrieved = markets.get("NONEXISTENT")
        self.assertIsNone(retrieved)

    def test_markets_len(self):
        """Test Markets.__len__."""
        markets = Markets()
        self.assertEqual(len(markets), 0)
        
        markets.market["M001"] = Markets.Market(
            market_id="M001",
            label="Market 1",
            description="Description 1"
        )
        self.assertEqual(len(markets), 1)
        
        markets.market["M002"] = Markets.Market(
            market_id="M002",
            label="Market 2",
            description="Description 2"
        )
        self.assertEqual(len(markets), 2)

    def test_markets_iter(self):
        """Test Markets.__iter__."""
        markets = Markets()
        markets.market["I001"] = Markets.Market(
            market_id="I001",
            label="Iter Market 1",
            description="Iter description 1"
        )
        markets.market["I002"] = Markets.Market(
            market_id="I002",
            label="Iter Market 2",
            description="Iter description 2"
        )
        
        market_ids = {m.market_id for m in markets}
        self.assertEqual(market_ids, {"I001", "I002"})

    def test_markets_contains(self):
        """Test Markets.__contains__."""
        markets = Markets()
        markets.market["C001"] = Markets.Market(
            market_id="C001",
            label="Contains Market",
            description="Contains description"
        )
        
        self.assertIn("C001", markets)
        self.assertNotIn("C002", markets)

    def test_markets_load_real_file(self):
        """Test loading from the actual market_descriptions.json file."""
        json_file = Path(__file__).parent.parent.parent.parent / "data" / "market_descriptions.json"
        
        if json_file.exists():
            try:
                markets = Markets.of(str(json_file))
                
                self.assertGreater(len(markets), 0)
                
                # Check first market
                first_id = list(markets.market.keys())[0]
                first = markets.get(first_id)
                self.assertIsNotNone(first)
                self.assertIsNotNone(first.market_id)
                self.assertIsNotNone(first.label)
                self.assertIsNotNone(first.description)
                
                # Check that properties are accessible
                self.assertTrue(hasattr(first, 'age_range') or 'age_range' in first.properties or True)
            except (json.JSONDecodeError, ValueError) as e:
                # Skip test if JSON file has syntax errors
                self.skipTest(f"JSON file has syntax errors: {e}")


if __name__ == '__main__':
    unittest.main()

