import json
import textwrap
from typing import Any, Dict, Optional

from .Generator import Generator


class AdaptiveGenerator(Generator):
    """Generator for adaptive (improved) advertisements based on feedback."""
    
    # Adaptive-specific constants
    DEFAULT_ADAPTIVE_INPUT = textwrap.dedent("""
    - Your previous ad layout and the contents filled
    - A list of customer feedbacks
    """)
    
    DEFAULT_ADAPTIVE_OUTPUT_FORMAT = textwrap.dedent("""
    - selected_layout_id: The ID of the layout chosen
    - filled_slots: The "content_slots" in the layout.  Fill all slots.  Do not invent slots.
    - improvement_summary: Describes what improvements was made from previous output.
    """)
    
    DEFAULT_ADAPTIVE_BEHAVIOR = textwrap.dedent("""
    You are improving a previous advertisement based solely on customer feedback.

    You will be given:
    - A previous ad (selected_layout_id, filled_content_slots).
    - A list of customer feedback objects.
    
    [RULES]
    - Learn from patterns in the feedback texts and ratings.
    - Only switch layouts if multiple feedback items indicate a mismatch with the current structure 
        (e.g., "too wordy," "needs more detail," "overwhelming," "not enough information," etc.).
    - Improve clarity, trust, relevance, emotional resonance, or information density according to repeated feedback themes.
    - Prefer conservative improvements. Do not drastically change tone or messaging unless feedback consistently demands it.
    """)
    
    def __init__(
            self,
            llm: str,
            layout_catalog_path: Optional[str] = None,
            target_market_or_user: Optional[str] = None,
            system_prompt: Optional[str] = None,
            user_prompt: Optional[str] = None,
            adaptive_input: Optional[str] = None,
            adaptive_output_format: Optional[str] = None,
            adaptive_behavior: Optional[str] = None
    ):
        """
        Initialize the adaptive generator.
        
        Args:
            llm: LLM model name
            layout_catalog_path: Path to layout descriptions JSON file. 
                                 Defaults to data/layout_descriptions_jinja2.json
            target_market_or_user: Target market name or user ID for ad generation
            system_prompt: Override for DEFAULT_SYSTEM_PROMPT
            user_prompt: Override for DEFAULT_USER_PROMPT
            adaptive_input: Override for DEFAULT_ADAPTIVE_INPUT
            adaptive_output_format: Override for DEFAULT_ADAPTIVE_OUTPUT_FORMAT
            adaptive_behavior: Override for DEFAULT_ADAPTIVE_BEHAVIOR
        """
        super().__init__(llm, layout_catalog_path, target_market_or_user, system_prompt, user_prompt)
        self.adaptive_input = adaptive_input if adaptive_input else self.DEFAULT_ADAPTIVE_INPUT
        self.adaptive_output_format = adaptive_output_format if adaptive_output_format else self.DEFAULT_ADAPTIVE_OUTPUT_FORMAT
        self.adaptive_behavior = adaptive_behavior if adaptive_behavior else self.DEFAULT_ADAPTIVE_BEHAVIOR
    
    def _get_mode_specific_input(self) -> str:
        return self.adaptive_input
    
    def _get_mode_specific_output_format(self) -> str:
        return self.adaptive_output_format
    
    def _get_mode_specific_behavior(self) -> str:
        return self.adaptive_behavior
    
    def generate(
        self,
        product_url: str,
        previous_ad: Optional[Dict[str, Any]] = None,
        feedback_list: Optional[list[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate an improved advertisement based on feedback.
        
        Args:
            product_url: URL of the product page
            previous_ad: Previous ad output (required for adaptive mode)
            feedback_list: List of feedback objects (required for adaptive mode)
            
        Returns:
            Dictionary with selected_layout_id, filled_slots, and improvement_summary
        """
        # Format previous ad as JSON
        previous_ad_json = ""
        if previous_ad:
            previous_ad_json = f"Previous ad:\n{json.dumps(previous_ad, indent=2)}"
        
        # Format feedback list as JSON
        feedback_list_json = ""
        if feedback_list:
            feedback_list_json = f"Customer feedback:\n{json.dumps(feedback_list, indent=2)}"
        
        # Call base class generate with formatted JSON strings
        return super().generate(product_url, previous_ad_json=previous_ad_json, feedback_list_json=feedback_list_json)

