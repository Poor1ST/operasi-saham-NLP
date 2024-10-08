import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from finta import TA
from datetime import datetime
import streamlit as st

# Initialize session state for stock data
if 'stock_data' not in st.session_state:
    st.session_state['stock_data'] = None

indonesian_months = {
    "januari": "January", "februari": "February", "maret": "March",
    "april": "April", "mei": "May", "juni": "June",
    "juli": "July", "agustus": "August", "september": "September",
    "oktober": "October", "november": "November", "desember": "December"
}

# Tokenization function
def tokenize(sentence):
    return sentence.replace(",", "").replace(".", "").split()

# Helper function to parse Indonesian dates
def parse_date(day, month, year):
    try:
        if month.lower() in indonesian_months:
            month = indonesian_months[month.lower()]
        date_string = f"{day} {month} {year}"
        return datetime.strptime(date_string, "%d %B %Y")
    except ValueError:
        return None

# Function to extract keywords like stock ticker, dates, actions, and indicators
def extract_keywords(tokens):
    actions = ["ambil", "tampilkan", "hitung"]
    indicators = ["rsi", "macd", "ma50", "ma20"]
    stock_ticker = None
    start_date = None
    end_date = None
    requested_actions = []
    requested_indicators = []

    for i, token in enumerate(tokens):
        if token.isupper() and len(token) == 4 and token != "MACD":
            stock_ticker = token
        if token.isdigit() and i+2 < len(tokens):
            day, month, year = token, tokens[i+1], tokens[i+2]
            date = parse_date(day, month, year)
            if date:
                if not start_date:
                    start_date = date
                else:
                    end_date = date
        if token.lower() in actions:
            requested_actions.append(token)
        if token.lower() in indicators:
            requested_indicators.append(token)

    return {
        "stock_ticker": stock_ticker,
        "start_date": start_date,
        "end_date": end_date,
        "actions": requested_actions,
        "indicators": requested_indicators
    }

# Streamlit command execution function
def execute_command(command):
    tokens = tokenize(command)
    parsed_data = extract_keywords(tokens)

    ticker = parsed_data["stock_ticker"]
    start_date = parsed_data["start_date"]
    end_date = parsed_data["end_date"] or datetime.today()
    actions = parsed_data["actions"]
    indicators = parsed_data["indicators"]

    if ticker:
        st.write(f"Fetching stock data for {ticker} from {start_date} to {end_date}")
        hist = yf.Ticker(ticker.lower() + ".jk")
        stock_data = hist.history(start=start_date, end=end_date, auto_adjust=True)

        stock_data['Name'] = ticker
        # Save stock_data in session state for future use
        st.session_state['stock_data'] = stock_data
        ticker = None

    for action in actions:
        if action == "ambil":
            st.write(stock_data)
        
        # Calculate technical indicators using finta
        if indicators:
            for indicator in indicators:
                if indicator.lower() == "rsi":
                    stock_data['RSI'] = TA.RSI(stock_data)
                    st.write("RSI calculated.")
                if indicator.lower() == "macd":
                    macd_data = TA.MACD(stock_data)
                    stock_data['MACD'] = macd_data['MACD']
                    stock_data['MACD_Signal'] = macd_data['SIGNAL']
                    st.write("MACD calculated.")
                if indicator.lower() == "ma50":
                    stock_data['MA50'] = TA.SMA(stock_data, 50)
                    st.write("MA50 calculated.")
                if indicator.lower() == "ma20":
                    stock_data['MA20'] = TA.SMA(stock_data, 20)
                    st.write("MA200 calculated.")
            st.write(stock_data.tail())
            # Save stock_data in session state for future use
            st.session_state['stock_data'] = stock_data
            st.write("Stock data saved in session state.")
        

        # Plot the stock data and indicators
        if action == "tampilkan":
            stock_data = st.session_state['stock_data']
            st.write("Displaying the stock data chart with indicators:")
            plt.figure(figsize=(10, 6))
            plt.plot(stock_data['Close'], label='Close Price')
            for indicator in indicators:
                if indicator == "ma50":
                    plt.plot(stock_data['MA50'], label='MA50')
                if indicator == "ma200":
                    plt.plot(stock_data['MA20'], label='MA20')
                if indicator == "rsi":
                    plt.plot(stock_data['RSI'], label='RSI')
                if indicator == "macd":
                    plt.plot(stock_data['MACD'], label='MACD')
                    plt.plot(stock_data['MACD_Signal'], label='MACD Signal')
            plt.title(f'{stock_data["Name"]} Stock Data with Indicators')
            plt.legend()
            st.pyplot(plt)

# Streamlit UI

st.title("Stock Data Command Processing with Technical Indicators")

# Input box for command
command = st.text_input("Enter your command (e.g., 'ambil harga saham AAPL dari 1 Januari 2023 sampai 31 Januari 2023'): ")

# Button to execute the command
if st.button("Execute"):
    if command:
        execute_command(command)
    else:
        st.write("Please enter a valid command.")

# Display previously fetched stock data (if available)
if st.session_state['stock_data'] is not None:
    st.write("Previously fetched stock data:")
    st.write(st.session_state['stock_data'].tail())
