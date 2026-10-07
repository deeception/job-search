import os
import json
from datetime import datetime, date
import pandas as pd
import streamlit as st

import utils
import amazon
import visa
import jpmorgan
import mastercard
import goldmansachs

TRACKER_FILE = "seen_jobs_tracker.json"
LEDGER_FILE = "job_history_ledger.csv"

# Updated for mobile optimization
st.set_page_config(
    page_title="Requisition Intelligence",
    page_icon="💼",
    layout="centered", # Better for mobile than "wide"
    initial_sidebar_state="collapsed" # Starts collapsed on mobile
)

# ----------------- Persistence Layer -----------------
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

def wipe_tracker():
    if os.path.exists(TRACKER_FILE):
        os.remove(TRACKER_FILE)

def load_ledger():
    if os.path.exists(LEDGER_FILE):
        try:
            df = pd.read_csv(LEDGER_FILE)
            df["Discovered_Date"] = pd.to_datetime(df["Discovered_Date"]).dt.date
            # Ensure new columns exist for backwards compatibility
            if "Posted_Date" not in df.columns:
                df["Posted_Date"] = "Unknown"
            else:
                df["Posted_Date"] = df["Posted_Date"].fillna("Unknown")
            
            if "Description" not in df.columns:
                df["Description"] = "Description not available"
            else:
                df["Description"] = df["Description"].fillna("Description not available")
                
            return df
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def append_to_ledger(new_jobs_list):
    if not new_jobs_list:
        return
    now_dt = datetime.now()
    cur_date = now_dt.date()
    cur_timestamp = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    for job in new_jobs_list:
        job["Discovered_Date"] = cur_date
        job["Discovered_Timestamp"] = cur_timestamp
        if "Posted_Date" not in job: job["Posted_Date"] = "Unknown"
        if "Description" not in job: job["Description"] = "Description not available"

    new_df = pd.DataFrame(new_jobs_list)
    
    if os.path.exists(LEDGER_FILE):
        existing_df = pd.read_csv(LEDGER_FILE)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset=["Company", "ID"], keep="last", inplace=True)
        combined_df.to_csv(LEDGER_FILE, index=False)
    else:
        new_df.to_csv(LEDGER_FILE, index=False)

# ----------------- Execution Orchestration -----------------
def execute_pipeline():
    seen_ids = load_tracker()
    fresh_jobs = []
    
    scrapers = [
        ("Amazon", amazon.scrape),
        ("Visa", visa.scrape),
        ("JPMorgan Chase", jpmorgan.scrape),
        ("Mastercard", mastercard.scrape),
        ("Goldman Sachs", goldmansachs.scrape),
    ]

    progress_bar = st.progress(0)
    status_box = st.empty()

    for idx, (name, scrape_fn) in enumerate(scrapers):
        status_box.text(f"Querying endpoint: {name}...")
        try:
            results = scrape_fn(seen_ids)
            if results:
                fresh_jobs.extend(results)
                for item in results:
                    seen_ids.add(str(item["ID"]))
        except Exception as e:
            st.error(f"Error communicating with {name}: {e}")
        progress_bar.progress((idx + 1) / len(scrapers))

    save_tracker(seen_ids)
    append_to_ledger(fresh_jobs)
    progress_bar.empty()
    status_box.empty()
    return len(fresh_jobs)

# ----------------- Sidebar Controls -----------------
with st.sidebar:
    st.markdown("### Engine Operations")
    
    if st.button("Run Global Extraction", type="primary", use_container_width=True):
        with st.spinner("Extracting active requisitions across portals..."):
            count = execute_pipeline()
            if count > 0:
                st.success(f"Execution complete: {count} new requisitions indexed.")
            else:
                st.info("Execution complete: No new requisitions match filter rules.")
            st.rerun()

    if st.button("Reset Deduplication Tracker", use_container_width=True):
        wipe_tracker()
        st.warning("Deduplication index cleared. Next run will re-ingest all postings.")

    st.markdown("---")
    st.markdown("### System Telemetry")
    
    ledger_data = load_ledger()
    tracked_count = len(load_tracker())
    
    st.metric(label="Total Seen Requisition IDs", value=tracked_count)
    st.metric(label="Total Requisitions in Ledger", value=len(ledger_data))
    
    today_count = 0
    if not ledger_data.empty:
        today_count = len(ledger_data[ledger_data["Discovered_Date"] == date.today()])
    st.metric(label="Requisitions Ingested Today", value=today_count)

# ----------------- Main Interface -----------------
st.title("Requisition Intelligence Terminal")
st.caption("Automated tracking, filtering, and analysis of enterprise engineering roles.")

