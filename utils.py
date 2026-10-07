import re

# 1. EXPANDED REJECT LIST: Kills false positives
REJECT_KEYWORDS = [
    # Seniority & Non-Tech
    "java", "senior", "sr", "sr.", "lead", "principal", "director", "manager", 
    "iv", "v", "hr", "strategy", "sales", "consulting", "marketing", 
    "staff", "head", "architect",
    # Job Types to Avoid
    "data scientist", "data science", "ftc", "contract", "intern", "student", 
    # Unrelated Domains (Operations, Hardware, Testing)
    "support", "test automation", "qa", "sdet", "quality assurance",
    "site reliability", "sre", "embedded", "firmware", "hardware", 
    "cyber", "security", "robotics", "frontend", "ui", "ux"
]

# 2. ENHANCED TARGET LIST: Aggressively target Agentic AI / RAG stacks based on JDs
TECH_KEYWORDS = [
    "software engineer", "sde", "software development engineer", "developer", 
    "data engineer", "ai engineer", "machine learning", "python", "backend", 
    "applied ai", "llm", "genai", "artificial intelligence",
    "rag", "langchain", "agentic", "mlops"
]

def get_location_tier(location_str):
    """
    Tier 1: India (Highest Priority)
    Tier 2: UK, Europe, Canada, Australia, Singapore (Easier Visa)
    Tier 3: US (Tough H-1B Lottery)
    Tier 4: Rest of World
    """
    loc = location_str.lower()
    if any(x in loc for x in ["india", "ind", "bangalore", "bengaluru", "pune", "hyderabad", "chennai", "mysuru", "gurgaon", "mumbai", "noida"]):
        return 1
    if any(x in loc for x in ["uk", "united kingdom", "london", "gb", "canada", "australia", "singapore", "germany", "ireland"]):
        return 2
    if any(x in loc for x in ["us", "united states", "usa", "california", "wa", "tx", "ny", "mo", "virginia", "colorado"]):
        return 3
    return 4

def parse_level(title_lower):
    # 1. Reject Seniors and Executive Titles
    if any(x in title_lower for x in ["lead", "senior", "sr", "principal", "manager", "director", "vp", "staff", "head", "architect"]):
        return 0 
        
    # 2. Reject Level 3 / III (Out of reach for 1.5 YoE; auto-rejects)
    if re.search(r'\b(iii|3)\b', title_lower) or "sde3" in title_lower or "sde 3" in title_lower:
        return 0
        
    # 3. Match Level 2 / II (Stretch Roles: 2-4 YoE)
    if re.search(r'\b(ii|2)\b', title_lower) or "sde2" in title_lower or "sde 2" in title_lower:
        return 2
        
    # 4. Match Level 1 / I (Sweet Spot Roles: 0-2 YoE)
    if re.search(r'\b(i|1)\b', title_lower) or "sde1" in title_lower or "sde 1" in title_lower or "associate" in title_lower or "fresher" in title_lower:
        return 1
        
    # 5. Generic / Unspecified (Likely entry-to-mid, safe to review)
    return 1.5

def is_valid_title(title_lower):
    if not any(t in title_lower for t in TECH_KEYWORDS): 
        return False
    if any(r in title_lower for r in REJECT_KEYWORDS): 
        return False
    return True