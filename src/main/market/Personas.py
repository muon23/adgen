import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class Persona:
    persona_id: str
    label: str
    market_affinity: dict[str, float]
    prevalence: float
    properties: dict[str, Any] = field(default_factory=dict)  # Other properties describing the persona

    def to_json(self) -> str:
        """
        Convert content to JSON string. Flatten properties.

        Returns:
            JSON string with all properties flattened (not nested under 'properties')
        """
        result = {
            "persona_id": self.persona_id,
            "label": self.label,
            "prevalence": self.prevalence,
            "market_affinity": [
                {"market_id": market_id, "weight": weight}
                for market_id, weight in self.market_affinity.items()
            ]
        }
        # Add all properties
        result.update(self.properties)
        return json.dumps(result, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Persona":
        """
        Create a Persona object from the JSON string.

        Args:
            json_str: JSON string containing persona data

        Returns:
            Persona instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Persona":
        """
        Create a Persona object from a dictionary.

        Args:
            data: Dictionary containing persona data

        Returns:
            Persona instance
        """
        # Extract core fields
        persona_id = data.get("persona_id", "")
        label = data.get("label", "")
        prevalence = data.get("prevalence", 0.0)

        # Convert market_affinity from list to dict
        market_affinity = {}
        market_affinity_list = data.get("market_affinity", [])
        if isinstance(market_affinity_list, list):
            for item in market_affinity_list:
                if isinstance(item, dict):
                    market_id = item.get("market_id")
                    weight = item.get("weight", 0.0)
                    if market_id:
                        market_affinity[market_id] = weight

        # All other fields go into properties
        core_fields = {"persona_id", "label", "market_affinity", "prevalence"}
        properties = {k: v for k, v in data.items() if k not in core_fields}

        return cls(
            persona_id=persona_id,
            label=label,
            market_affinity=market_affinity,
            prevalence=prevalence,
            properties=properties
        )

    def __getattr__(self, name: str) -> Any:
        """
        Access properties using attribute syntax.

        This allows accessing properties like persona.type instead of persona.properties["type"].
        Core fields (persona_id, label, market_affinity, prevalence) are accessed normally.

        Args:
            name: Property name to access

        Returns:
            Property value

        Raises:
            AttributeError: If property doesn't exist
        """
        if name in self.properties:
            return self.properties[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class Personas:

    def __init__(self):
        """Initialize an empty Personas collection."""
        self.persona: dict[str, Persona] = {}  # persona_id -> Persona lookup

    @classmethod
    def of(cls, file: str) -> "Personas":
        """
        Create a Personas object by reading data from a JSON persona file.
        
        Args:
            file: Path to JSON file containing personas
            
        Returns:
            Personas instance with loaded personas
        """
        personas = cls()
        personas.load(file)
        return personas

    def load(self, file: str):
        """
        Load more data from a JSON persona file. Duplicated persona_id will be overridden.
        
        Args:
            file: Path to JSON file containing personas
        """
        file_path = Path(file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "personas" in data:
            for persona_data in data["personas"]:
                persona = Persona.from_dict(persona_data)
                self.persona[persona.persona_id] = persona

    def get(self, persona_id: str) -> Optional[Persona]:
        """
        Get Persona by ID.
        
        Args:
            persona_id: ID of the persona to retrieve
            
        Returns:
            Persona instance if found, None otherwise
        """
        return self.persona.get(persona_id)

    def __len__(self) -> int:
        """Return the number of personas in the collection."""
        return len(self.persona)

    def __iter__(self):
        """Iterate over personas."""
        return iter(self.persona.values())

    def __contains__(self, persona_id: str) -> bool:
        """Check if a persona with the given ID exists."""
        return persona_id in self.persona
