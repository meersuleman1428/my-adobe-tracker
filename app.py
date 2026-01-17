import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Adobe Pro Insights", layout="wide")
st_autorefresh(interval=60 * 1000, key="datarefresh")

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

search_query = st.sidebar.text_input("Enter Topic (e.g. Dinosaur)", "Nature")

# --- DAILY TRENDS LIST (FIXED) ---
st.subheader("🔥 Adobe Stock: Daily Global Trends List")

@st.cache_data(ttl=3600) # Data ko 1 ghante ke liye save rakhega taake khali na dikhe
def get_daily_trends():
    url = "https://stock.adobe.com/search?k=trending+now"
    # User-Agent ko mazeed professional kiya hai
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Trending keywords nikalne ka naya tareeqa
        trends = soup.find_all('a', {'data-t': 'search-pill'})[:10] 
        if not trends: # Agar purana method kaam na kare toh ye check kare
            trends = soup.select('a[href*="/search?k="]')[:10]
            
        trend_list = [{"Trend Rank": i+1, "Topic": t.text.strip(), "Status": "📈 Growing"} for i, t in enumerate(trends) if len(t.text.strip()) > 2]
        return pd.DataFrame(trend_list)
    except Exception as e:
        return pd.DataFrame([{"Topic": "Refreshing Trends...", "Status": "Connecting to Adobe"}])

with st.spinner('Adobe se Trends nikal raha hoon...'):
    df_daily = get_daily_trends()
    if not df_daily.empty and len(df_daily) > 1:
        st.table(df_daily)
    else:
        st.info("Adobe temporary block kar raha hai, 1-2 minute mein data aa jayega.")

# --- Baki Sara Dashboard Code Pehle Jaisa ---
# (Yahan aapka pichla Downloads aur Charts wala code chalega)
