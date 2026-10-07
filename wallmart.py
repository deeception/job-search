import requests
import utils

def scrape(seen_ids):
    url = "https://careers.walmart.com/api/graphql"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://careers.walmart.com"
    }
    
    # We will query just 'software engineer' and 'data engineer' to cast a wide net,
    # and let our utils.py filters aggressively weed out the false positives.
    target_queries = ["software engineer", "data engineer", "machine learning"]
    jobs = []
    
    for query in target_queries:
        # Walmart's specific GraphQL query payload for job search
        payload = {
            "queryId": "b0467c1f-f578-4261-9280-0ea4614f251c",
            "variables": {
                "chatRequest": {
                    "messages": [{"role": "user", "content": [{"type": "text", "text": query}]}],
                    "channel": "job_search",
                    "context": {
                        "job_search_context": {
                            "locale": "en_US",
                            "sort": "relevance",
                            "active_tab": "jobs",
                            "content_page": 0,
                            "future_roles_page": 0,
                            "job_page": 0,
                            # We can pass country directly to the payload to filter for India
                            "countries": ["India"]
                        }
                    }
                }
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # The jobs are deeply nested in the GraphQL response
            messages = data.get("data", {}).get("chat", {}).get("messages", [])
            job_list = []
            
            for msg in messages:
                content = msg.get("content", [])
                for item in content:
                    if item.get("type") == "job_search_results":
                        job_list = item.get("jobs", [])
                        break
            
            for job in job_list:
                job_id = job.get("job_id", "")
                title = job.get("title", "")
                
                if not job_id or not title or job_id in seen_ids:
                    continue
                    
                title_lower = title.lower()
                if not utils.is_valid_title(title_lower):
                    continue
                    
                level = utils.parse_level(title_lower)
                if level == 0:
                    continue
                
                # Extract location formatting
                loc_data = job.get("location", {})
                city = loc_data.get("city", "")
                state = loc_data.get("state", "")
                country = loc_data.get("country", "India")
                full_loc = f"{city}, {state}, {country}".strip(", ")
                
                jobs.append({
                    "Company": "Walmart",
                    "ID": job_id,
                    "Title": title,
                    "Location": full_loc,
                    "Tier": utils.get_location_tier(full_loc),
                    "Level": level,
                    # Walmart URL construction
                    "Link": f"https://careers.walmart.com/us/en/job/{job_id}"
                })
        except Exception as e:
            print(f"[Walmart] Error on '{query}': {e}")
            
    return jobs