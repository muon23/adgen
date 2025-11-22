import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class Market:
    market_id: str
    label: str
    description: str
    properties: dict[str, Any] = field(default_factory=dict)  # Other properties describing the market

    def to_json(self) -> str:
        """
        Convert content to JSON string. Flatten properties.

        Returns:
            JSON string with all properties flattened (not nested under 'properties')
        """
        result = {
            "market_id": self.market_id,
            "label": self.label,
            "description": self.description
        }
        # Add all properties
        result.update(self.properties)
        return json.dumps(result, indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Market":
        """
        Create a Market object from the JSON string.

        Args:
            json_str: JSON string containing market data

        Returns:
            Market instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Market":
        """
        Create a Market object from a dictionary.

        Args:
            data: Dictionary containing market data

        Returns:
            Market instance
        """
        # Extract core fields
        market_id = data.get("market_id", "")
        label = data.get("label", "")
        description = data.get("description", "")

        # All other fields go into properties
        core_fields = {"market_id", "label", "description"}
        properties = {k: v for k, v in data.items() if k not in core_fields}

        return cls(
            market_id=market_id,
            label=label,
            description=description,
            properties=properties
        )

    def __getattr__(self, name: str) -> Any:
        """
        Access properties using attribute syntax.

        This allows accessing properties like market.age_range instead of market.properties["age_range"].
        Core fields (market_id, label, description) are accessed normally.

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


class Markets:

    def __init__(self):
        """Initialize an empty Markets collection."""
        self.market: dict[str, Market] = {}  # market_id -> Market lookup

    @classmethod
    def of(cls, file: str) -> "Markets":
        """
        Create a Markets object by reading data from a JSON market file.
        
        Args:
            file: Path to JSON file containing markets
            
        Returns:
            Markets instance with loaded markets
        """
        markets = cls()
        markets.load(file)
        return markets

    def load(self, file: str):
        """
        Load more data from a JSON market file. Duplicated market_id will be overridden.
        
        Args:
            file: Path to JSON file containing markets
        """
        file_path = Path(file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "target_markets" in data:
            for market_data in data["target_markets"]:
                market = Market.from_dict(market_data)
                self.market[market.market_id] = market

    def get(self, market_id: str) -> Optional[Market]:
        """
        Get Market by ID.
        
        Args:
            market_id: ID of the market to retrieve
            
        Returns:
            Market instance if found, None otherwise
        """
        return self.market.get(market_id)

    def __len__(self) -> int:
        """Return the number of markets in the collection."""
        return len(self.market)

    def __iter__(self):
        """Iterate over markets."""
        return iter(self.market.values())

    def __contains__(self, market_id: str) -> bool:
        """Check if a market with the given ID exists."""
        return market_id in self.market
