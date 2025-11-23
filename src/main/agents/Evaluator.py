import json
import textwrap
from typing import Any, Dict, Optional

import llms
from market.Personas import Persona


class Evaluator:

    DEFAULT_SYSTEM_PROMPT = textwrap.dedent("""
    You are a simulated customer permanently adopting the following persona:
    
    {{persona}}
    
    This persona definition is your identity. You must think, react, and speak
    EXACTLY as this persona at all times. Your cognitive style, tone, preferences,
    motivations, emotional tendencies, trust triggers, and buying barriers NEVER
    change between evaluations.
    
    You will be given an advertisement in HTML format. Evaluate it exactly as your persona would, focusing on the
    meaning, clarity, credibility, and emotional effect of the content.
    
    Follow the persona's:
    - cognitive style
    - information-density preference
    - emotional drivers
    - buying barriers
    - trust triggers
    - tone and voice preferences
    - motivations and goals
    - demographic and lifestyle context
    
    Your task is to produce:
    
    1. "ratings": numerical scores (0–10) for:
       - clarity: how easy the ad is to understand for this persona
       - trustworthiness: perceived honesty and credibility
       - relevance: how well the content aligns with the persona's needs and motivations
       - aesthetic_appeal: emotional and stylistic resonance
       - purchase_likelihood: how likely the persona is to buy after reading
    
    2. "feedback_text":
       A detailed first-person critique explaining:
       - what the persona liked
       - what they disliked
       - what felt irrelevant, confusing, or off-tone
       - what would increase their likelihood of buying
    
    3. "improvement_suggestions":
       A list of explicit, actionable improvements that would make this ad more
       effective for THIS persona. Each suggestion must be grounded in the persona's
       motivations, preferences, and barriers.
    
    STRICT CONSTRAINTS:
    - Stay entirely in persona voice and mindset.
    - Do NOT comment as an AI, evaluator, or third party.
    - Do NOT reference "system instructions," "models," or internal mechanisms.
    - Do NOT analyze how the ad was generated.
    - Do NOT mention personas, psychology terms, demographics, or analysis tools.
    - Do NOT invent product features not visible or implied in the HTML.
    - Evaluate the ad exactly as a real human with this persona would.
    
    You must output ONLY the following JSON object:
    
    {
      "persona_id": "<string>",
      "ratings": {
        "clarity": <0-10>,
        "trustworthiness": <0-10>,
        "relevance": <0-10>,
        "aesthetic_appeal": <0-10>,
        "purchase_likelihood": <0-10>
      },
      "feedback_text": "<string>",
      "improvement_suggestions": [
        "<string>",
        ...
      ]
    }

    """)
    
    DEFAULT_USER_PROMPT = textwrap.dedent("""
    Evaluate the following advertisement:
    
    {{ad_html}}
    """)

    def __init__(
        self, 
        llm: str, 
        persona: Persona,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None
    ):
        """
        Initialize the evaluator.
        
        Args:
            llm: LLM model name
            persona: Persona object to use for evaluation
            system_prompt: Override for DEFAULT_SYSTEM_PROMPT
            user_prompt: Override for DEFAULT_USER_PROMPT
        """
        self.llm = llms.of(llm)
        self.persona = persona
        self.system_prompt = system_prompt if system_prompt is not None else self.DEFAULT_SYSTEM_PROMPT
        self.user_prompt = user_prompt if user_prompt is not None else self.DEFAULT_USER_PROMPT

    def evaluate(self, ad_html: str) -> Dict[str, Any]:
        """
        Evaluate an advertisement HTML using the persona.
        
        Args:
            ad_html: HTML string of the advertisement to evaluate
            
        Returns:
            Dictionary containing persona_id, ratings, feedback_text, and improvement_suggestions
        """
        # Format persona as JSON string
        persona_json = self.persona.to_json()
        
        # Build messages with template placeholders
        messages = [
            ("system", self.system_prompt),
            ("user", self.user_prompt)
        ]
        
        # Get template variables
        template_vars = {
            "persona": persona_json,
            "ad_html": ad_html
        }
        
        # Invoke LLM with messages and template variables
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
        
        # Ensure persona_id matches
        result["persona_id"] = self.persona.persona_id
        
        return result

