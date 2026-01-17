import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# 1. Page Config & Refresh (5 Mins to avoid blocks)
st.set_page_config(page_title="Adobe Pro Insights", layout="wide")
st_autorefresh(interval=300 * 1000, key="datarefresh")

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# Sidebar
search_query = st.sidebar.text_input("Enter Topic", "Cyberpunk")

# 2. DAILY TRENDS (Hamesha dikhne wali table)
st.subheader("🔥 Adobe Stock: Daily Global Trends List")
@st.cache_data(ttl=3600)
# --- Is line ko dhoond kar iske neechay ye paste karein ---
st.subheader(f"💰 Top Downloads for '{search_query}'")

def get_live_selling(kw):
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    # Teeno categories (Photo, Video, Vector) ko cover karega
    types = {"Photos": "images", "Videos": "video", "Vectors": "vectors"}
    for name, t in types.items():
        url = f"https://stock.adobe.com/search/{t}?k={kw.replace(' ', '+')}&order=relevance"
        try:
            r = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            # Naya logic: Ab ye direct links nikalay ga
            items = soup.select('a.js-search-result-link')[:2] 
            for item in items:
                asset_url = "https://stock.adobe.com" + item['href']
                img_tag = item.find('img')
                title = img_tag['alt'] if img_tag else "View Asset"
                data.append({"Category": name, "Title": title, "Link": asset_url})
        except: continue
    return pd.DataFrame(data)

# Table dikhane ka tareeqa jo links ko clickable banaye ga
df_links = get_live_selling(search_query)
if not df_links.empty:
    st.dataframe(
        df_links, 
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn("View on Adobe")}
    )

st.table(get_daily_trends())

# 3. TOP DOWNLOADS (Adobe Live Scraper)
st.markdown("---")
st.subheader(f"💰 Top Downloads for '{search_query}'")
def get_live_selling(kw):
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = f"https://stock.adobe.com/search?k={kw.replace(' ', '+')}&order=relevance"
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('img', alt=True)[:4]
        for item in items:
            data.append({"Popular Asset Title": item['alt']})
        return pd.DataFrame(data)
    except: return pd.DataFrame([{"Popular Asset Title": "Loading live titles..."}])

st.dataframe(get_live_selling(search_query), use_container_width=True)

# 4. MARKET CHARTS (Google Trends)
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
    st.warning("Google is resting. Charts will auto-load in 5 minutes.")

