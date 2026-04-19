from groq import Groq
import streamlit as st
import yfinance as yf
import requests
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import xml.etree.ElementTree as ET # Added for reliable news fetching

# ── Groq client ───────────────────────────────────────────
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")

# ── Page config ───────────────────────────────────────────
st.set_page_config(page_title="Indian Stock Analyzer", page_icon="📈", layout="wide")

# ── Database Setup (Logging) ──────────────────────────────
def init_db():
    conn = sqlite3.connect('search_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (timestamp TEXT, stock_name TEXT, ticker TEXT, price REAL)''')
    conn.commit()
    conn.close()

def log_search(name, ticker, price):
    conn = sqlite3.connect('search_logs.db')
    c = conn.cursor()
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (time_now, name, ticker, price))
    conn.commit()
    conn.close()

init_db()

# ── Trendy UI Theme & Typography ──────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp {
    background: radial-gradient(circle at top right, #f8faff, #eef2ff);
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

strong {
    color: #4338ca;
    background-color: #eef2ff;
    padding: 2px 6px;
    border-radius: 6px;
    font-weight: 800;
}

[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #e0e7ff !important;
    border-radius: 16px !important;
    padding: 15px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
}

.disclaimer-banner {
    background: linear-gradient(to right, #fffbeb, #ffffff);
    border-left: 6px solid #f59e0b;
    padding: 20px 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.06);
}

.news-link {
    display: block;
    padding: 12px 16px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 10px;
    color: #1e1b4b !important;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s;
}
.news-link:hover {
    border-color: #6366f1;
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Custom Banner ─────────────────────────────────────────
try:
    st.image("banner.jpg", use_container_width=True)
except:
    st.error("⚠️ Missing banner.jpg in the directory.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Data Loading Logic (NSE Data Only) ────────────────────
@st.cache_data
def load_data():
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        lines = r.text.strip().split("\n")
        stock_dict = {}
        for l in lines[1:]:
            parts = l.split(",")
            if len(parts) > 1:
                ticker = parts[0].strip()
                name = parts[1].strip().title()
                stock_dict[f"{ticker} - {name}"] = (name, f"{ticker}.NS")
        return stock_dict
    except: return {"TATAMOTORS - Tata Motors": ("Tata Motors", "TATAMOTORS.NS")}

ALL_STOCKS = load_data()

# ── Search (Single Dropdown) ──────────────────────────────
st.markdown("### 🔍 Search Indian Equities (NSE)")

selected_option = st.selectbox(
    "Search NSE Stocks",
    options=list(ALL_STOCKS.keys()),
    index=None,
    placeholder="🔎 Start typing an NSE stock (e.g., Tata, ITC, Karur)...",
    label_visibility="collapsed"
)

# ── Main Dashboard ────────────────────────────────────────
if selected_option:
    name, ticker = ALL_STOCKS[selected_option]
    
    st.markdown("""
    <div class="disclaimer-banner">
        <h3 style="color: #b45309; margin: 0 0 8px 0; font-size: 1.2rem;">📌 Educational & Research Purposes Only</h3>
        <p style="color: #78350f; margin: 0; font-size: 0.9rem; line-height: 1.5;">
            All AI-generated insights and charts provided on this dashboard are strictly for educational and portfolio-building purposes. 
            <strong>This is NOT financial advice.</strong> Always perform your own due diligence before executing trades.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"## 🔭 Dashboard: **{name}**")

    with st.spinner("Fetching live market data & company profile..."):
        stk = yf.Ticker(ticker)
        try:
            fast_info = stk.fast_info
            full_info = stk.info 
            current_price = round(fast_info.last_price, 2)
            year_high = round(fast_info.year_high, 2)
            year_low = round(fast_info.year_low, 2)
            market_cap = f"₹{round(fast_info.market_cap/1e7):,} Cr"
            pe_ratio = round(full_info.get('trailingPE', 0), 2) if full_info.get('trailingPE') else "N/A"
        except:
            current_price, year_high, year_low, market_cap, pe_ratio = "N/A", "N/A", "N/A", "N/A", "N/A"
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Live Price", f"₹{current_price}" if current_price != "N/A" else "Data Error")
    m2.metric("52W High", f"₹{year_high}" if year_high != "N/A" else "N/A")
    m3.metric("52W Low", f"₹{year_low}" if year_low != "N/A" else "N/A")
    m4.metric("Market Cap", market_cap)
    m5.metric("P/E Ratio", pe_ratio)

    # ── Company Profile & News Section ─────────────
    with st.expander("🏢 Company Profile & Latest News", expanded=False):
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"**Sector:** {full_info.get('sector', 'N/A')} | **Industry:** {full_info.get('industry', 'N/A')}")
            summary = full_info.get('longBusinessSummary', 'Company description not available.')
            st.caption(summary[:600] + ("..." if len(summary) > 600 else ""))
            if full_info.get('website'):
                st.markdown(f"[🌐 Visit Official Website]({full_info.get('website')})")
        
        with c2:
            st.markdown("**📰 Recent Headlines**")
            try:
                # 1. Swapping Yahoo for Google News RSS (Highly Reliable)
                # We use the company name instead of ticker for better Indian news results
                search_query = f"{name.replace(' ', '+')}+stock+India"
                rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-IN&gl=IN&ceid=IN:en"
                
                # 2. CRITICAL: Adding a User-Agent header so Google doesn't block us as a bot
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                
                rss_resp = requests.get(rss_url, headers=headers, timeout=5)
                
                # Parse the XML
                root = ET.fromstring(rss_resp.content)
                items = root.findall('./channel/item')
                
                if items:
                    for item in items[:3]: 
                        title = item.find('title').text
                        link = item.find('link').text
                        st.markdown(f"<a href='{link}' target='_blank' class='news-link'>🗞️ {title}</a>", unsafe_allow_html=True)
                else:
                    st.caption("No recent news found for this company.")
            except Exception as e:
                # Failing gracefully without throwing ugly red syntax errors 
                st.caption("Unable to fetch news feed at this time. The news server might be temporarily blocking requests.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Advanced Interactive Chart ───────────────────────
    st.markdown("### 📊 Advanced Interactive Chart")
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        period = st.selectbox("Select Timeframe", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"], index=2)
    with col_c2:
        indicators = st.multiselect("Overlay Technical Indicators", ["SMA 20", "SMA 50", "EMA 20", "Volume"], default=["SMA 20", "Volume"])

    with st.spinner("Rendering advanced chart..."):
        try:
            hist = stk.history(period=period)
            if not hist.empty:
                if "Volume" in indicators:
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
                    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'), row=1, col=1)
                    vol_colors = ['#10b981' if row['Close'] >= row['Open'] else '#ef4444' for index, row in hist.iterrows()]
                    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', marker_color=vol_colors), row=2, col=1)
                    row_idx = 1
                else:
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'))
                    row_idx = None

                if "SMA 20" in indicators:
                    hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
                    trace = go.Scatter(x=hist.index, y=hist['SMA_20'], name='SMA 20', line=dict(color='#3b82f6', width=1.5))
                    if row_idx: 
                        fig.add_trace(trace, row=row_idx, col=1) 
                    else: 
                        fig.add_trace(trace)
                    
                if "SMA 50" in indicators:
                    hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
                    trace = go.Scatter(x=hist.index, y=hist['SMA_50'], name='SMA 50', line=dict(color='#f59e0b', width=1.5))
                    if row_idx: 
                        fig.add_trace(trace, row=row_idx, col=1) 
                    else: 
                        fig.add_trace(trace)
                    
                if "EMA 20" in indicators:
                    hist['EMA_20'] = hist['Close'].ewm(span=20, adjust=False).mean()
                    trace = go.Scatter(x=hist.index, y=hist['EMA_20'], name='EMA 20', line=dict(color='#8b5cf6', width=1.5))
                    if row_idx: 
                        fig.add_trace(trace, row=row_idx, col=1) 
                    else: 
                        fig.add_trace(trace)

                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=500 if "Volume" in indicators else 400, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Plus Jakarta Sans"))
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(gridcolor='#e0e7ff')
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Not enough market data available for this ticker.")
        except Exception as e:
            st.warning(f"Chart data error: {e}")

    # ── AI Analysis ─────────────────────────────────────
    analyze = st.button("🚀 GENERATE AI INSIGHTS", type="primary", use_container_width=True)

    if analyze:
        if current_price != "N/A":
            log_search(name, ticker, current_price) 
        
        tabs = st.tabs(["📋 Fundamental", "📉 Technical", "⚡ Short Term", "🏦 Long Term"])
        
        def call_ai(mode):
            prompt = f"""
            Act as an elite equity analyst. Provide a {mode} analysis for {name} ({ticker}).
            
            CRITICAL CONTEXT - USE THIS REAL-TIME DATA FOR YOUR ANALYSIS:
            - Current Live Price: ₹{current_price}
            - 52-Week High: ₹{year_high}
            - 52-Week Low: ₹{year_low}
            - Market Cap: {market_cap}
            - P/E Ratio: {pe_ratio}

            Do not use outdated pricing for your support and resistance levels. Base your critical levels near the Current Live Price of ₹{current_price}.

            You MUST format your response exactly like this:

            ### 🎯 The Verdict
            (State clearly: **STRONG BUY**, **BUY**, **HOLD**, or **SELL** and one sentence why.)

            ### ⚡ Key Drivers
            * **Catalyst 1**: (Explain briefly)
            * **Catalyst 2**: (Explain briefly)

            ### 📊 Critical Levels
            * **Resistance Target**: (Specific price above ₹{current_price})
            * **Support Base**: (Specific price below ₹{current_price})

            ### ⚠️ The Risk
            (One major risk factor. Be direct.)
            """
            try:
                res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                return res.choices[0].message.content
            except Exception as e: return f"⚠️ **AI Error**: Check your Groq API Key! ({e})"

        for i, mode in enumerate(["Fundamental", "Technical", "Short Term (1-3 months)", "Long Term (1-5 Years)"]):
            with tabs[i]:
                with st.container(border=True): 
                    with st.spinner(f"Generating {mode} intelligence..."):
                        st.markdown(call_ai(mode))

# ── Logs Expander ─────────────────────────────────────────
st.markdown("<br><br><br>", unsafe_allow_html=True) 
with st.expander("🗄️ System Logs & Export History (Local DB)"):
    conn = sqlite3.connect('search_logs.db')
    df_logs = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", conn)
    conn.close()
    
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download as CSV", data=df_logs.to_csv(index=False).encode('utf-8'), file_name='logs.csv', mime='text/csv')
    else:
        st.info("Your search history will appear here once you generate AI insights.")