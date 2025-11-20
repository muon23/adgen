import json
from typing import Any, Optional

from jinja2 import Template


class Layouts:
    """Manages layout descriptions for advertisement generation."""

    def __init__(self, layout_file: str):
        """
        Initialize Layouts by reading a layout description file.
        
        Args:
            layout_file: Path to layout descriptions JSON file (required)
        """

        with open(layout_file, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
            self.slot_meta = layout_data.get("slot_meta", {})
            self.layout_descriptions = layout_data.get("layout_descriptions", [])
            
            # Create a dictionary for efficient lookup by ID
            self.layouts_by_id: dict[str, dict] = {}
            for layout in self.layout_descriptions:
                layout_id = layout.get("id")
                if layout_id:
                    self.layouts_by_id[layout_id] = layout

    def for_generator(self) -> str:
        """
        Outputs JSON string for a Generator object.
        
        Contains a list of all layout descriptions with:
        - id: layout identifier
        - layout_features: list of feature strings
        - content_slots: dict mapping slot names to their slot_meta
        - html_4b: HTML template for bot/backend use
        
        Returns:
            JSON string containing layout descriptions for generator use
        """
        generator_layouts = []
        
        for layout in self.layout_descriptions:
            # Convert content_slots from list to dict
            content_slots_dict = {}
            for slot_name in layout.get("content_slots", []):
                if slot_name in self.slot_meta:
                    content_slots_dict[slot_name] = self.slot_meta[slot_name]
                else:
                    # If slot_meta not found, create a minimal entry
                    content_slots_dict[slot_name] = {
                        "description": f"Content slot: {slot_name}",
                        "type": "string"
                    }
            
            generator_layout = {
                "id": layout.get("id", ""),
                "layout_features": layout.get("layout_features", []),
                "content_slots": content_slots_dict,
                "html_4b": layout.get("html_4b", "")
            }
            generator_layouts.append(generator_layout)
        
        return json.dumps(generator_layouts, indent=2)

    def get(self, layout_id: str) -> Optional[dict]:
        """
        Get a layout description by ID.
        
        Args:
            layout_id: ID of the layout to retrieve
            
        Returns:
            Layout description dictionary if found, None otherwise
        """
        return self.layouts_by_id.get(layout_id)
    
    def for_human(self, layout_id: str, **kwargs: Any) -> str:
        """
        Outputs an HTML page for a specific layout using html_4p field as a template.
        
        The content slots are filled with values from **kwargs.
        
        Args:
            layout_id: ID of the layout to render
            **kwargs: Values for content slots (e.g., headline="...", benefits=[...])
            
        Returns:
            Rendered HTML string
            
        Raises:
            ValueError: If layout_id is not found
        """
        # Find the layout by ID using the dictionary
        layout = self.get(layout_id)
        
        if layout is None:
            raise ValueError(f"Layout with id '{layout_id}' not found")
        
        # Get the html_4p template
        html_template_str = layout.get("html_4p", "")
        if not html_template_str:
            raise ValueError(f"Layout '{layout_id}' does not have html_4p template")
        
        # Render the template with Jinja2
        template = Template(html_template_str)
        rendered_html = template.render(**kwargs)
        
        return rendered_html

