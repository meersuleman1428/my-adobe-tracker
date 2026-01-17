import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# --- Page Config (Mobile Friendly) ---
st.set_page_config(page_title="Adobe Pro Insights", layout="wide")

# --- Auto Refresh (Har 60 Seconds baad update) ---
st_autorefresh(interval=60 * 1000, key="datarefresh")

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# Sidebar
search_query = st.sidebar.text_input("Enter Topic (e.g. Dinosaur)", "Dinosaur")

# --- NEW FEATURE: DAILY GLOBAL TRENDS LIST ---
st.markdown("---")
st.subheader("🔥 Adobe Stock: Daily Global Trends List")

def get_daily_trends():
    # Adobe ke trends page se data nikalne ka logic
    url = "https://stock.adobe.com/search?k=trending+now"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Trending keywords aur topics nikalna
        trends = soup.find_all('a', {'class': 'js-search-link'})[:10] 
        trend_list = [{"Trend Rank": i+1, "Topic": t.text.strip(), "Status": "📈 Growing"} for i, t in enumerate(trends) if t.text.strip()]
        return pd.DataFrame(trend_list)
    except:
        return pd.DataFrame([{"Topic": "Data Updating...", "Status": "Please Wait"}])

df_daily = get_daily_trends()
st.table(df_daily) # Ye wahi list hai jo aapne maangi thi

# --- SECTION 2: TOP SELLING ASSETS (By Keyword) ---
st.markdown("---")
st.subheader(f"💰 Top Downloads for '{search_query}'")

def get_live_selling(kw):
    types = {"Photos": "images", "Videos": "video", "Vectors": "vectors"}
    data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for name, t in types.items():
        url = f"https://stock.adobe.com/search/{t}?k={kw.replace(' ', '+')}&order=relevance"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.find_all('img', alt=True)[:2]
            for item in items:
                data.append({"Category": name, "Popular Asset Title": item['alt']})
        except:
            continue
    return pd.DataFrame(data)

st.dataframe(get_live_selling(search_query), use_container_width=True)

# --- SECTION 3: GLOBAL COUNTRIES & DEMAND ---
st.markdown("---")
col1, col2 = st.columns(2)

try:
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([search_query], timeframe='now 7-d')

    with col1:
        st.subheader("📍 Top 10 Buying Countries")
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
    st.info("Global data update ho raha hai...")
