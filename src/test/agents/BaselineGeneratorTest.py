import unittest
import sys
from pathlib import Path

# Add project root to path to import modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "main"))

from agents.BaselineGenerator import BaselineGenerator


class BaselineGeneratorTest(unittest.TestCase):
    """Unit tests for the BaselineGenerator class."""

    def test_generate_nike_vomero_premium(self):
        """Test generating an ad for the Nike Vomero Premium product page."""
        # Get path to layout descriptions file
        layout_file = str(project_root / "data" / "layout_descriptions_jinja2.json")
        
        # Initialize generator with the same LLM as in the notebook
        generator = BaselineGenerator(
            llm="gpt-5.1",
            layout_catalog_path=layout_file,
            target_market_or_user="URBAN_COMMUTERS"
        )
        
        # Debug: Print generator configuration
        print(f"\n=== Generator Configuration ===")
        print(f"LLM: {generator.llm}")
        print(f"Target market: {generator.target_market_or_user}")
        print(f"Layouts loaded: {len(generator.layouts.layout_descriptions)}")
        if generator.layouts.layout_descriptions:
            print(f"First layout ID: {generator.layouts.layout_descriptions[0].get('id', 'N/A')}")
        
        # Generate ad for the Nike Vomero Premium
        product_url = "https://runrepeat.com/nike-vomero-premium"
        print(f"\n=== Generating ad for: {product_url} ===")
        
        try:
            result = generator.generate(product_url)
        except Exception as e:
            print(f"\n!!! Exception during generation: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Debug: Print the result to see what we got
        print(f"\n=== Generator Result ===")
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        # Basic assertions
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("selected_layout_id", result, "Result should contain 'selected_layout_id'")
        self.assertIn("filled_slots", result, "Result should contain 'filled_slots'")
        
        # Check that selected_layout_id is not empty
        selected_layout_id = result.get("selected_layout_id", "")
        print(f"Selected layout ID: '{selected_layout_id}'")
        if not selected_layout_id:
            print("WARNING: selected_layout_id is empty!")
        self.assertNotEqual(selected_layout_id, "", "selected_layout_id should not be empty")
        
        # Check that filled_slots is not empty
        filled_slots = result.get("filled_slots", {})
        self.assertIsInstance(filled_slots, dict, "filled_slots should be a dictionary")
        print(f"Filled slots: {filled_slots}")
        print(f"Number of filled slots: {len(filled_slots)}")
        if len(filled_slots) == 0:
            print("WARNING: filled_slots is empty!")
        self.assertGreater(len(filled_slots), 0, "filled_slots should not be empty")
        
        # Check that each slot has content
        for slot_name, slot_value in filled_slots.items():
            self.assertIsNotNone(slot_value, f"Slot '{slot_name}' should have a value")
            if isinstance(slot_value, list):
                self.assertGreater(len(slot_value), 0, f"Slot '{slot_name}' list should not be empty")
            elif isinstance(slot_value, str):
                self.assertGreater(len(slot_value.strip()), 0, f"Slot '{slot_name}' string should not be empty")
            print(f"  Slot '{slot_name}': {slot_value}")


if __name__ == '__main__':
    unittest.main()

