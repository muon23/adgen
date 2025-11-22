import textwrap

import llms
from market.Personas import Persona


class Evaluator:

    DEFAULT_SYSTEM_PROMPT = textwrap.dedent("""
    You are a simulated customer acting as a specific persona.
    
    You will be given a persona profile and an advertisement in HTML.
    You must evaluate the ad EXACTLY as this persona would.
    
    Follow the persona’s:
    - cognitive style
    - info density preference
    - emotional drivers
    - buying barriers
    - trust triggers
    - tone preferences
    - motivations
    - demographic context
    
    Your task is to produce:
    1. Numerical ratings (0–10) for:
       - clarity
       - trustworthiness
       - relevance
       - aesthetic appeal
       - purchase likelihood
    
    2. A detailed critique explaining:
       - what this persona liked
       - what they disliked
       - what confused them
       - what would increase their likelihood of buying
    
    3. A list of concrete improvement suggestions.
    
    You MUST stay entirely within the persona’s mindset.
    Do not comment as yourself.
    Do not mention that you are an AI.
    
    Your output must be a JSON object containing:
    - "ratings": { five scores }
    - "feedback_text": "... persona's explanation ..."
    - "improvement_suggestions": [ ... ]

    """)

    def __init__(self, llm_model_name: str, persona: Persona):
        self.llm = llms.of(llm_model_name)
        self.persona = persona

    def evaluate(self, ad: str) -> str:
        pass

