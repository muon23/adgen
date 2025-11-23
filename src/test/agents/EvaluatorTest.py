import unittest
import sys
from pathlib import Path

# Add project root to path to import modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "main"))

from agents.Evaluator import Evaluator
from agents.Layouts import Layouts
from market.Personas import Personas


class EvaluatorTest(unittest.TestCase):
    test_data = {
        "layout_id": "hero_plus_bullets",
        "slot_values": {
            'headline': 'Premium cushioning for the everyday city run',
            'subheadline': 'The Nike Vomero Premium wraps your feet in plush cushioning, breathable support, and durable traction—built to handle daily miles, crowded pavements, and everything your urban commute throws at you.',
            'benefits': [
                'Soft, responsive cushioning for comfortable daily runs and walks',
                'Breathable upper material to keep feet cooler in busy city conditions',
                'Secure, supportive fit designed for consistent everyday use',
                'Durable outsole built to stand up to regular pavement pounding',
                'Premium detailing and finish for a polished look on and off the run'
            ],
            'details_paragraph': "Designed as a cushioned neutral running shoe, the Nike Vomero Premium combines a plush underfoot feel with breathable upper and hard‑wearing outsole. It's made to transition smoothly from your commute to your workout and back again.",
            'cta_text': "Shop Now",
            'footer_note': "Check retailer's site for current sizing, availability, and return policy."
        }
    }

    def test_evaluate_ad(self):
        """Test evaluating an ad with a persona."""
        # Load layouts
        layout_file = str(project_root / "data" / "layout_descriptions_jinja2.json")
        layouts = Layouts(layout_file)
        
        # Render html_4b with slot_values
        layout_id = self.test_data["layout_id"]
        slot_values = self.test_data["slot_values"]
        ad_html = layouts.render_html_4b(layout_id, **slot_values)
        
        print(f"\n=== Rendered HTML (length: {len(ad_html)}) ===")
        print(ad_html[:200] + "..." if len(ad_html) > 200 else ad_html)
        
        # Load personas
        persona_file = str(project_root / "data" / "personas_realworld_clustered_z.json")
        personas = Personas.of(persona_file)
        
        # Get first persona (or you could select a specific one)
        if len(personas) == 0:
            self.fail("No personas found in file")
        
        persona = next(iter(personas))
        print(f"\n=== Using Persona: {persona.persona_id} - {persona.label} ===")
        
        # Create evaluator
        evaluator = Evaluator(
            llm="gpt-5.1",
            persona=persona
        )
        
        # Evaluate the ad
        print(f"\n=== Evaluating ad ===")
        try:
            result = evaluator.evaluate(ad_html)
        except Exception as e:
            print(f"\n!!! Exception during evaluation: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # Debug: Print the result
        print(f"\n=== Evaluation Result ===")
        print(f"Persona ID: {result.get('persona_id')}")
        print(f"Ratings: {result.get('ratings')}")
        print(f"Feedback text: {result.get('feedback_text', '')[:200]}...")
        print(f"Improvement suggestions: {result.get('improvement_suggestions', [])}")
        
        # Assertions
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertEqual(result.get("persona_id"), persona.persona_id, "persona_id should match")
        self.assertIn("ratings", result, "Result should contain 'ratings'")
        self.assertIn("feedback_text", result, "Result should contain 'feedback_text'")
        self.assertIn("improvement_suggestions", result, "Result should contain 'improvement_suggestions'")
        
        # Check ratings structure
        ratings = result.get("ratings", {})
        self.assertIn("clarity", ratings, "Ratings should contain 'clarity'")
        self.assertIn("trustworthiness", ratings, "Ratings should contain 'trustworthiness'")
        self.assertIn("relevance", ratings, "Ratings should contain 'relevance'")
        self.assertIn("aesthetic_appeal", ratings, "Ratings should contain 'aesthetic_appeal'")
        self.assertIn("purchase_likelihood", ratings, "Ratings should contain 'purchase_likelihood'")
        
        # Check rating values are in range 0-10
        for rating_name, rating_value in ratings.items():
            self.assertIsInstance(rating_value, (int, float), f"{rating_name} should be a number")
            self.assertGreaterEqual(rating_value, 0, f"{rating_name} should be >= 0")
            self.assertLessEqual(rating_value, 10, f"{rating_name} should be <= 10")


if __name__ == '__main__':
    unittest.main()
