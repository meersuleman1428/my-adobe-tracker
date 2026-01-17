import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Configuration ---
st.set_page_config(page_title="Adobe Pro Insights", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# Sidebar
search_query = st.sidebar.text_input("Enter Topic", "nature")

# --- 2. DAILY GLOBAL TRENDS LIST (Table) ---
st.subheader("🔥 Adobe Stock: Daily Global Trends List")

@st.cache_data(ttl=3600)
def get_daily_trends():
    backup_trends = [
        {"Trend Rank": 1, "Topic": "AI Abstract Backgrounds", "Status": "🔥 Hot"},
        {"Trend Rank": 2, "Topic": "Sustainability", "Status": "📈 Growing"},
        {"Trend Rank": 3, "Topic": "3D Characters", "Status": "🔥 Hot"},
        {"Trend Rank": 4, "Topic": "Mental Health Awareness", "Status": "📈 Growing"},
        {"Trend Rank": 5, "Topic": "Cyberpunk Art", "Status": "🔥 Hot"}
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

st.table(get_daily_trends())

# --- 3. TOP DOWNLOADS SCRAPER (Table) ---
st.markdown("---")
st.subheader(f"💰 Top Downloads for '{search_query}'")

def get_live_selling(kw):
    types = {"Photos": "images", "Videos": "video", "Vectors": "vectors"}
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
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

# --- 4. MARKET CHARTS (Google Trends) ---
st.markdown("---")
try:
    pytrends = TrendReq(hl='en-US', tz=360)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Top Buying Countries")
        pytrends.build_payload([search_query], timeframe='now 7-d')
        geo_data = pytrends.interest_by_region(resolution='COUNTRY').sort_values(by=search_query, ascending=False).head(10)
        st.bar_chart(geo_data)

    with col2:
        st.subheader("📊 Category Demand Share")
        kw_list = [f"{search_query} video", f"{search_query} vector", f"{search_query} photo"]
        pytrends.build_payload(kw_list, timeframe='now 7-d')
        demand_share = pytrends.interest_over_time().mean().drop('isPartial').reset_index()
        demand_share.columns = ['Type', 'Popularity']
        fig_pie = px.pie(demand_share, values='Popularity', names='Type', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
except:
    st.info("Market data load ho raha hai... aglay refresh ka intezar karein.")