tab_active, tab_analytics, tab_history, tab_config = st.tabs([
    "Active Opportunities",
    "Data Grouping & Analytics",
    "Historical Ingestion Log",
    "Rule Configuration"
])

# ----------------- Tab 1: Active Opportunities -----------------
with tab_active:
    if ledger_data.empty:
        st.info("The requisition ledger is empty. Run an extraction using the sidebar to populate records.")
    else:
        st.markdown("#### Requisition Catalog")
        
        # Mobile optimized filtering (uses expander to save space)
        with st.expander("🔍 Filters & Sorting", expanded=False):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                comp_list = ["All Companies"] + sorted(list(ledger_data["Company"].dropna().unique()))
                sel_comp = st.selectbox("Company", comp_list)
                
                level_list = ["All Levels"] + sorted(list(ledger_data["Level"].astype(str).unique()))
                sel_level = st.selectbox("Career Level", level_list)
            
            with f_col2:
                tier_list = ["All Tiers"] + sorted(list(ledger_data["Tier"].dropna().unique()))
                sel_tier = st.selectbox("Location Tier", tier_list)
                search_query = st.text_input("Title / Keyword Search", "")

            date_scope = st.radio(
                "Temporal Filter",
                options=["All Dates", "Discovered Today", "Discovered Yesterday", "Custom Date Selection"],
                horizontal=True
            )
            
            sort_pref = st.selectbox(
                "Sort Table By",
                ["Discovered Timestamp (Newest)", "Level (Highest First)", "Company (A-Z)"]
            )

            if date_scope == "Custom Date Selection":
                unique_dates = sorted(list(ledger_data["Discovered_Date"].unique()), reverse=True)
                chosen_date = st.selectbox("Select Record Date", unique_dates)

        filtered = ledger_data.copy()
        
        if sel_comp != "All Companies": filtered = filtered[filtered["Company"] == sel_comp]
        if sel_tier != "All Tiers": filtered = filtered[filtered["Tier"] == sel_tier]
        if sel_level != "All Levels": filtered = filtered[filtered["Level"].astype(str) == sel_level]
        if search_query: filtered = filtered[filtered["Title"].str.contains(search_query, case=False, na=False)]

        today_val = date.today()
        if date_scope == "Discovered Today":
            filtered = filtered[filtered["Discovered_Date"] == today_val]
        elif date_scope == "Discovered Yesterday":
            yesterday_val = today_val - pd.Timedelta(days=1)
            filtered = filtered[filtered["Discovered_Date"] == yesterday_val]
        elif date_scope == "Custom Date Selection":
            filtered = filtered[filtered["Discovered_Date"] == chosen_date]

        # Apply Sorting
        if sort_pref == "Discovered Timestamp (Newest)":
            filtered = filtered.sort_values(by="Discovered_Timestamp", ascending=False)
        elif sort_pref == "Level (Highest First)":
            filtered = filtered.sort_values(by=["Level", "Discovered_Timestamp"], ascending=[False, False])
        elif sort_pref == "Company (A-Z)":
            filtered = filtered.sort_values(by=["Company", "Discovered_Timestamp"], ascending=[True, False])

        st.markdown(f"**Displaying {len(filtered)} requisitions**")
        
        # --- Share to Gemini Payload Generator ---
        if not filtered.empty:
            with st.expander("🤖 Share to Gemini", expanded=False):
                st.caption("Copy this text block and paste it into the Gemini app for review.")
                share_text = "Here are the latest job matches from my scraper:\n\n"
                for _, row in filtered.head(20).iterrows(): 
                    share_text += f"• **{row['Title']}** at {row['Company']}\n  Location: {row['Location']} | Tier: {row.get('Tier', 'N/A')} | Level: {row['Level']}\n  Date: {row.get('Posted_Date', 'Unknown')}\n  Link: {row['Link']}\n\n"
                
                if len(filtered) > 20:
                    share_text += f"...and {len(filtered) - 20} more jobs."
                st.code(share_text, language="markdown")
        
        # Condensed mobile-friendly table display
        display_columns = ["Company", "Title", "Location", "Level", "Posted_Date", "Link"]
        available_cols = [c for c in display_columns if c in filtered.columns]
        
        st.dataframe(
            filtered[available_cols],
            column_config={
                "Link": st.column_config.LinkColumn("Application Portal", display_text="Open Listing"),
                "Posted_Date": st.column_config.TextColumn("ATS Posted Date")
            },
            use_container_width=True,
            hide_index=True
        )

        # Export Controls
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Export Filtered Set to CSV",
            data=csv_data,
            file_name=f"requisition_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

