@st.cache_data(ttl=3600)
def get_daily_trends():
    # Pehle koshish karega live data lane ki
    url = "https://stock.adobe.com/search?k=trending+now"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        trends = soup.select('a[data-t="search-pill"]')[:10]
        
        if trends:
            return pd.DataFrame([{"Trend Rank": i+1, "Topic": t.text.strip(), "Status": "📈 Growing"} for i, t in enumerate(trends)])
    except:
        pass

    # AGAR ADOBE BLOCK KARE TO YE BACKUP LIST DIKHAYE GA (2026 Trends)
    backup_trends = [
        {"Trend Rank": 1, "Topic": "AI Abstract Backgrounds", "Status": "🔥 Hot"},
        {"Trend Rank": 2, "Topic": "Sustainability & Green Energy", "Status": "📈 Growing"},
        {"Trend Rank": 3, "Topic": "3D Isometric Characters", "Status": "🔥 Hot"},
        {"Trend Rank": 4, "Topic": "Mental Health Awareness Visuals", "Status": "📈 Growing"},
        {"Trend Rank": 5, "Topic": "Cyberpunk Cityscapes", "Status": "🔥 Hot"}
    ]
    return pd.DataFrame(backup_trends)
