import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Adobe Pro Insights", layout="wide")
# Refresh time ko 5 minute kar diya hai taake Google block na kare
st_autorefresh(interval=300 * 1000, key="datarefresh") 

st.title("🚀 Adobe Stock Live Market & Daily Trends")
st.write(f"🕒 Last Sync: {pd.Timestamp.now().strftime('%H:%M:%S')}")

search_query = st.sidebar.text_input("Enter Topic", "Cyberpunk")

# --- Tables section wahi rahega jo pehle sahi chal raha hai ---
# ... (Baki code same hai) ...

try:
    # Adding more "Human-like" connection settings
    pytrends = TrendReq(hl='en-US', tz=360, retries=5, backoff_factor=0.5)
    # ... (Charts logic) ...
except:
    st.warning("Google is resting. Charts will auto-load in 5 minutes.")
