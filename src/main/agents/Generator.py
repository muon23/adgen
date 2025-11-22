import json
import textwrap
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import llms
from .Layouts import Layouts


class Generator(ABC):
    """Base class for advertisement generators."""

    # Shared system prompt template
    DEFAULT_SYSTEM_PROMPT = textwrap.dedent("""
    You are an HTML advertisement generator for a shoe brand.
    
    You will receive:
    - A PRODUCT_URL for the shoe's product page.
    - A catalog of possible ad layouts.
    - A target market name or user ID.
    {{mode_specific_input}}
    
    Your responsibilities:
    1. Fetch and read the PRODUCT_URL using your browsing capability.
    2. Extract key product information relevant for advertisement: purpose, materials, construction,
        support/cushioning technology, benefits, durability, fit notes, intended user,
        use-case scenarios, and any distinctive features.
    3. Select the single most appropriate layout from the LAYOUT_CATALOG.
    4. Fill **all** content slots listed under that layout's "content_slots".
    5. Use the layout's "html" template **as a guide only** to understand the intended structure, tone, and emphasis — 
        you do NOT need to render or output any HTML. You only decide content based on what the layout implies.
    6. Output a structured JSON object exactly in the required format:
    {{mode_specific_output_format}}
    
    {{mode_specific_behavior}}
    - Do not hallucinate product facts not found on the product page.
    - If a slot expects a list (e.g., "benefits"), output a JSON array.
    - Always produce valid JSON with no extra text.
    
    Each layout in the LAYOUT_CATALOG is a JSON object with at least:
    - "id": string
    - "persona_fit": string (metadata only, for humans)
    - "layout_features": list of strings
    - "content_slots": list of slot names (strings)
    - "html": string (Jinja2-style template for human reference only)

    {{layout_catalog}}
    """)

    # Shared user prompt template
    DEFAULT_USER_PROMPT = textwrap.dedent("""
    {{target_market_or_user}}
    
    {{product_url}}
    
    {{previous_ad_json}}
    
    {{feedback_list_json}}
    
    Your task:
    - First action: fetch and read PRODUCT_URL using your browsing tool.
    - Select a layout from the layout catalog.
    - Fill all of that layout's content slots.
    - Return ONLY a single JSON object:
    {{mode_specific_output_format}}
    """)

    def __init__(
            self,
            llm: str,
            layout_catalog_path: str,
            target_market_or_user: Optional[str] = None,
            system_prompt: Optional[str] = None,
            user_prompt: Optional[str] = None
    ):
        """
        Initialize the generator.
        
        Args:
            llm: LLM model name
            layout_catalog_path: Path to layout descriptions JSON file (required)
            target_market_or_user: Target market name or user ID for ad generation
            system_prompt: Override for DEFAULT_SYSTEM_PROMPT
            user_prompt: Override for DEFAULT_USER_PROMPT
        """
        self.llm = llms.of(llm)
        self.target_market_or_user = target_market_or_user or ""
        self.system_prompt = system_prompt if system_prompt is not None else self.DEFAULT_SYSTEM_PROMPT
        self.user_prompt = user_prompt if user_prompt is not None else self.DEFAULT_USER_PROMPT

        # Load layouts using Layouts class
        self.layouts = Layouts(layout_catalog_path)

    def _get_template_variables(
            self,
            product_url: str,
            previous_ad_json: Optional[str] = None,
            feedback_list_json: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get template variables for prompt substitution."""
        mode_specific_input = self._get_mode_specific_input()
        mode_specific_output_format = self._get_mode_specific_output_format()
        mode_specific_behavior = self._get_mode_specific_behavior()
        layout_catalog_str = self.layouts.for_generator()

        return {
            "mode_specific_input": mode_specific_input,
            "mode_specific_output_format": mode_specific_output_format,
            "mode_specific_behavior": mode_specific_behavior,
            "layout_catalog": layout_catalog_str,
            "target_market_or_user": self.target_market_or_user,
            "product_url": f"PRODUCT_URL: {product_url}",
            "previous_ad_json": previous_ad_json or "",
            "feedback_list_json": feedback_list_json or ""
        }

    @abstractmethod
    def _get_mode_specific_input(self) -> str:
        """Get mode-specific input description."""
        pass

    @abstractmethod
    def _get_mode_specific_output_format(self) -> str:
        """Get mode-specific output format description."""
        pass

    @abstractmethod
    def _get_mode_specific_behavior(self) -> str:
        """Get mode-specific behavior description."""
        pass

    def generate(
            self,
            product_url: str,
            previous_ad_json: Optional[str] = None,
            feedback_list_json: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an advertisement.
        
        Args:
            product_url: URL of the product page
            previous_ad_json: Formatted previous ad JSON string (for adaptive mode)
            feedback_list_json: Formatted feedback list JSON string (for adaptive mode)
            
        Returns:
            Dictionary matching generator_output.json schema
        """
        # Build messages with template placeholders
        messages = [
            ("system", self.system_prompt),
            ("user", self.user_prompt)
        ]

        # Get template variables for substitution
        template_vars = self._get_template_variables(
            product_url,
            previous_ad_json=previous_ad_json,
            feedback_list_json=feedback_list_json
        )

        # Invoke LLM with messages and template variables as arguments
        # The Llm.invoke() method will handle Jinja2 template rendering internally
        response = self.llm.invoke(messages, arguments=template_vars, prompt_format="jinja2")

        # Parse JSON response
        response_text = response.text if hasattr(response, 'text') else str(response)

        # Try to extract JSON from response (in case there's extra text)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        result = json.loads(response_text)

        # Ensure output matches schema (base implementation returns what's in result)
        output = {
            "selected_layout_id": result.get("selected_layout_id", ""),
            "filled_slots": result.get("filled_slots", {})
        }
        
        # Add improvement_summary if present (for adaptive mode)
        if "improvement_summary" in result:
            output["improvement_summary"] = result.get("improvement_summary", "")

        return output
