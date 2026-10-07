import os
import json
import re

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback defaults if config.json is missing
    return {
        "inclusion_keywords": ["software engineer", "sde", "data engineer", "machine learning", "ai engineer"],
        "exclusion_keywords": ["senior", "principal", "manager", "lead", "iii", "3", "vp", "vice president", "sr"],
        "tier_1_locations": ["bengaluru", "hyderabad", "pune"],
        "tier_2_locations": ["london", "singapore"],
        "tier_3_locations": ["united states", "seattle"]
    }

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)

def is_valid_title(title, config):
    """
    Strictly filters titles. Exclusions MUST be checked before inclusions.
    Uses regex word boundaries to prevent accidental substring matches.
    """
    title_lower = title.lower()
    
    # 1. CRITICAL: Check exclusions first. 
    # If a blacklist word is found, reject the job immediately.
    for excl in config.get("exclusion_keywords", []):
        # \b ensures we match the exact word (e.g., "iii" matches "Engineer III", but not "Hawaii")
        pattern = r'\b' + re.escape(excl) + r'\b'
        if re.search(pattern, title_lower):
            return False
            
    # 2. Check inclusions only after exclusions have passed
    for incl in config.get("inclusion_keywords", []):
        if incl in title_lower:
            return True
            
    # If no inclusion keywords match, reject
    return False

def extract_level(title):
    """
    Intelligently assigns a numeric level to a job title, 
    accounting for Roman numerals and text variations.
    """
    title_lower = title.lower()
    
    # Check Level 3 / Senior equivalents
    if re.search(r'\b(iii|3|senior|sr|lead|principal|manager)\b', title_lower):
        return 3.0
    
    # Check Level 2 / Mid equivalents
    if re.search(r'\b(ii|2|mid)\b', title_lower):
        return 2.0
        
    # Check Level 1 / Junior equivalents
    if re.search(r'\b(i|1|junior|jr|associate|analyst|entry)\b', title_lower):
        return 1.0
        
    # Fallback for unspecified levels
    return 1.5

def extract_tier(location, config):
    loc_lower = str(location).lower()
    
    for t1 in config.get("tier_1_locations", []):
        if t1 in loc_lower: return "Tier 1"
        
    for t2 in config.get("tier_2_locations", []):
        if t2 in loc_lower: return "Tier 2"
        
    for t3 in config.get("tier_3_locations", []):
        if t3 in loc_lower: return "Tier 3"
        
    return "Tier 4"