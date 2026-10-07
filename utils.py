import os
import json
import re

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "inclusion_keywords": [
        "software engineer", "software development engineer", "sde", 
        "data engineer", "machine learning", "ml engineer", 
        "ai engineer", "applied ai", "backend", "systems engineer", 
        "platform engineer", "applied scientist"
    ],
    "exclusion_keywords": [
        "senior", "sr.", "sr ", "staff", "principal", "director", 
        "manager", "lead", "architect", "intern", "internship", 
        "qa", "quality assurance", "test engineer", "sdet", 
        "support", "sales", "recruiter", "product manager",
        "iii", " 3 ", " 3", "iii," # Added Level 3 / Senior numerical blocks
    ],
    "tier_1_locations": [
        "bengaluru", "bangalore", "hyderabad", "pune", "mumbai", 
        "chennai", "gurgaon", "noida", "india"
    ],
    "tier_2_locations": [
        "london", "dublin", "singapore", "tokyo", "berlin", 
        "amsterdam", "united kingdom", "ireland"
    ],
    "tier_3_locations": [
        "united states", "us", "san francisco", "sunnyvale", 
        "cupertino", "seattle", "austin", "new york", "palo alto"
    ]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)

def is_valid_title(title_lower):
    config = load_config()
    
    inclusions = config.get("inclusion_keywords", DEFAULT_CONFIG["inclusion_keywords"])
    if not any(kw.lower() in title_lower for kw in inclusions):
        return False
        
    exclusions = config.get("exclusion_keywords", DEFAULT_CONFIG["exclusion_keywords"])
    if any(kw.lower() in title_lower for kw in exclusions):
        return False
        
    return True

def parse_level(title_lower):
    # Use regex word boundaries (\b) so " i " doesn't match inside " ii " or " iii "
    # SDE 1 / Early Career
    sde1_pattern = r"\b(sde 1|sde i|sde-1|sde-i|engineer 1|engineer i|analyst)\b"
    if re.search(sde1_pattern, title_lower):
        return 1.0
        
    # SDE 2 / Mid Career
    sde2_pattern = r"\b(sde 2|sde ii|sde-2|sde-ii|engineer 2|engineer ii|engineer - ii|associate)\b"
    if re.search(sde2_pattern, title_lower):
        return 2.0
        
    # Unspecified / General IC
    return 1.5

def get_location_tier(location_str):
    loc_lower = str(location_str).lower()
    config = load_config()
    
    tier_1 = config.get("tier_1_locations", DEFAULT_CONFIG["tier_1_locations"])
    tier_2 = config.get("tier_2_locations", DEFAULT_CONFIG["tier_2_locations"])
    tier_3 = config.get("tier_3_locations", DEFAULT_CONFIG["tier_3_locations"])
    
    if any(city in loc_lower for city in tier_1):
        return "Tier 1"
    if any(city in loc_lower for city in tier_2):
        return "Tier 2"
    if any(city in loc_lower for city in tier_3):
        return "Tier 3"
    return "Tier 4"