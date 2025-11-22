import textwrap
from typing import Optional

from .Generator import Generator


class BaselineGenerator(Generator):
    """Generator for baseline (initial) advertisements."""
    
    # Baseline-specific constants
    DEFAULT_BASELINE_INPUT = ""
    
    DEFAULT_BASELINE_OUTPUT_FORMAT = textwrap.dedent("""
    - selected_layout_id: The ID of the layout chosen
    - filled_slots: The "content_slots" in the layout.  Fill all slots.  Do not invent slots.
    """)
    
    DEFAULT_BASELINE_BEHAVIOR = textwrap.dedent("""
    You are generating an initial advertisement with no prior versions and no feedback.

    [RULES]
    - Write broadly suitable marketing copy for the given target market name.
    - Use concise, factual, moderately energetic language appropriate for general audiences.
    """)
    
    def __init__(
            self,
            llm: str,
            layout_catalog_path: str,
            target_market_or_user: Optional[str] = None,
            system_prompt: Optional[str] = None,
            user_prompt: Optional[str] = None,
            baseline_input: Optional[str] = None,
            baseline_output_format: Optional[str] = None,
            baseline_behavior: Optional[str] = None
    ):
        """
        Initialize the baseline generator.
        
        Args:
            llm: LLM model name
            layout_catalog_path: Path to layout descriptions JSON file (required)
            target_market_or_user: Target market name or user ID for ad generation
            system_prompt: Override for DEFAULT_SYSTEM_PROMPT
            user_prompt: Override for DEFAULT_USER_PROMPT
            baseline_input: Override for DEFAULT_BASELINE_INPUT
            baseline_output_format: Override for DEFAULT_BASELINE_OUTPUT_FORMAT
            baseline_behavior: Override for DEFAULT_BASELINE_BEHAVIOR
        """
        super().__init__(llm, layout_catalog_path, target_market_or_user, system_prompt, user_prompt)
        self.baseline_input = baseline_input if baseline_input is not None else self.DEFAULT_BASELINE_INPUT
        self.baseline_output_format = baseline_output_format if baseline_output_format is not None else self.DEFAULT_BASELINE_OUTPUT_FORMAT
        self.baseline_behavior = baseline_behavior if baseline_behavior is not None else self.DEFAULT_BASELINE_BEHAVIOR
    
    def _get_mode_specific_input(self) -> str:
        return self.baseline_input
    
    def _get_mode_specific_output_format(self) -> str:
        return self.baseline_output_format
    
    def _get_mode_specific_behavior(self) -> str:
        return self.baseline_behavior