# ----------------- Tab 2: Grouping & Analytics -----------------
with tab_analytics:
    if ledger_data.empty:
        st.info("No data available for analytics. Run an extraction first.")
    else:
        st.markdown("#### Aggregate Analytics")
        
        group_dim = st.selectbox(
            "Primary Grouping Dimension", 
            ["Company", "Location Tier", "Level", "Discovered_Date", "Posted_Date"]
        )
        
        mapped_col = {
            "Company": "Company",
            "Location Tier": "Tier",
            "Level": "Level",
            "Discovered_Date": "Discovered_Date",
            "Posted_Date": "Posted_Date"
        }[group_dim]
        
        summary_table = (
            ledger_data.groupby(mapped_col)
            .agg(
                Total_Requisitions=("ID", "count"),
                Unique_Titles=("Title", "nunique")
            )
            .reset_index()
            .sort_values(by="Total_Requisitions", ascending=False)
        )
        
        # Removed columns here to allow vertical stacking on mobile
        st.markdown(f"##### Distribution across {group_dim}")
        chart_df = summary_table.set_index(mapped_col)["Total_Requisitions"]
        st.bar_chart(chart_df)
        
        st.markdown(f"##### Breakdown by {group_dim}")
        st.dataframe(summary_table, use_container_width=True, hide_index=True)

# ----------------- Tab 3: Historical Ingestion Log -----------------
with tab_history:
    if ledger_data.empty:
        st.info("No historical records discovered.")
    else:
        st.markdown("#### Chronological Ledger History")
        
        daily_summary = (
            ledger_data.groupby("Discovered_Date")
            .agg(
                Total_Jobs_Indexed=("ID", "count"),
                Companies_Covered=("Company", "nunique")
            )
            .reset_index()
            .sort_values(by="Discovered_Date", ascending=False)
        )
        
        st.dataframe(daily_summary, use_container_width=True, hide_index=True)
        
        st.markdown("#### Detailed Run Logs")
        date_inspect = st.selectbox(
            "Inspect Log for Date", 
            daily_summary["Discovered_Date"].tolist()
        )
        
        day_slice = ledger_data[ledger_data["Discovered_Date"] == date_inspect]
        
        cols_to_show = ["Discovered_Timestamp", "Company", "Title", "Location", "Posted_Date", "Link"]
        avail_log_cols = [c for c in cols_to_show if c in day_slice.columns]
        
        st.dataframe(
            day_slice[avail_log_cols],
            column_config={
                "Link": st.column_config.LinkColumn("Listing", display_text="Open Listing")
            },
            use_container_width=True,
            hide_index=True
        )

# ----------------- Tab 4: Rule Configuration -----------------
with tab_config:
    st.markdown("#### Dynamic Engine Configuration")
    st.caption("Modifications saved here persist to `config.json` and are immediately consumed by `utils.py`.")
    
    current_config = utils.load_config()
    
    with st.form("rules_editor_form"):
        st.markdown("##### Title Whitelist Patterns (Inclusion)")
        inclusions_str = st.text_area(
            "Requisition must match at least one keyword (comma-separated)",
            value=", ".join(current_config.get("inclusion_keywords", []))
        )
        
        st.markdown("##### Title Blacklist Patterns (Exclusion)")
        exclusions_str = st.text_area(
            "Requisition containing any of these keywords will be rejected (comma-separated)",
            value=", ".join(current_config.get("exclusion_keywords", []))
        )
        
        # Replaced columns with standard stacking for mobile readability
        st.markdown("##### Location Rules")
        t1_str = st.text_area("Tier 1 Locations", value=", ".join(current_config.get("tier_1_locations", [])))
        t2_str = st.text_area("Tier 2 Locations", value=", ".join(current_config.get("tier_2_locations", [])))
        t3_str = st.text_area("Tier 3 Locations", value=", ".join(current_config.get("tier_3_locations", [])))
            
        submitted = st.form_submit_button("Save and Apply Configuration", type="primary")
        
        if submitted:
            updated_payload = {
                "inclusion_keywords": [k.strip().lower() for k in inclusions_str.split(",") if k.strip()],
                "exclusion_keywords": [k.strip().lower() for k in exclusions_str.split(",") if k.strip()],
                "tier_1_locations": [k.strip().lower() for k in t1_str.split(",") if k.strip()],
                "tier_2_locations": [k.strip().lower() for k in t2_str.split(",") if k.strip()],
                "tier_3_locations": [k.strip().lower() for k in t3_str.split(",") if k.strip()],
            }
            utils.save_config(updated_payload)
            st.success("Configuration saved. Filter rules updated across all scrapers.")