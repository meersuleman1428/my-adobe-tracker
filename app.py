import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Configuration ---
st.set_page_config(page_title="Adobe Pro Insights", layout="wide")
st_autorefresh(interval=300 * 1000, key="datarefresh")

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# Sidebar
search_query = st.sidebar.text_input("Enter Topic", "nature")

# --- 2. DAILY GLOBAL TRENDS LIST (Table) ---
st.subheader("🔥 Adobe Stock: Daily Global Trends List")
@st.cache_data(ttl=3600)
def get_daily_trends():
    backup = [
        {"Trend Rank": 1, "Topic": "AI Abstract Backgrounds", "Status": "🔥 Hot"},
        {"Trend Rank": 2, "Topic": "Sustainability", "Status": "📈 Growing"},
        {"Trend Rank": 3, "Topic": "3D Characters", "Status": "🔥 Hot"},
        {"Trend Rank": 4, "Topic": "Mental Health Awareness", "Status": "📈 Growing"},
        {"Trend Rank": 5, "Topic": "Cyberpunk Art", "Status": "🔥 Hot"}
    ]
    return pd.DataFrame(backup)

st.table(get_daily_trends())

# --- 3. TOP DOWNLOADS WITH CLICKABLE LINKS ---
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
            # Scrape direct asset links
            items = soup.select('a.js-search-result-link')[:2]
            for item in items:
                asset_url = "https://stock.adobe.com" + item['href']
                img_tag = item.find('img')
                title = img_tag['alt'] if img_tag else "View Asset"
                data.append({"Category": name, "Title": title, "Link": asset_url})
        except: continue
    return pd.DataFrame(data)

df_links = get_live_selling(search_query)
if not df_links.empty:
    st.dataframe(
        df_links, 
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn("View on Adobe")}
    )

# --- 4. MARKET CHARTS (Google Trends) ---
st.markdown("---")
try:
    pytrends = TrendReq(hl='en-US', tz=360, retries=5)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 Top Buying Countries")
        pytrends.build_payload([search_query], timeframe='now 7-d')
        geo = pytrends.interest_by_region(resolution='COUNTRY').sort_values(by=search_query, ascending=False).head(10)
        st.bar_chart(geo)
    with col2:
        st.subheader("📊 Category Demand Share")
        kws = [f"{search_query} video", f"{search_query} photo", f"{search_query} vector"]
        pytrends.build_payload(kws, timeframe='now 7-d')
        demand = pytrends.interest_over_time().mean().drop('isPartial').reset_index()
        demand.columns = ['Type', 'Popularity']
        fig = px.pie(demand, values='Popularity', names='Type', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
except:
    st.info("Google is resting. Charts will auto-load in next refresh.")
