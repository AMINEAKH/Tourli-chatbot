import sys
import os
import re
import unicodedata
import numpy as np
import requests
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher, get_close_matches
import nltk
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('omw-1.4')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.preprocessing.data_loader import load_all_data
from src.retrieval.city_detector import CityDetector
from src.retrieval.world_city_formatter import WorldCityResponseFormatter

lemmatizer = WordNetLemmatizer()

def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r"'s\b", '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def lemmatize_text(text):
    return " ".join([lemmatizer.lemmatize(word) for word in text.split()])


# OpenWeatherMap API key (provided by user)
load_dotenv()

API_KEY = os.getenv("TOURLI_API_KEY")

# City matching similarity threshold (80%)
CITY_MATCH_THRESHOLD = 0.80


def get_weather(city: str) -> dict | None:
    """
    Returns a dictionary with weather info:
    { temperature, humidity, condition, wind }
    or None if the city is not found or API fails.
    """
    if not city or not isinstance(city, str):
        return None
    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        resp = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params, timeout=8)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Basic validation
        if 'main' not in data or 'weather' not in data:
            return None

        temperature = data.get('main', {}).get('temp')
        humidity = data.get('main', {}).get('humidity')
        condition = ''
        weather_list = data.get('weather', [])
        if weather_list and isinstance(weather_list, list):
            condition = weather_list[0].get('description', '')
        wind = data.get('wind', {}).get('speed')

        return {
            'temperature': temperature,
            'humidity': humidity,
            'condition': condition,
            'wind': wind,
        }
    except Exception:
        return None

