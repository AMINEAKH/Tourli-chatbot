"""
City Detection Module
Handles detection of Moroccan and non-Moroccan cities with fuzzy matching.
"""

import re
import csv
import os
from difflib import get_close_matches
from typing import Optional, Dict, Tuple


class CityDetector:
    """Detects Moroccan and global cities from user input."""
    
    def __init__(self, global_cities_csv: str):
        """
        Initialize the CityDetector.
        
        Args:
            global_cities_csv: Path to the global cities CSV file
        """
        self.moroccan_cities = {
            "agadir", "al hoceima", "azrou", "beni mellal", "berkane",
            "casablanca", "chefchaouen", "dakhla", "el jadida", "errachidia",
            "essaouira", "fes", "guelmim", "ifrane", "kenitra",
            "khouribga", "laayoune", "larache", "marrakech", "martil",
            "meknes", "mohammedia", "nador", "ouarzazate", "oujda",
            "rabat", "safi", "sale", "tangier", "tetouan",
            "tiznit", "taroudant", "tata", "tanger med", "sidi ifni"
        }
        
        # Common misspellings and abbreviations for Moroccan cities
        self.moroccan_city_misspellings = {
            "casa": "casablanca",
            "cali": "casablanca",
            "mkech": "marrakech",
            "marrakch": "marrakech",
            "marakech": "marrakech",
            "marakesh": "marrakech",
            "fesss": "fes",
            "ksablanka": "casablanca",
            "casablanka": "casablanca",
            "casablanca": "casablanca",
            "agdir": "agadir",
            "agad": "agadir",
            "rabay": "rabat",
            "tangr": "tangier",
            "tanger": "tangier",
            "tetouan": "tetouan",
            "meknes": "meknes",
        }
        
        # Load global cities dataset (this will also extract countries)
        self.global_cities = self._load_global_cities(global_cities_csv)
        
        # Get the extracted countries from the CSV loading
        self.countries = getattr(self, '_extracted_countries', set())
    
    def _load_global_cities(self, csv_path: str) -> Dict[str, Dict]:
        """
        Load global cities from CSV.
        For cities with duplicate names, keeps the one with highest population.
        
        Args:
            csv_path: Path to worldcities_clean.csv
            
        Returns:
            Dict mapping normalized city names to city data
        """
        cities = {}
        countries = set()  # Also track countries while loading
        try:
            if not os.path.exists(csv_path):
                print(f"[Warning] Cities CSV not found at {csv_path}")
                return cities
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city_name = row.get('city', '').strip()
                    country_name = row.get('country', '').strip()
                    
                    # Extract countries while loading
                    if country_name:
                        countries.add(country_name.lower().strip())
                    
                    if city_name:
                        # Store by normalized name for case-insensitive lookup
                        norm_name = city_name.lower().strip()
                        
                        # Parse population for comparison
                        try:
                            pop = int(float(row.get('population', 0) or 0))
                        except (ValueError, TypeError):
                            pop = 0
                        
                        # If we haven't seen this city, or this entry has higher population, keep it
                        if norm_name not in cities:
                            cities[norm_name] = {
                                'city': city_name,
                                'city_ascii': row.get('city_ascii', ''),
                                'country': row.get('country', ''),
                                'lat': row.get('lat', ''),
                                'lng': row.get('lng', ''),
                                'admin_name': row.get('admin_name', ''),
                                'capital': row.get('capital', ''),
                                'population': row.get('population', ''),
                                'iso2': row.get('iso2', ''),
                                'iso3': row.get('iso3', ''),
                            }
                        else:
                            # Compare with existing entry
                            try:
                                existing_pop = int(float(cities[norm_name].get('population', 0) or 0))
                            except (ValueError, TypeError):
                                existing_pop = 0
                            
                            # Keep the one with higher population
                            if pop > existing_pop:
                                cities[norm_name] = {
                                    'city': city_name,
                                    'city_ascii': row.get('city_ascii', ''),
                                    'country': row.get('country', ''),
                                    'lat': row.get('lat', ''),
                                    'lng': row.get('lng', ''),
                                    'admin_name': row.get('admin_name', ''),
                                    'capital': row.get('capital', ''),
                                    'population': row.get('population', ''),
                                    'iso2': row.get('iso2', ''),
                                    'iso3': row.get('iso3', ''),
                                }
            print(f"[CityDetector] Loaded {len(cities)} global cities")
            print(f"[CityDetector] Extracted {len(countries)} unique countries")
            
            # Store countries for later use
            self._extracted_countries = countries
        except Exception as e:
            print(f"[Error] Failed to load global cities: {e}")
        
        return cities
    
    def _extract_countries_from_cities(self) -> set:
        """
        Extract unique countries from the loaded cities data.
        
        Returns:
            Set of normalized country names
        """
        countries = set()
        for city_data in self.global_cities.values():
            country = city_data.get('country', '').strip()
            if country:
                # Normalize country name for matching
                norm_country = country.lower().strip()
                countries.add(norm_country)
        
        print(f"[CityDetector] Extracted {len(countries)} unique countries from cities data")
        return countries
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        text = text.lower().strip()
        # Remove common punctuation but keep spaces
        text = re.sub(r"[^\w\s]", '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def detect_moroccan_city(self, user_input: str) -> Optional[str]:
        """
        Detect if user mentioned a Moroccan city.
        
        Returns:
            Normalized city name if found, None otherwise
        """
        query = self._normalize_text(user_input)
        
        # Check exact matches with misspellings first
        for misspelling, canonical in self.moroccan_city_misspellings.items():
            if re.search(r'\b' + re.escape(misspelling) + r'\b', query):
                return canonical
        
        # Check exact match with normalized Moroccan cities (word boundaries)
        for city in self.moroccan_cities:
            if re.search(r'\b' + re.escape(city) + r'\b', query):
                return city
        
        # Fuzzy match: Try to match words in the query against Moroccan cities
        words = query.split()
        for word in words:
            if len(word) >= 4:  # Minimum 4 chars to avoid false positives like "fes" from "festival"
                matches = get_close_matches(word, self.moroccan_cities, n=1, cutoff=0.75)
                if matches:
                    return matches[0]
        
        return None
    
    def detect_global_city(self, user_input: str) -> Optional[Dict]:
        """
        Detect if user mentioned a non-Moroccan city.
        Uses EXACT matching only to avoid false positives from fuzzy matching.
        Prioritizes larger/more well-known cities (population >= 50,000).
        
        Returns:
            City data dict if found, None otherwise
        """
        query = self._normalize_text(user_input)
        original_words = user_input.split()
        
        candidates = []
        
        # Check all words for EXACT city matches (case-insensitive)
        # No fuzzy matching to avoid matching "main" to "Mainz" etc.
        for word in original_words:
            word_clean = self._normalize_text(word)
            
            # Require minimum word length and match in global cities
            if len(word_clean) >= 4:  # Minimum 4 chars
                # Exact match (case-insensitive)
                if word_clean in self.global_cities:
                    city_data = self.global_cities[word_clean]
                    population = self._get_population(city_data)
                    # Require larger cities (minimum 50,000 people) to reduce false positives
                    if population >= 50000:
                        candidates.append((city_data, population))
        
        # If we found candidates, return the one with highest population
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def _get_population(self, city_data: Dict) -> int:
        """Extract and return population as integer, default to 0 if not available."""
        try:
            pop = float(city_data.get('population', 0))
            return int(pop)
        except (ValueError, TypeError):
            return 0
    
    def detect_city(self, user_input: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Detect city in user input.
        
        Priority:
        1. Check if it's a Moroccan city
        2. Check if it's a global city (but not Moroccan)
        
        Returns:
            Tuple of (moroccan_city_name, global_city_data)
            One or both can be None
        """
        moroccan = self.detect_moroccan_city(user_input)
        if moroccan:
            return (moroccan, None)
        
        global_city = self.detect_global_city(user_input)
        if global_city:
            return (None, global_city)
        
        return (None, None)
    
    def is_morocco_mentioned(self, user_input: str) -> bool:
        """Check if 'Morocco' is mentioned in the query."""
        return bool(re.search(r'\bmorocco\b', user_input.lower()))
    
    def detect_country(self, user_input: str) -> Optional[str]:
        """
        Detect if user mentioned a country name.
        Prioritizes non-Morocco countries if multiple countries are mentioned.
        Returns the country name if found, None otherwise.
        """
        query = self._normalize_text(user_input)
        
        detected_countries = []
        
        # Check for exact country matches (word boundaries)
        for country in self.countries:
            # Handle multi-word countries like "united states", "south africa"
            if ' ' in country:
                if re.search(r'\b' + re.escape(country) + r'\b', query):
                    detected_countries.append(country)
            else:
                # Single-word countries
                if re.search(r'\b' + re.escape(country) + r'\b', query):
                    detected_countries.append(country)
        
        if not detected_countries:
            return None
        
        # If we found multiple countries, prioritize non-Morocco ones
        non_morocco = [c for c in detected_countries if c.lower() != "morocco"]
        if non_morocco:
            return non_morocco[0]  # Return first non-Morocco country
        
        # If only Morocco was found, return it
        return detected_countries[0] if detected_countries else None
