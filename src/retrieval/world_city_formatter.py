"""
World City Response Formatter
Generates friendly responses for non-Moroccan cities.
"""

from typing import Dict, Optional


class WorldCityResponseFormatter:
    """Formats responses for global cities (non-Moroccan)."""
    
    @staticmethod
    def format_world_city_response(city_data: Dict) -> str:
        """
        Generate a response for a non-Moroccan city.
        
        Args:
            city_data: City information from global dataset
            
        Returns:
            Formatted response string
        """
        city_name = city_data.get('city', 'Unknown')
        country = city_data.get('country', 'Unknown')
        population = city_data.get('population', 'N/A')
        admin_name = city_data.get('admin_name', 'N/A')
        lat = city_data.get('lat', 'N/A')
        lng = city_data.get('lng', 'N/A')
        capital = city_data.get('capital', 'N/A')
        
        # Format population with commas if it's a number
        try:
            pop_int = int(float(population))
            population = f"{pop_int:,}"
        except (ValueError, TypeError):
            population = "N/A"
        
        # Build response
        response = f"Sorry, {city_name} is not in Morocco so it's not my specialty.\n"
        response += f"But here's what I found about {city_name}:\n"
        
        facts = []
        
        if country and country != 'N/A':
            facts.append(f"- Country: {country}")
        
        if population and population != 'N/A':
            facts.append(f"- Population: {population}")
        
        if admin_name and admin_name != 'N/A':
            facts.append(f"- Located in: {admin_name}")
        
        if capital and capital != 'N/A' and capital.lower() != 'admin':
            # Capitalize first letter for better readability
            capital_type = capital.capitalize() if capital else ''
            if capital_type:
                facts.append(f"- Capital: {capital_type}")
        
        if lat and lng and lat != 'N/A' and lng != 'N/A':
            try:
                lat_f = float(lat)
                lng_f = float(lng)
                facts.append(f"- Coordinates: {lat_f:.2f}, {lng_f:.2f}")
            except (ValueError, TypeError):
                pass
        
        # Add facts (max 5)
        for fact in facts[:5]:
            response += fact + "\n"
        
        response += "\nIf you want, I can help you explore amazing Moroccan cities instead!"
        
        return response
