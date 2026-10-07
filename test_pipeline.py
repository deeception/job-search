import pandas as pd
import microsoft, paypal, walmart

def run_targeted_test():
    print("🚀 Testing Remaining Companies (Microsoft, PayPal, Walmart)...\n" + "="*50)
    
    modules = [
        ("Microsoft", microsoft),
        ("PayPal", paypal),
        ("Walmart", walmart)
    ]
    
    all_jobs = []
    
    for company_name, module in modules:
        print(f"Testing {company_name}...")
        try:
            jobs = module.scrape([])
            print(f"  ✓ Found {len(jobs)} valid engineering roles.")
            if jobs:
                sample = jobs[0]
                print(f"  ✓ Date Extracted: {sample['Posted_Date']}")
                print(f"  ✓ Desc Snippet:   {sample['Description'][:85]}...\n")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  ❌ FAILED: {e}\n")
    
    print("="*50)
    print(f"🎉 Test Complete! Extracted {len(all_jobs)} total jobs.")
    
    if all_jobs:
        df = pd.DataFrame(all_jobs)
        cols = ["Company", "ID", "Title", "Level", "Tier", "Location", "Posted_Date", "Link", "Description"]
        df = df[[c for c in cols if c in df.columns]]
        
        filename = "remaining_companies_test.xlsx"
        try:
            df.to_excel(filename, index=False)
            print(f"📁 Saved output to: {filename}")
        except ModuleNotFoundError:
            csv_filename = "remaining_companies_test.csv"
            df.to_csv(csv_filename, index=False)
            print(f"⚠️ 'openpyxl' not installed. Saved as CSV instead: {csv_filename}")

if __name__ == "__main__":
    run_targeted_test()