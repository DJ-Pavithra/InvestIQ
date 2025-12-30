"""
Data building module for InvestIQ.
"""
import yfinance as yf
import os

companies = ["AAPL", "MSFT", "GOOGL","NVDA","AMZN","META","TSLA"]

all_text = ""

for symbol in companies:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    summary = info.get("longBusinessSummary", "")
    all_text += f"{symbol}:\n{summary}\n\n"

os.makedirs("data", exist_ok=True)

with open("data/finance.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print("✅ Financial data collected and saved.")

