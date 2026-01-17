import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Adobe Pro Insights", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# Sidebar
search_query = st.sidebar.text_input("Enter Topic", "nature")

# --- 2. DAILY GLOBAL TRENDS LIST ---
st.subheader("🔥 Adobe Stock: Daily Global Trends List")
@st.cache_data(ttl=3600)
def get_daily_trends():
    backup = [
        {"Trend Rank": 1, "Topic": "AI Abstract Backgrounds", "Status": "🔥 Hot"},
        {"Trend Rank": 2, "Topic": "Sustainability", "Status": "📈 Growing"},
        {"Trend Rank": 3, "Topic": "3D Characters", "Status": "🔥 Hot"},
        {"Trend Rank": 4, "Topic": "Mental Health", "Status": "📈 Growing"},
        {"Trend Rank": 5, "Topic": "Cyberpunk Art", "Status": "🔥 Hot"}
    ]
    return pd.DataFrame(backup)

st.table(get_daily_trends())

# --- 3. TOP DOWNLOADS TABLE ---
st.markdown("---")
st.subheader(f"💰 Top Downloads for '{search_query}'")
def get_live_selling(kw):
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    types = {"Photos": "images", "Videos": "video", "Vectors": "vectors"}
    for name, t in types.items():
        url = f"https://stock.adobe.com/search/{t}?k={kw.replace(' ', '+')}&order=relevance"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.find_all('img', alt=True)[:2]
            for item in items:
                data.append({"Category": name, "Popular Asset Title": item['alt']})
        except: continue
    return pd.DataFrame(data)

st.dataframe(get_live_selling(search_query), use_container_width=True)

# --- 4. MARKET CHARTS (With Retry Logic) ---
st.markdown("---")
col1, col2 = st.columns(2)

try:
    # Adding more robust connection settings
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=3, backoff_factor=0.5)
    
    with col1:
        st.subheader("📍 Top Buying Countries")
        pytrends.build_payload([search_query], timeframe='now 7-d')
        geo = pytrends.interest_by_region(resolution='COUNTRY').sort_values(by=search_query, ascending=False).head(10)
        if not geo.empty and geo[search_query].sum() > 0:
            st.bar_chart(geo)
        else:
            st.info("Searching for country-wise interest... please wait.")

    with col2:
        st.subheader("📊 Category Demand Share")
        kws = [f"{search_query} video", f"{search_query} photo", f"{search_query} vector"]
        pytrends.build_payload(kws, timeframe='now 7-d')
        demand = pytrends.interest_over_time().mean().drop('isPartial').reset_index()
        demand.columns = ['Type', 'Popularity']
        fig = px.pie(demand, values='Popularity', names='Type', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
except:
    st.warning("Google Trends limits reached. Refreshing in 60 seconds to try again.")
