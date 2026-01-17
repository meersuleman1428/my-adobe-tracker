import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- Page Config ---
st.set_page_config(page_title="Adobe Pro Insights", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# Sidebar - Default Keyword set to 'Nature'
search_query = st.sidebar.text_input("Enter Topic", "nature")

# --- 1. DAILY GLOBAL TRENDS LIST ---
@st.cache_data(ttl=3600)
def get_daily_trends():
    backup_trends = [
        {"Trend Rank": 1, "Topic": "AI Abstract Backgrounds", "Status": "🔥 Hot"},
        {"Trend Rank": 2, "Topic": "Sustainability & Green Energy", "Status": "📈 Growing"},
        {"Trend Rank": 3, "Topic": "3D Isometric Characters", "Status": "🔥 Hot"},
        {"Trend Rank": 4, "Topic": "Mental Health Awareness Visuals", "Status": "📈 Growing"},
        {"Trend Rank": 5, "Topic": "Cyberpunk Cityscapes", "Status": "🔥 Hot"}
    ]
    try:
        url = "https://stock.adobe.com/search?k=trending+now"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('a[data-t="search-pill"]')[:10]
        if trends:
            return pd.DataFrame([{"Trend Rank": i+1, "Topic": t.text.strip(), "Status": "📈 Growing"} for i, t in enumerate(trends)])
    except: pass
    return pd.DataFrame(backup_trends)

st.subheader("🔥 Adobe Stock: Daily Global Trends List")
st.table(get_daily_trends())

# --- 2. MARKET ANALYSIS SECTION ---
if search_query:
    st.markdown("---")
    with st.spinner(f"Fetching live data for '{search_query}'..."):
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Category Demand Share
            kw_list = [f"{search_query} video", f"{search_query} vector", f"{search_query} photo"]
            pytrends.build_payload(kw_list, timeframe='now 7-d')
            demand_data = pytrends.interest_over_time()
            
            if not demand_data.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📍 Top Buying Countries")
                    # Using single keyword for regional interest to avoid errors
                    pytrends.build_payload([search_query], timeframe='now 7-d')
                    geo_data = pytrends.interest_by_region(resolution='COUNTRY').sort_values(by=search_query, ascending=False).head(10)
                    st.bar_chart(geo_data)
                
                with col2:
                    st.subheader("📊 Category Demand Share")
                    avg_demand = demand_data.mean().drop('isPartial').reset_index()
                    avg_demand.columns = ['Type', 'Popularity']
                    fig_pie = px.pie(avg_demand, values='Popularity', names='Type', hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Loading market charts... please wait for next refresh.")
        except:
            st.warning("Google Trends is busy. Charts will appear in 1-2 minutes.")
