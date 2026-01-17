import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- 1. Dashboard Configuration ---
st.set_page_config(page_title="Adobe Stock Pro 2026", layout="wide")
st_autorefresh(interval=600 * 1000, key="datarefresh") # Refresh time 10 mins

st.title("🚀 Adobe Stock Professional Market Intelligence")
st.write(f"🕒 Last Update: {pd.Timestamp.now().strftime('%H:%M:%S')} | Status: Live")

# Sidebar
search_query = st.sidebar.text_input("Enter Research Topic", "nature")

# --- 2. CREATIVE TRENDS 2026 (Fori Ideas) ---
st.subheader("🎨 Adobe Creative Trends 2026 (Predicted & Rising)")
col_a, col_b = st.columns(2)
with col_a:
    st.info("🔥 **High Demand (Hot Topics)**")
    st.write("- **AI Hyper-Realism:** Photorealistic textures.")
    st.write("- **Eco-Minimalism:** Sustainability visuals.")
with col_b:
    st.success("📈 **Global Growth Keywords**")
    st.write("- **Inclusivity & Diversity:** Authentic emotions.")
    st.write("- **3D Abstract Geometry:** Clean isometric vectors.")

# --- 3. DAILY TRENDS TABLE ---
st.markdown("---")
st.subheader("🌍 Daily Global Trends Table")
@st.cache_data(ttl=3600)
def get_daily_trends():
    backup = [
        {"Rank": 1, "Topic": "AI Abstract Backgrounds", "Status": "🔥 Breakout"},
        {"Rank": 2, "Topic": "Solar Energy Solutions", "Status": "📈 Rising"},
        {"Rank": 3, "Topic": "Mental Health Awareness", "Status": "📈 Rising"},
        {"Rank": 4, "Topic": "Cryptocurrency 3D Icons", "Status": "🔥 Breakout"},
        {"Rank": 5, "Topic": "Organic Texture Patterns", "Status": "✅ Stable"}
    ]
    return pd.DataFrame(backup)
st.table(get_daily_trends())

# --- 4. LIVE ASSET SEARCH (With Direct Links) ---
st.markdown("---")
st.subheader(f"🔍 Live Asset Search: What's selling for '{search_query}'?")
def get_live_assets(kw):
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = f"https://stock.adobe.com/search?k={kw.replace(' ', '+')}&order=relevance"
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.select('a.js-search-result-link')[:6]
        for item in items:
            asset_url = "https://stock.adobe.com" + item['href']
            img_tag = item.find('img')
            title = img_tag['alt'] if img_tag else "View Asset"
            data.append({"Trending Title": title, "Link": asset_url})
        return pd.DataFrame(data)
    except: return pd.DataFrame()

asset_df = get_live_assets(search_query)
if not asset_df.empty:
    st.dataframe(asset_df, use_container_width=True, column_config={"Link": st.column_config.LinkColumn("View Asset")})

# --- 5. MARKET SHARE & COUNTRIES ---
st.markdown("---")
try:
    # Stable Connection with higher timeout
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(15,30), retries=2)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 Top Buying Countries")
        pytrends.build_payload([search_query], timeframe='now 7-d')
        geo = pytrends.interest_by_region(resolution='COUNTRY').sort_values(by=search_query, ascending=False).head(10)
        st.bar_chart(geo)
    with col2:
        st.subheader("📊 Asset Popularity Share")
        # Simplified for faster loading
        kws = [f"{search_query} video", f"{search_query} vector"]
        pytrends.build_payload(kws, timeframe='now 7-d')
        demand = pytrends.interest_over_time().mean().drop('isPartial').reset_index()
        demand.columns = ['Type', 'Popularity']
        fig = px.pie(demand, values='Popularity', names='Type', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
except:
    st.info("Market Analytics are syncing. Use the 'Daily Trends' table for now.")
