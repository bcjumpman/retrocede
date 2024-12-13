import yfinance as yf
import pandas as pd

def get_stock_data(symbol):
    """
    Fetch stock data from Yahoo Finance and calculate averages if needed.
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="5d") # 5 days
        if data.empty:
            return {"error": "No data available for this symbol"}

        # Get the most recent day's data
        latest_data = data.iloc[-1]

        # Calculate averages for high, low, and volume for the available period
        avg_high = data['High'].mean()
        avg_low = data['Low'].mean()
        avg_volume = data['Volume'].mean()

        return {
            "symbol": symbol.upper(),
            "date": str(latest_data.name.date()),
            "open": latest_data["Open"],
            "high": latest_data["High"],
            "low": latest_data["Low"],
            "close": latest_data["Close"],
            "volume": int(latest_data["Volume"]),
            "avg_high": avg_high,
            "avg_low": avg_low,
            "avg_volume": avg_volume,
        }
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