class Retriever:
    def __init__(self, debug=False):
        self.debug = debug
        print("[Retriever] Loading datasets...")
        all_data = load_all_data()
        self.qa_list = all_data.get('cleaned_dataset', []) + all_data.get('edge_cases_cleaned', [])
        print(f"[Retriever] Total Q&A entries loaded: {len(self.qa_list)}")
        if not self.qa_list:
            raise ValueError("No Q&A entries found.")
        
        # Initialize city detector with global cities dataset
        cities_csv_path = os.path.join(os.path.dirname(__file__), '../../data/processed/worldcities_clean.csv')
        self.city_detector = CityDetector(cities_csv_path)
        self.world_city_formatter = WorldCityResponseFormatter()

        # --- Intents ---
        self.intent_keywords = {
            "greeting": ["hello", "hi", "hey", "salam", "greetings", "yo", "good morning", "good evening"],
            "greeting_personal": ["how are you", "how's it going", "what's up", "how have you been"],
            "farewell": ["bye", "goodbye", "see you", "later", "take care"],
            "small_talk": ["how's life", "nice weather", "what's new", "how are things"],
            "joke_or_troll": ["joke", "funny", "make me laugh", "prank", "tagine swim"],
            "rude_or_aggressive": ["shut up", "stupid", "idiot", "annoying", "dumb"],
            "ask_beaches": ["beach", "swim", "sand", "ocean", "sea", "sunbathe", "coast", "shore", "swimming spot"],
            "ask_surfing": ["surf", "surfing", "waves", "board", "learn to surf"],
            "ask_waterfalls": ["waterfall", "cascade", "swimming spot", "hike to waterfall", "nature water"],
            "ask_food": ["food", "eat", "hungry", "meal", "snack", "what to eat", "fud", "find food", "eating", "cuisine"],
            "ask_restaurants": ["restaurant", "dining", "place to eat", "where to eat", "cafe", "seafood", "beach restaurants"],
            "ask_local_dishes": ["local dish", "bastilla", "Moroccan food", "specialty"],
            "ask_bars": ["bar", "pub", "alcohol", "drink", "cocktail", "wine", "beer"],
            "ask_clubs": ["club", "nightclub", "party", "dance", "DJ", "disco"],
            "ask_nightlife": ["nightlife", "party", "evening fun", "after dark", "night entertainment"],
            "ask_hotels": ["hotel", "stay", "accommodation", "lodging", "inn", "where to sleep"],
            "ask_riads": ["riad", "guesthouse", "traditional house", "Moroccan stay"],
            "ask_cheap_hotels": ["cheap hotel", "budget stay", "hostel", "low cost lodging"],
            "ask_landmarks": ["landmark", "monument", "must see", "historic site", "famous place", "old medinas", "medina", "places to visit"],
            "ask_attractions": ["attraction", "sight", "tourist spot"],
            "ask_museums": ["museum", "art gallery", "history museum", "exhibit", "cultural site"],
            "ask_nature": ["nature", "park", "garden", "natural site", "green area", "outdoors", "mountains", "explore"],
            "ask_parks": ["park", "botanical garden", "playground", "open space", "nature park"],
            "ask_hiking": ["hike", "trek", "trail", "mountain walk", "nature walk", "adventure hike"],
            "ask_things_to_do": ["activities", "fun things", "things to do", "what to do", "cool", "fun", "something to do", "what to see", "famous to see"],
            "ask_activities": ["activity", "experience", "adventure", "excursion", "recreational activity"],
            "ask_family_activities": ["kids", "child-friendly", "family fun", "children activity"],
            "ask_kid_friendly": ["kids", "child-friendly", "safe for children", "family-friendly"],
            "ask_transport": ["transport", "get around", "travel", "moving around", "how to go", "commute"],
            "ask_taxi": ["taxi", "cab", "ride", "grab a taxi", "hire transport"],
            "ask_public_transport": ["bus", "train", "metro", "tram", "public transport", "local transport"],
            "ask_airport": ["airport", "flight", "departure", "arrival", "plane"],
            "ask_weather": ["weather", "forecast", "rain", "sunny", "temperature", "climate", "how warm", "how cold", "weather conditions"],
            "ask_distance": ["distance", "how far", "how far is", "kilometers", "kilometres", "km", "miles", "how many km", "distance between", "how far from"],
            "ask_temperature": ["temperature", "hot", "cold", "degrees", "how warm", "how cold", "warm", "degrees"],
            "ask_safe_areas": ["safe", "security", "dangerous areas", "crime", "unsafe place"],
            "ask_scams": ["scam", "trick", "fraud", "cheat", "avoid scams"],
            "ask_safety": ["safety", "safe travel", "is it safe"],
            "ask_shopping": ["shopping", "buy", "mall", "store", "souvenir"],
            "ask_souks": ["souk", "bazaar", "traditional market", "artisan market", "handicraft"],
            "ask_markets": ["market", "best markets", "markets", "local market", "food market"],
            "ask_culture": ["culture", "tradition", "customs", "heritage", "local culture"],
            "ask_history": ["history", "heritage", "historical site", "old city", "past events"],
            "ask_festivals": ["festival", "celebration", "event", "cultural festival", "holiday"],
            "ask_best_time": ["best time", "season", "when to visit", "ideal time"],
            "ask_family": ["family", "travel with kids", "family-friendly", "with children"],
            "general_morocco": ["Morocco info", "country info", "overview", "general info", "Morocco guide", "about Morocco", "something about Morocco"],
            "irrelevant_question": ["random", "irrelevant", "off-topic", "not related"],
        }

        self.cities = [
            "Agadir", "Al Hoceima", "Azrou", "Beni Mellal", "Berkane",
            "Casablanca", "Chefchaouen", "Dakhla", "El Jadida", "Errachidia",
            "Essaouira", "Fes", "Guelmim", "Ifrane", "Kenitra",
            "Khouribga", "Laayoune", "Larache", "Marrakech", "Martil",
            "Meknes", "Mohammedia", "Nador", "Ouarzazate", "Oujda",
            "Rabat", "Safi", "Sale", "Tangier", "Tetouan",
            "Tiznit", "Taroudant", "Tata", "Tanger Med", "Sidi Ifni"
        ]
        self.cities_norm = [normalize_text(c) for c in self.cities]

        # Normalize dataset
        for entry in self.qa_list:
            entry['_norm_question'] = normalize_text(entry.get('question', ''))
            entry['_norm_city'] = normalize_text(entry.get('city', ''))
            entry['_norm_intent'] = entry.get('intent', '').lower()

        self.questions = [entry['_norm_question'] for entry in self.qa_list]

        # Vectorization
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=8000)
        self.q_vectors = self.vectorizer.fit_transform(self.questions)
        print("[Retriever] TF-IDF vectors ready.")

        self.generic_fallback = [
            "I’m not sure about that yet.",
            "Could you clarify your question?",
            "Sorry, I don’t know that yet."
        ]

    # Fuzzy similarity helper
    @staticmethod
    def _fuzzy_similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()

    # -----------------
    # City detection with typo handling
    # -----------------
    def _extract_city(self, user_input):
        query = normalize_text(user_input)
        
        # City abbreviation mappings
        city_abbreviations = {
            "casa": "casablanca",
            "cali": "casablanca",
            "mkech": "marrakech",
            "meknes": "meknes",
            "fes": "fes"
        }
        
        # Check abbreviations first
        for abbrev, full_city in city_abbreviations.items():
            if re.search(r'\b' + re.escape(abbrev) + r'\b', query):
                return normalize_text(full_city)
        
        # Exact match with optional 's
        for city_norm in self.cities_norm:
            if re.search(r'\b' + re.escape(city_norm) + r"(?:'s)?\b", query):
                return city_norm
        # Word-level fuzzy match (only for words with 4+ characters to avoid false matches)
        for word in query.split():
            if len(word) >= 4:  # Require minimum 4 chars for fuzzy city matching
                close = get_close_matches(word, self.cities_norm, n=1, cutoff=0.70)
                if close:
                    return close[0]
        # Full-query fuzzy match
        close = get_close_matches(query, self.cities_norm, n=1, cutoff=0.70)
        if close:
            return close[0]
        return None

    # -----------------
    # Intent detection with typo handling
    # -----------------
    def _detect_intent(self, user_input):
        query = normalize_text(user_input)
        query_lem = lemmatize_text(query)
        
        # Replace common abbreviations and slang
        query_expanded = query.replace(" 2 ", " to ").replace(" n ", " in ").replace(" cn ", " can ")
        query_expanded_lem = lemmatize_text(query_expanded)

        # Joke/troll priority
        for kw in self.intent_keywords.get("joke_or_troll", []):
            kw_norm = normalize_text(kw)
            kw_lem = lemmatize_text(kw_norm)
            if kw_norm in query or kw_lem in query_lem or self._fuzzy_similarity(query, kw_norm) > 0.8:
                return "joke_or_troll"

        # Normal intents - check both original and expanded query
        # Prioritize distance detection (should come before generic queries about cities)
        distance_keywords = self.intent_keywords.get("ask_distance", [])
        for kw in distance_keywords:
            kw_norm = normalize_text(kw)
            kw_lem = lemmatize_text(kw_norm)
            if re.search(r'\b' + re.escape(kw_norm) + r'\b', query) or \
               re.search(r'\b' + re.escape(kw_lem) + r'\b', query_lem) or \
               self._fuzzy_similarity(query, kw_norm) > 0.75:
                return "ask_distance"
        
        # Prioritize weather detection before bars
        weather_keywords = self.intent_keywords.get("ask_weather", [])
        for kw in weather_keywords:
            kw_norm = normalize_text(kw)
            kw_lem = lemmatize_text(kw_norm)
            if re.search(r'\b' + re.escape(kw_norm) + r'\b', query) or \
               re.search(r'\b' + re.escape(kw_lem) + r'\b', query_lem) or \
               self._fuzzy_similarity(query, kw_norm) > 0.75:
                return "ask_weather"
        
        for intent, keywords in self.intent_keywords.items():
            if intent in {"joke_or_troll", "ask_weather", "ask_distance"}:
                continue
            for kw in keywords:
                kw_norm = normalize_text(kw)
                kw_lem = lemmatize_text(kw_norm)
                # Check original query
                if re.search(r'\b' + re.escape(kw_norm) + r'\b', query) or \
                   re.search(r'\b' + re.escape(kw_lem) + r'\b', query_lem) or \
                   self._fuzzy_similarity(query, kw_norm) > 0.75:
                    return intent
                # Check expanded query (for abbreviations)
                if re.search(r'\b' + re.escape(kw_norm) + r'\b', query_expanded) or \
                   re.search(r'\b' + re.escape(kw_lem) + r'\b', query_expanded_lem) or \
                   self._fuzzy_similarity(query_expanded, kw_norm) > 0.75:
                    return intent
        return None

    # -----------------
    # Robust city extraction for distance queries
    # -----------------
    def _extract_cities_from_text(self, text, max_cities=2):
        """
        Scan the text for up to `max_cities` city name matches using n-gram scanning
        and `find_city_coordinates` for verification. Returns list of tuples
        (display_name, lat, lng, country).
        
        Priority: Moroccan cities first, then global cities with strict matching.
        """
        if not text or not isinstance(text, str):
            return []

        found = []
        
        # FIRST: Check for exact Moroccan city matches (high priority)
        for city in self.cities:
            city_norm = normalize_text(city)
            text_norm = normalize_text(text)
            # Look for word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(city_norm) + r'\b', text_norm):
                coords = self.find_city_coordinates(city)
                if coords and normalize_text(coords[0]) not in [normalize_text(f[0]) for f in found]:
                    found.append(coords)
                    if len(found) >= max_cities:
                        return found

        # SECOND: Check for Moroccan city abbreviations/misspellings
        for misspelling, canonical in self.city_detector.moroccan_city_misspellings.items():
            if len(found) >= max_cities:
                break
            text_norm = normalize_text(text)
            if re.search(r'\b' + re.escape(misspelling) + r'\b', text_norm):
                coords = self.find_city_coordinates(canonical)
                if coords and normalize_text(coords[0]) not in [normalize_text(f[0]) for f in found]:
                    found.append(coords)

        # If we have enough cities from Morocco, return
        if len(found) >= max_cities:
            return found[:max_cities]

        # THIRD: Try simple split heuristics FIRST (between X and Y / from X to Y)
        # This is more reliable than n-gram scanning for multi-city queries
        if len(found) < max_cities:
            text_lower = text.lower()
            m = re.search(r'between\s+(.+?)\s+and\s+(.+)', text_lower)
            if not m:
                m = re.search(r'from\s+(.+?)\s+to\s+(.+)', text_lower)
            if m:
                a = m.group(1).strip(' "\'')
                b = m.group(2).strip(' "\'')
                for cand in (a, b):
                    if len(found) >= max_cities:
                        break
                    c = self.find_city_coordinates(cand)
                    if c and normalize_text(c[0]) not in [normalize_text(f[0]) for f in found]:
                        found.append(c)

        # FOURTH: Use n-gram scanning for remaining cities (if still need more)
        if len(found) < max_cities:
            remove_punctuation = text.replace("'", " ").replace('"', " ")
            tokens = re.findall(r"[\w\-À-ÖØ-öø-ÿ]+", remove_punctuation, flags=re.UNICODE)
            
            # Common stopwords/non-city words to skip in single-token matches
            common_words = {
                'whats', 'what', 'hows', 'how', 'the', 'is', 'are', 'and', 'or', 'to', 'from',
                'between', 'distance', 'far', 'away', 'where', 'which', 'when', 'can', 'will',
                'does', 'did', 'do', 'about', 'for', 'as', 'with', 'at', 'in', 'on', 'by',
                'of', 'an', 'a', 'km', 'kilometers', 'miles', 'you', 'me', 'him', 'her'
            }

            # Try longer n-grams first (4 -> 1)
            max_n = min(4, len(tokens))
            used_spans = set()
            for n in range(max_n, 0, -1):
                if len(found) >= max_cities:
                    break
                for i in range(0, len(tokens) - n + 1):
                    if len(found) >= max_cities:
                        break
                    span = (i, i + n)
                    if span in used_spans:
                        continue
                    phrase = " ".join(tokens[i:i + n])
                    # Skip very short phrases
                    if len(phrase) < 2:
                        continue
                    # For single-token n-grams, skip common stopwords
                    if n == 1 and phrase.lower() in common_words:
                        continue
                    candidate = self.find_city_coordinates(phrase)
                    if candidate:
                        # Avoid duplicates (by normalized name)
                        norm = normalize_text(candidate[0])
                        if norm not in [normalize_text(f[0]) for f in found]:
                            found.append(candidate)
                            # mark tokens used to avoid overlapping matches
                            for j in range(i, i + n):
                                used_spans.add((j, j + 1))

        return found

    # -----------------
    # Distance helpers
    # -----------------
    def find_city_coordinates(self, city_name: str):
        """
        Return tuple (display_name, lat(float), lng(float), country, score) or None.
        
        Algorithm:
        1. Exact match (highest priority) -> score 1.0
        2. Check if query resembles Moroccan city -> boost Morocco entries by 0.15
        3. For short names (<=5 chars), use high threshold (>= 0.90) to avoid false fuzzy matches
        4. For longer names, use standard threshold (>= 0.80)
        5. Prioritize by (similarity_score, population)
        6. Try major cities (pop >= 50,000) before minor ones
        
        Returns:
            (name, lat, lng, country, score) or None
            score < 0.80 means low confidence match
        """
        if not city_name or not isinstance(city_name, str):
            return None

        # Normalize search string (case-insensitive, accent-insensitive)
        query = normalize_text(city_name)
        
        gc = self.city_detector.global_cities

        # STEP 1: Exact match in global cities (keys are normalized)
        if query in gc:
            data = gc[query]
            try:
                lat = float(data.get('lat') or 0.0)
                lng = float(data.get('lng') or 0.0)
            except (ValueError, TypeError):
                return None
            
            name = data.get('city') or data.get('city_ascii') or city_name
            country = data.get('country', '')
            return (name, lat, lng, country, 1.0)

        # STEP 2: Check if input looks like a Moroccan city
        is_moroccan_query = self.city_detector.detect_moroccan_city(city_name) is not None

        # STEP 3: Build and evaluate candidates
        candidates = []
        
        # Adjust threshold based on query length (short names need stricter matching)
        dynamic_threshold = 0.90 if len(query) <= 5 else CITY_MATCH_THRESHOLD
        
        for norm_key, v in gc.items():
            city_ascii_norm = normalize_text(v.get('city_ascii') or v.get('city') or '')
            
            try:
                pop = int(float(v.get('population') or 0))
            except Exception:
                pop = 0
            
            # Calculate similarity against both normalized key and city_ascii
            def similarity(a, b):
                if not a or not b:
                    return 0.0
                return SequenceMatcher(None, a, b).ratio()

            sim1 = similarity(query, norm_key)
            sim2 = similarity(query, city_ascii_norm)
            score = max(sim1, sim2)
            
            # STEP 4: Country-based boosting
            # If query looks Moroccan AND this is a Morocco entry, boost score
            country = (v.get('country') or '').strip()
            if is_moroccan_query and country.lower() == 'morocco':
                score = min(1.0, score + 0.15)
            
            # Only consider matches above threshold (use dynamic threshold for short names)
            if score >= dynamic_threshold:
                candidates.append((norm_key, v, score, pop))

        # STEP 5: Split into major and minor cities
        major = [c for c in candidates if c[3] >= 50000]
        minor = [c for c in candidates if c[3] < 50000]

        # STEP 6: Pick the best candidate (prioritize major cities)
        def pick_best(pool):
            if not pool:
                return None
            # Sort by (score DESC, population DESC)
            pool_sorted = sorted(pool, key=lambda x: (x[2], x[3]), reverse=True)
            return pool_sorted[0]

        chosen = pick_best(major)
        if not chosen:
            chosen = pick_best(minor)

        if not chosen:
            return None

        norm_key, v, top_score, pop = chosen
        
        try:
            lat = float(v.get('lat') or 0.0)
            lng = float(v.get('lng') or 0.0)
        except (ValueError, TypeError):
            return None

        name = v.get('city') or v.get('city_ascii') or city_name
        country = v.get('country', '')

        if self.debug:
            try:
                print(f"[CITY] '{city_name}' → {name}, {country}, {top_score:.2f}")
            except Exception:
                pass

        # Return name, lat, lng, country, score
        return (name, lat, lng, country, top_score)

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Compute Haversine distance (in kilometers) between two lat/lon points.
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371.0  # Earth radius in km
        rlat1, rlon1, rlat2, rlon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = rlat2 - rlat1
        dlon = rlon2 - rlon1
        a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def get_city_distance(self, city_a: str, city_b: str) -> str:
        """
        Core logic:
        - Find both cities
        - Detect Morocco vs. non-Morocco
        - Compute distance using haversine
        - Format final response string
        """
        if not city_a or not city_b or not isinstance(city_a, str) or not isinstance(city_b, str):
            return "Please provide two valid city names."

        found_a = self.find_city_coordinates(city_a)
        found_b = self.find_city_coordinates(city_b)

        if not found_a:
            return "I couldn't identify that city, can you rephrase or specify the country?"
        if not found_b:
            return "I couldn't identify that city, can you rephrase or specify the country?"

        # find_city_coordinates returns (name, lat, lng, country, score)
        try:
            name_a, lat_a, lng_a, country_a, score_a = found_a
        except Exception:
            # Backwards compatibility: fallback to old tuple
            name_a, lat_a, lng_a, country_a = found_a
            score_a = 1.0
        try:
            name_b, lat_b, lng_b, country_b, score_b = found_b
        except Exception:
            name_b, lat_b, lng_b, country_b = found_b
            score_b = 1.0

        # If either match is low confidence, ask for confirmation
        # Use clear phrasing and include country when available
        if score_a < CITY_MATCH_THRESHOLD:
            display_country = f"{country_a}" if country_a else ''
            display = f"{name_a} ({display_country})" if display_country else name_a
            return f"I'm not sure which city you mean. Did you mean {display}?"
        if score_b < CITY_MATCH_THRESHOLD:
            display_country = f"{country_b}" if country_b else ''
            display = f"{name_b} ({display_country})" if display_country else name_b
            return f"I'm not sure which city you mean. Did you mean {display}?"

        # Compute distance
        try:
            dist = self.haversine_distance(lat_a, lng_a, lat_b, lng_b)
        except Exception:
            return "Sorry, I couldn't compute the distance right now."

        dist_str = f"{dist:,.1f}"

        # Detect Morocco membership
        is_a_morocco = (country_a or '').strip().lower() == 'morocco' or normalize_text(name_a) in self.city_detector.moroccan_cities
        is_b_morocco = (country_b or '').strip().lower() == 'morocco' or normalize_text(name_b) in self.city_detector.moroccan_cities

        if not (is_a_morocco and is_b_morocco):
            prefix = "My main specialty is Morocco, but here is the information you requested: "
            reply = f"{prefix}The distance between {name_a} and {name_b} is {dist_str} km."
        else:
            reply = f"The distance between {name_a} and {name_b} is {dist_str} km."

        return reply

    # -----------------
    # Main retrieval
    # -----------------
    def get_answer(self, user_input, top_k=1):
        if not user_input.strip():
            return [("Please ask a question.", 0.0)]

        user_norm = normalize_text(user_input)
        user_lem = lemmatize_text(user_norm)

        # Use NEW city detection system
        moroccan_city, global_city = self.city_detector.detect_city(user_input)
        morocco_mentioned = self.city_detector.is_morocco_mentioned(user_input)
        country_detected = self.city_detector.detect_country(user_input)
        
        # Fall back to old detection for backward compatibility
        old_city_detect = self._extract_city(user_input)
        
        detected_intent = self._detect_intent(user_input)

        if self.debug:
            try:
                print(f"\n[DEBUG] Query: {user_input}")
                print(f"[DEBUG] Moroccan city detected: {moroccan_city}")
                # Handle potential Unicode issues with global city data
                global_city_str = f"{global_city.get('city', 'N/A')} ({global_city.get('country', 'N/A')})" if global_city else None
                print(f"[DEBUG] Global city detected: {global_city_str}")
                print(f"[DEBUG] 'Morocco' mentioned: {morocco_mentioned}")
                print(f"[DEBUG] Detected intent: {detected_intent}")
            except Exception as e:
                print(f"[DEBUG] (Some debug info skipped due to encoding: {e})")

        # --- Weather intent handling (high priority) ---
        if detected_intent == 'ask_weather':
            # If a Moroccan city was detected
            if moroccan_city:
                city_query = moroccan_city
                weather = get_weather(city_query)
                if not weather:
                    return [("I couldn’t find the weather for that city. Can you try another one?", 0.5)]
                city_display = city_query.title()
                cond = (weather.get('condition') or '').capitalize()
                temp = weather.get('temperature')
                hum = weather.get('humidity')
                wind = weather.get('wind')
                reply = (f"The weather in {city_display} right now:\n"
                         f"• {cond}\n"
                         f"• Temperature: {temp}°C\n"
                         f"• Humidity: {hum}%\n"
                         f"• Wind: {wind} m/s")
                return [(reply, 1.0)]

            # If a global (non-Moroccan) city was detected
            if global_city:
                city_query = global_city.get('city') or global_city.get('city_ascii') or ''
                weather = get_weather(city_query)
                if not weather:
                    return [("I couldn’t find the weather for that city. Can you try another one?", 0.5)]
                city_display = city_query.title()
                cond = (weather.get('condition') or '').capitalize()
                temp = weather.get('temperature')
                hum = weather.get('humidity')
                wind = weather.get('wind')
                prefix = "I don't specialize outside Morocco, but here's the weather:"
                reply = (f"{prefix}\nThe weather in {city_display} right now:\n"
                         f"• {cond}\n"
                         f"• Temperature: {temp}°C\n"
                         f"• Humidity: {hum}%\n"
                         f"• Wind: {wind} m/s")
                return [(reply, 1.0)]

            # No city detected
            return [("Sure! Which city do you want the weather for?", 0.5)]

        # --- Distance intent handling ---
        if detected_intent == 'ask_distance':
            # Use robust n-gram scanning to extract up to two city candidates
            text = user_input.strip()
            found = self._extract_cities_from_text(text, max_cities=2)

            if len(found) >= 2:
                a, b = found[0], found[1]
                reply = self.get_city_distance(a[0], b[0])
                return [(reply, 1.0)]

            # If only one was found, try heuristics to extract the other chunk and resolve it
            if len(found) == 1:
                only = found[0]
                # Remove the matched city name from text and attempt to find another
                remaining_text = re.sub(re.escape(only[0]), '', text, flags=re.I).strip()
                more = self._extract_cities_from_text(remaining_text, max_cities=1)
                if more:
                    reply = self.get_city_distance(only[0], more[0][0])
                    return [(reply, 1.0)]

            # Last resort: try splitting by common delimiters and resolve each part
            parts = [p.strip() for p in re.split(r'between|and|to|from|,|;|\bvs\b', text, flags=re.I) if p.strip()]
            candidates = []
            for part in parts:
                if len(candidates) >= 2:
                    break
                c = self.find_city_coordinates(part)
                if c:
                    candidates.append(c)

            if len(candidates) >= 2:
                reply = self.get_city_distance(candidates[0][0], candidates[1][0])
                return [(reply, 1.0)]

            # If still not enough info
            return [("I couldn't identify two cities in your request, can you rephrase or specify the countries?", 0.5)]

        
        # ===== DECISION TREE (Priority Order) =====
        
        # 1. If Moroccan city detected → Morocco city intents
        if moroccan_city:
            return self._answer_moroccan_city_query(user_input, moroccan_city, top_k)
        
        # 2. If non-Moroccan city detected → World-city facts response (prioritize over general Morocco)
        if global_city:
            world_response = self.world_city_formatter.format_world_city_response(global_city)
            return [(world_response, 1.0)]
        
        # 3. If a NON-MOROCCO country is mentioned → Not in specialty
        if country_detected and country_detected.lower() != "morocco":
            # User is asking about another country, not Morocco
            country_display = country_detected.title() if country_detected.lower() not in ["usa", "uk"] else country_detected.upper()
            message = f"I'm specialized in Morocco tourism, so {country_display} is outside my expertise. But if you're interested in visiting Morocco instead, I'd be happy to help!"
            return [(message, 0.3)]
        
        # 4. Else if "morocco" in query → General Morocco intent responses
        if morocco_mentioned:
            return self._answer_general_morocco_query(user_input, top_k)
        
        # 5. Else → Use original retrieval logic with generic fallback
        return self._answer_generic_query(user_input, detected_intent, top_k)
    
    def _answer_moroccan_city_query(self, user_input, city_name, top_k=1):
        """Handle queries about Moroccan cities."""
        user_norm = normalize_text(user_input)
        detected_intent = self._detect_intent(user_input)
        
        # Exact match
        for entry in self.qa_list:
            if user_norm == entry['_norm_question']:
                return [(entry['assistant'], 1.0)]

        # Immediate responses for greetings/trolls
        if detected_intent in {"greeting", "farewell", "joke_or_troll", "greeting_personal"}:
            candidates = [e for e in self.qa_list if e['_norm_intent'] == detected_intent]
            if candidates:
                return [(np.random.choice(candidates)['assistant'], 1.0)]

        # Candidate selection
        candidate_idxs = [
            i for i in range(len(self.qa_list))
            if self.qa_list[i]['_norm_intent'] not in {"greeting", "farewell", "irrelevant_question", "rude_or_aggressive"}
        ]

        # Filter by city
        city_matches = [i for i in candidate_idxs if self.qa_list[i]['_norm_city'] == city_name]
        if city_matches:
            candidate_idxs = city_matches

        # Filter by intent
        if detected_intent:
            intent_matches = [i for i in candidate_idxs if self.qa_list[i]['_norm_intent'] == detected_intent]
            if intent_matches:
                candidate_idxs = intent_matches

        if not candidate_idxs:
            return [(np.random.choice(self.generic_fallback), 0.0)]

        # TF-IDF + fuzzy scoring
        candidate_vecs = self.q_vectors[candidate_idxs]
        tfidf_sims = cosine_similarity(self.vectorizer.transform([normalize_text(user_input)]), candidate_vecs).flatten()

        scored_candidates = []
        for idx, tfidf_score in zip(candidate_idxs, tfidf_sims):
            fuzzy_score = self._fuzzy_similarity(user_norm, self.qa_list[idx]['_norm_question'])
            final_score = (0.6 * tfidf_score) + (0.4 * fuzzy_score)
            if final_score > 0.15:
                scored_candidates.append((self.qa_list[idx]['assistant'], final_score))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        if not scored_candidates:
            return [(np.random.choice(self.generic_fallback), 0.0)]
        return scored_candidates[:top_k]
    
    def _answer_general_morocco_query(self, user_input, top_k=1):
        """Handle general Morocco queries (no specific city).
        
        When "Morocco" is mentioned, use TF-IDF + fuzzy matching on general_morocco entries
        to find the BEST answer, not random.
        """
        user_norm = normalize_text(user_input)
        user_lem = lemmatize_text(user_norm)
        
        # First, check for exact match
        for entry in self.qa_list:
            if user_norm == entry['_norm_question']:
                return [(entry['assistant'], 1.0)]

        # Get the detected intent
        detected_intent = self._detect_intent(user_input)

        # Immediate responses for greetings/trolls (higher priority)
        if detected_intent in {"greeting", "farewell", "joke_or_troll", "greeting_personal"}:
            candidates = [e for e in self.qa_list if e['_norm_intent'] == detected_intent]
            if candidates:
                return [(np.random.choice(candidates)['assistant'], 1.0)]

        # For Morocco queries: Get ALL general_morocco intent entries
        general_morocco_entries = [e for e in self.qa_list if e['_norm_intent'] == 'general_morocco']
        
        if not general_morocco_entries:
            return [(np.random.choice(self.generic_fallback), 0.0)]

        # Convert to indices for vectorization
        candidate_idxs = [self.qa_list.index(e) for e in general_morocco_entries]

        # Apply TF-IDF + fuzzy matching to find BEST answer
        candidate_vecs = self.q_vectors[candidate_idxs]
        tfidf_sims = cosine_similarity(self.vectorizer.transform([user_norm]), candidate_vecs).flatten()

        scored_candidates = []
        for idx, tfidf_score in zip(candidate_idxs, tfidf_sims):
            fuzzy_score = self._fuzzy_similarity(user_norm, self.qa_list[idx]['_norm_question'])
            # Weight TF-IDF more for general Morocco queries
            final_score = (0.85 * tfidf_score) + (0.15 * fuzzy_score)
            
            # Keyword boosting: Extract key content words (not common stop words)
            query_words = set(user_norm.lower().split())
            stop_words = {'what', 'are', 'the', 'a', 'an', 'is', 'in', 'of', 'to', 'for', 'and', 'or', 'with', 'on', 'at', 'by', 'from', 'main'}
            key_words = [w for w in query_words if w not in stop_words and len(w) > 2]
            
            # Boost score if key words match, with stronger boost for longer/more specific words
            candidate_question = self.qa_list[idx]['_norm_question'].lower()
            if key_words:
                # Give 15% boost per matching keyword, with extra 10% for longer words (>6 chars)
                boost = 0.0
                for w in key_words:
                    if w in candidate_question:
                        if len(w) > 6:
                            boost += 0.25  # More specific words get bigger boost
                        else:
                            boost += 0.15
                # Cap the boost at 80% (allows multiple keywords to compound)
                boost = min(0.80, boost)
                if boost > 0:
                    final_score = final_score * (1 + boost)
            
            if final_score > 0.1:  # Lower threshold for general Morocco
                scored_candidates.append((self.qa_list[idx]['assistant'], final_score))

        # If no candidates met threshold, return best match anyway
        if not scored_candidates:
            best_idx = candidate_idxs[tfidf_sims.argmax()]
            return [(self.qa_list[best_idx]['assistant'], tfidf_sims.max())]

        # Sort by score and return best answer
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:top_k]
    
    def _answer_generic_query(self, user_input, detected_intent, top_k=1):
        """Handle generic queries without city or Morocco mention."""
        user_norm = normalize_text(user_input)

        # Exact match
        for entry in self.qa_list:
            if user_norm == entry['_norm_question']:
                return [(entry['assistant'], 1.0)]

        # Immediate responses for greetings/trolls
        if detected_intent in {"greeting", "farewell", "joke_or_troll", "greeting_personal"}:
            candidates = [e for e in self.qa_list if e['_norm_intent'] == detected_intent]
            if candidates:
                return [(np.random.choice(candidates)['assistant'], 1.0)]

        # Candidate selection
        candidate_idxs = [
            i for i in range(len(self.qa_list))
            if self.qa_list[i]['_norm_intent'] not in {"greeting", "farewell", "irrelevant_question", "rude_or_aggressive"}
        ]

        # Filter by intent
        if detected_intent:
            intent_matches = [i for i in candidate_idxs if self.qa_list[i]['_norm_intent'] == detected_intent]
            if intent_matches:
                candidate_idxs = intent_matches

        if not candidate_idxs:
            return [(np.random.choice(self.generic_fallback), 0.0)]

        # TF-IDF + fuzzy scoring
        candidate_vecs = self.q_vectors[candidate_idxs]
        tfidf_sims = cosine_similarity(self.vectorizer.transform([user_norm]), candidate_vecs).flatten()

        scored_candidates = []
        for idx, tfidf_score in zip(candidate_idxs, tfidf_sims):
            fuzzy_score = self._fuzzy_similarity(user_norm, self.qa_list[idx]['_norm_question'])
            final_score = (0.6 * tfidf_score) + (0.4 * fuzzy_score)
            if final_score > 0.15:
                scored_candidates.append((self.qa_list[idx]['assistant'], final_score))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        if not scored_candidates:
            return [(np.random.choice(self.generic_fallback), 0.0)]
        return scored_candidates[:1]

if __name__ == "__main__":
    retriever = Retriever(debug=True)
    test_questions = [
        
        "I'm traveling to Morocco next week with my family. We'll land in Casablanca then go to Marrakech. What should we do first?",
        "My cousin told me Rabat has amazing seafood, can I find beach restaurants there?",
    ]

    
    print("-" * 50)
    for q in test_questions:
        ans = retriever.get_answer(q)
        print(f"Q: {q}")
        print(f"A: {ans[0][0]} (Score: {ans[0][1]:.2f})\n")