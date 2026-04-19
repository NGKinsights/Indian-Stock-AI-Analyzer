# 📈 Indian Stock AI Analyzer

A real-time, AI-powered financial dashboard for Indian equities (NSE).

## 🚀 Overview
A full-stack application built to bridge the gap between complex financial data and actionable AI insights. Designed for retail investors to perform fundamental and technical analysis.

## 🛠 Tech Stack
* **Frontend:** Streamlit
* **AI Engine:** Llama 3 (via Groq API)
* **Data Pipelines:** `yfinance` for real-time market data & Google News RSS.
* **Backend:** SQLite for search history telemetry.

## 💡 Key Features
* **Live Market Data:** Real-time price tracking and company news.
* **Mitigated AI Hallucinations:** Injects live market data into the LLM context to ensure accurate analysis.
* **Interactive Charts:** Dynamic Plotly candlestick charts with technical indicators.
* **System Logs:** Automated database logging of all searches.

## ⚙️ How to Run
1. Clone this repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Set your Groq API key in the script.
4. Run the app: `streamlit run stock_sentiment.py`

![Demo Video](https://drive.google.com/file/d/11Wpv7asiBTM2QTEnXW87DCgz4Z48XqpE/view?usp=drive_link)
