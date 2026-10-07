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
    return {
        "inclusion_keywords": ["software", "sde", "developer", "data", "machine learning", "ai", "engineer", "backend", "frontend", "fullstack"],
        "exclusion_keywords": ["senior", "principal", "manager", "lead", "iii", "3", "vp", "vice president", "sr"],
        "tier_1_locations": ["bengaluru", "hyderabad", "pune"],
        "tier_2_locations": ["london", "singapore"],
        "tier_3_locations": ["united states", "seattle"]
    }

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)

def is_valid_title(title, config=None):
    # FALLBACK: If a scraper doesn't pass a config, load it automatically
    if config is None:
        config = load_config()
        
    title_lower = title.lower()
    
    # 1. Check exclusions first
    for excl in config.get("exclusion_keywords", []):
        excl_clean = excl.strip().lower()
        if not excl_clean: continue
        
        if excl_clean.isalnum():
            pattern = r'\b' + re.escape(excl_clean) + r'\b'
            if re.search(pattern, title_lower):
                return False
        else:
            if excl_clean in title_lower:
                return False
            
    # 2. Check inclusions
    inclusions = config.get("inclusion_keywords", [])
    if not inclusions: 
        return True
        
    for incl in inclusions:
        incl_clean = incl.strip().lower()
        if not incl_clean: continue
        if incl_clean in title_lower:
            return True
            
    return False

def parse_level(title):
    title_lower = title.lower()
    if re.search(r'\b(iii|3|senior|sr|lead|principal|manager)\b', title_lower):
        return 3.0
    if re.search(r'\b(ii|2|mid)\b', title_lower):
        return 2.0
    if re.search(r'\b(i|1|junior|jr|associate|analyst|entry)\b', title_lower):
        return 1.0
    return 1.5

def get_location_tier(location):
    loc_lower = str(location).lower()
    config = load_config()
    
    for t1 in config.get("tier_1_locations", []):
        if t1 in loc_lower: return "Tier 1"
    for t2 in config.get("tier_2_locations", []):
        if t2 in loc_lower: return "Tier 2"
    for t3 in config.get("tier_3_locations", []):
        if t3 in loc_lower: return "Tier 3"
    return "Tier 4"