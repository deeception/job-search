import os
import json
import utils
import amazon
import jpmorgan
import visa
import mastercard
import goldmansachs

def run_diagnostics():
    print("========================================")
    print("🕵️ REQUISITION ENGINE DIAGNOSTICS")
    print("========================================\n")

    # --- TEST 1: Check Configuration ---
    print("--- TEST 1: LOAD CONFIGURATION ---")
    config = utils.load_config()
    print(f"Inclusions loaded: {len(config.get('inclusion_keywords', []))}")
    print(f"Exclusions loaded: {len(config.get('exclusion_keywords', []))}")
    print(f"Sample Inclusions: {config.get('inclusion_keywords', [])[:3]}")
    print(f"Sample Exclusions: {config.get('exclusion_keywords', [])[:3]}\n")

    # --- TEST 2: Check Regex Logic ---
    print("--- TEST 2: FILTER LOGIC CHECK ---")
    test_titles = [
        "Software Development Engineer II", # Should pass (Amazon)
        "Associate - Engineering",          # Should pass (Goldman)
        "Software Engineer III",            # Should fail (III)
        "Sr. Software Engineer"             # Should fail (Sr.)
    ]
    
    for title in test_titles:
        result = utils.is_valid_title(title, config)
        print(f"Title: '{title}' -> Allowed? {result}")
    print("\n")

    # --- TEST 3: Raw Scraper Endpoints ---
    print("--- TEST 3: SCRAPER API ENDPOINTS ---")
    scrapers = [
        ("Amazon", amazon.scrape),
        ("JPMorgan", jpmorgan.scrape),
        ("Visa", visa.scrape),
        ("Mastercard", mastercard.scrape),
        ("Goldman Sachs", goldmansachs.scrape),
    ]

    for name, scrape_fn in scrapers:
        print(f"Querying {name}...")
        try:
            # Pass an empty set so it doesn't block any jobs as "already seen"
            results = scrape_fn(set())
            
            if results is None:
                print(f"  ❌ FAILED: Scraper returned 'None'.")
            elif len(results) == 0:
                print(f"  ⚠️ WARNING: Scraper ran but returned 0 jobs. (Either network blocked or all filtered out)")
            else:
                print(f"  ✅ SUCCESS: Found {len(results)} valid jobs!")
                print(f"  -> Sample Job: {results[0]['Title']}")
                
        except Exception as e:
            print(f"  ❌ CRASH: Exception thrown -> {e}")
        print("-" * 40)

if __name__ == "__main__":
    run_diagnostics()