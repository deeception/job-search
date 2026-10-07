import os
import json
import glob
from datetime import datetime
import pandas as pd
import streamlit as st

# Import your scraper modules
import amazon
import visa
import jpmorgan
import mastercard
import microsoft
import goldmansachs
# import paypal # Uncomment when PayPal roles open up

TRACKER_FILE = "seen_jobs_tracker.json"
DATA_DIR = "."

st.set_page_config(page_title="SWE Job Scraper Dashboard", layout="wide")

# ----------------- Helper Functions -----------------
def load_tracker():
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_tracker(seen_ids):
    with open(TRACKER_FILE, "w") as f:
        json.dump(list(seen_ids), f, indent=2)

def reset_tracker():
    if os.path.exists(TRACKER_FILE):
        os.remove(TRACKER_FILE)
    st.session_state["seen_ids"] = set()

def get_latest_csv():
    csv_files = glob.glob(os.path.join(DATA_DIR, "job_matches_*.csv"))
    if not csv_files:
        return None
    return max(csv_files, key=os.path.getctime)

def run_scrapers():
    seen_ids = load_tracker()
    new_jobs = []
    
    scrapers = [
        ("Amazon", amazon.scrape),
        ("Visa", visa.scrape),
        ("JPMorgan", jpmorgan.scrape),
        ("Mastercard", mastercard.scrape),
        ("Microsoft", microsoft.scrape),
        ("Goldman Sachs", goldmansachs.scrape),
    ]

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, (name, scrape_fn) in enumerate(scrapers):
        status_text.text(f"Scraping {name}...")
        try:
            results = scrape_fn(seen_ids)
            if results:
                new_jobs.extend(results)
                for job in results:
                    seen_ids.add(str(job["ID"]))
        except Exception as e:
            st.warning(f"Error scraping {name}: {e}")
        progress_bar.progress((idx + 1) / len(scrapers))

    save_tracker(seen_ids)
    st.session_state["seen_ids"] = seen_ids
    progress_bar.empty()
    status_text.empty()

    if new_jobs:
        df_new = pd.DataFrame(new_jobs)
        # Drop raw scraper internal IDs from table view
        display_cols = [c for c in ["Company", "Title", "Location", "Tier", "Level", "Link"] if c in df_new.columns]
        df_new = df_new[display_cols]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_matches_{timestamp}.csv"
        df_new.to_csv(filename, index=False)
        return df_new, filename
    return None, None

# ----------------- UI Layout -----------------
st.title("🎯 Tech & FinTech Job Lead Terminal")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Controls")
    
    if st.button("🚀 Run Live Scrape", type="primary", use_container_width=True):
        with st.spinner("Scraping corporate endpoints..."):
            new_df, saved_file = run_scrapers()
            if new_df is not None:
                st.success(f"Found {len(new_df)} new jobs! Saved to `{saved_file}`")
                st.session_state["current_df"] = new_df
            else:
                st.info("No new jobs found matching your filters.")

    if st.button("🔄 Reset Tracker (Wipe Seen IDs)", use_container_width=True):
        reset_tracker()
        st.success("Seen job IDs wiped. Next scrape will pull all active matching roles.")

    st.divider()
    st.subheader("📊 Tracker Status")
    current_seen = load_tracker()
    st.metric("Total Seen Jobs in Memory", len(current_seen))

# Load data into session if not already loaded
if "current_df" not in st.session_state:
    latest_file = get_latest_csv()
    if latest_file and os.path.exists(latest_file):
        st.session_state["current_df"] = pd.read_csv(latest_file)
    else:
        st.session_state["current_df"] = pd.DataFrame()

df = st.session_state["current_df"]

if not df.empty:
    # Top-level Filtering Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        companies = ["All"] + sorted(list(df["Company"].dropna().unique()))
        selected_company = st.selectbox("Company", companies)
        
    with col2:
        tiers = ["All"] + sorted(list(df["Tier"].dropna().unique()))
        selected_tier = st.selectbox("Location Tier", tiers)
        
    with col3:
        levels = ["All"] + sorted(list(df["Level"].dropna().unique()))
        selected_level = st.selectbox("Seniority Level", levels)

    with col4:
        search_kw = st.text_input("Title Keyword Search", "")

    # Apply filters
    filtered_df = df.copy()
    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["Company"] == selected_company]
    if selected_tier != "All":
        filtered_df = filtered_df[filtered_df["Tier"] == selected_tier]
    if selected_level != "All":
        filtered_df = filtered_df[filtered_df["Level"] == selected_level]
    if search_kw:
        filtered_df = filtered_df[filtered_df["Title"].str.contains(search_kw, case=False, na=False)]

    st.markdown(f"**Showing {len(filtered_df)} matches**")
    
    # Display table with clickable URLs
    st.dataframe(
        filtered_df,
        column_config={
            "Link": st.column_config.LinkColumn("Application Link", display_text="Open Job ↗")
        },
        use_container_width=True,
        hide_index=True
    )

    # Download Button
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Current View as CSV",
        data=csv_bytes,
        file_name="filtered_job_matches.csv",
        mime="text/csv",
    )
else:
    st.info("No job records loaded yet. Click **Run Live Scrape** in the sidebar to populate listings.")