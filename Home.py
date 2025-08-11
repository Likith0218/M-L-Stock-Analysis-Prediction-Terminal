import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time
import ta
from typing import Dict, Optional
import requests

# Page Configuration Settings
st.set_page_config(
    page_title="M&L Stock Analysis and prediction Terminal",
    page_icon="M&L",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Likith0218',
        'Report a bug': "https://github.com/Likith0218",
        'About': "# Stock Analysis Terminal\nA modern stock analysis tool."
    }
)

# Define common stock categories and symbols for quick access
# Update COMMON_STOCKS to include Indian stocks
COMMON_STOCKS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA"],
    "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
    "Finance": ["JPM", "BAC", "V", "MA", "GS"],
    "Retail": ["AMZN", "WMT", "COST", "TGT", "HD"],
    "Electric Vehicles": ["TSLA", "F", "GM", "NIO", "RIVN"],
    "Indian Tech": ["TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS"],  # Updated LTI to HCLTECH
    "Indian Banks": ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS"]
}

# Add this CSS for loading animation
st.markdown("""
    <style>
    /* Loading Animation */
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #64ffda;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
""", unsafe_allow_html=True)

# Update the MARKET_INDICES dictionary
MARKET_INDICES = {
    "US Markets": [
        {"symbol": "^GSPC", "name": "S&P 500"},
        {"symbol": "^DJI", "name": "Dow Jones"},
        {"symbol": "^IXIC", "name": "NASDAQ"}
    ],
    "Indian Markets": [
        {"symbol": "^NSEI", "name": "NIFTY 50"},
        {"symbol": "^BSESN", "name": "SENSEX"}
        
    ],
    "Forex": [
        {"symbol": "EURUSD=X", "name": "EUR/USD"},
        {"symbol": "GBPUSD=X", "name": "GBP/USD"},
        {"symbol": "INR=X", "name": "USD/INR"}
    ]
}

# Update the fetch_market_overview function to handle Indian market data
def fetch_market_overview():
    """Fetch real-time market data for overview section"""
    market_data = {}
    
    for category, symbols in MARKET_INDICES.items():
        market_data[category] = []
        for item in symbols:
            try:
                ticker = yf.Ticker(item["symbol"])
                info = ticker.fast_info
                current_price = info.last_price if hasattr(info, 'last_price') else 0
                prev_close = info.previous_close if hasattr(info, 'previous_close') else 0
                change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                
                # Format price based on market type
                if "Indian Markets" in category:
                    price_str = f"₹{current_price:,.2f}"
                else:
                    price_str = f"${current_price:,.2f}"
                
                market_data[category].append({
                    "name": item["name"],
                    "price": price_str,
                    "change": change,
                    "raw_price": current_price  # Keep raw price for sorting if needed
                })
            except Exception:
                continue
    
    return market_data

def fetch_stock_data(symbol: str):
    """Fetches comprehensive stock data for a given symbol"""
    with st.spinner('Loading stock data...'):
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="1y")

            if history.empty:
                st.error("No price data available")
                return None

            current_price = float(history['Close'].iloc[-1])
            
            with st.spinner('Fetching company information...'):
                info = ticker.info

            # Get earnings data
            with st.spinner('Loading financial data...'):
                try:
                    income_stmt = ticker.income_stmt
                    if income_stmt is not None and not income_stmt.empty:
                        # Extract quarterly data
                        quarterly_data = {
                            'Revenue': income_stmt.loc['Total Revenue'].iloc[:4],
                            'Earnings': income_stmt.loc['Net Income'].iloc[:4]
                        }
                        earnings_df = pd.DataFrame(quarterly_data)
                        has_earnings = True
                    else:
                        earnings_df = None
                        has_earnings = False
                except:
                    earnings_df = None
                    has_earnings = False

            st.success('Data loaded successfully!')
            return {
                'symbol': symbol,
                'price': current_price,
                'name': info.get('longName', symbol),
                'history': history,
                'info': info,
                'earnings': earnings_df,
                'has_earnings': has_earnings
            }

        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return None

def fetch_market_overview():
    """Fetch real-time market data for overview section"""
    market_data = {}
    
    for category, symbols in MARKET_INDICES.items():
        market_data[category] = []
        for item in symbols:
            try:
                ticker = yf.Ticker(item["symbol"])
                info = ticker.fast_info
                current_price = info.last_price if hasattr(info, 'last_price') else 0
                prev_close = info.previous_close if hasattr(info, 'previous_close') else 0
                change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                
                # Format price based on market type
                if "Indian Markets" in category:
                    price_str = f"₹{current_price:,.2f}"
                else:
                    price_str = f"${current_price:,.2f}"
                
                market_data[category].append({
                    "name": item["name"],
                    "price": price_str,
                    "change": change,
                    "raw_price": current_price  # Keep raw price for sorting if needed
                })
            except Exception:
                continue
    
    return market_data

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates various technical indicators for stock analysis
    
    Parameters:
        df (pd.DataFrame): DataFrame containing OHLCV data
    
    Returns:
        pd.DataFrame: DataFrame with added technical indicators
    """
    # Create a copy to avoid modifications to original data
    df = df.copy()
    
    # Moving Averages
    df['EMA_9'] = ta.trend.ema_indicator(df['Close'], window=9)
    df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
    df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['Close'])
    df['BB_Upper'] = bollinger.bollinger_hband()
    df['BB_Lower'] = bollinger.bollinger_lband()
    df['BB_Middle'] = bollinger.bollinger_mavg()
    
    # Volume indicators
    df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
    
    return df

def display_overview(data: dict):
    """
    Displays the main overview section with key metrics and price chart
    
    Parameters:
        data (dict): Stock data dictionary containing all required information
    """
    st.markdown(f"""
        <div class="glass-container">
            <h2 class="neon-header">
                {data['name']} ({data['symbol']})
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Create modern metrics layout
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_price = data['price']
        prev_close = data['history']['Close'].iloc[-2]
        price_change = ((current_price/prev_close)-1) if prev_close != 0 else 0
        st.metric(
            "Current Price", 
            f"${current_price:.2f}",
            f"{price_change*100:.1f}%"
        )
    
    with col2:
        market_cap = data['info'].get('marketCap', 0)
        if market_cap:
            market_cap_b = market_cap / 1e9
            st.metric(
                "Market Cap", 
                f"${market_cap_b:.2f}B" if market_cap_b else "N/A"
            )
        else:
            st.metric("Market Cap", "N/A")
    
    with col3:
        week_change = data['info'].get('52WeekChange')
        st.metric(
            "52 Week Change",
            f"{week_change*100:.1f}%" if week_change else "N/A"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Price Chart
    st.subheader("Price History")
    fig = go.Figure(data=[go.Candlestick(
        x=data['history'].index,
        open=data['history']['Open'],
        high=data['history']['High'],
        low=data['history']['Low'],
        close=data['history']['Close'],
        name='OHLC'
    )])
    
    fig.update_layout(
        height=400,
        template='plotly_dark',
        xaxis_title="Date",
        yaxis_title="Price ($)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def is_market_open():
    """Check if the market is currently open (US Eastern Time)"""
    now = datetime.now()
    # Convert to US Eastern Time (UTC-4)
    et_time = now - timedelta(hours=4)
    
    # Check if it's a weekday
    if et_time.weekday() < 5:  # Monday = 0, Friday = 4
        # Market hours are 9:30 AM to 4:00 PM ET
        market_start = et_time.replace(hour=9, minute=30, second=0)
        market_end = et_time.replace(hour=16, minute=0, second=0)
        return market_start <= et_time <= market_end
    return False

def enhanced_sidebar():
    """
    Enhanced sidebar with stock selection, date range, and auto-refresh controls
    """
    with st.sidebar:
        st.markdown("### Stock Selection")
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT)", "")
        
        # Date range selection
        st.markdown("### Date Range")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        start_date = st.date_input("Start Date", start_date)
        end_date = st.date_input("End Date", end_date)
        
        # Add auto-refresh controls
        st.markdown("### Auto-Refresh Settings")
        enable_auto_refresh = st.toggle("Enable Auto-Refresh", value=False)
        refresh_interval = st.slider(
            "Refresh Interval (seconds)",
            min_value=5,
            max_value=300,
            value=60
        )
        
        # Display last update time
        if 'last_update' in st.session_state:
            st.markdown(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        return symbol, start_date, end_date, enable_auto_refresh, refresh_interval

# Update the main() function to include auto-refresh
def main():
    """Main application function with auto-refresh capability"""
    # Title section at the very top
    st.markdown("""
        <div class="glass-container" style="text-align: center; padding: 30px;">
            <h1 class="neon-header" style="font-size: 3em; margin-bottom: 10px;">
                M&L Stock Analysis Terminal
            </h1>
            <p style="color: #66b2ff; font-size: 1.2em;">
                Advanced Technical & Fundamental Analysis
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get inputs including auto-refresh settings
    symbol, start_date, end_date, enable_auto_refresh, refresh_interval = enhanced_sidebar()
    
    # Initialize last update time if not exists
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
    
    # Check if it's time to refresh
    current_time = datetime.now()
    time_elapsed = (current_time - st.session_state.last_update).total_seconds()
    
    # Auto-refresh logic
    if enable_auto_refresh and time_elapsed >= refresh_interval:
        if is_market_open():
            st.session_state.last_update = current_time
            # Refresh market data
            if 'stock_data' in st.session_state:
                st.session_state.stock_data = fetch_stock_data(
                    st.session_state.stock_data['symbol']
                )
            # Force page refresh
            st.rerun()
        else:
            st.sidebar.warning("Market is closed. Auto-refresh paused.")
    
    # Use enhanced sidebar
    # symbol, start_date, end_date = enhanced_sidebar()

    # Welcome message after title
    if "stock_data" not in st.session_state:
        st.markdown("""
            <div class="glass-container" style="text-align: center; padding: 40px;">
                <h2 class="neon-header">Welcome to M&L Stock Analysis and Prediction </h2>
                <p style="font-size: 1.2em; color: #66b2ff; margin: 20px 0;">
                    Get started by:
                </p>
                <ul style="list-style: none; padding: 0;">
                    <li><<<< Enter a stock symbol in the sidebar</li>
                    <li>Click on stocks in the Popular Stocks section</li>
                    <li>Add stocks to your watchlist</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Display market overview
    def display_market_overview():
        """Display market overview data in a modern grid layout"""
        st.subheader("Market Overview")
        market_data = fetch_market_overview()
        
        for category, items in market_data.items():
            st.markdown(f"### {category}")
            for item in items:
                color = "green" if item["change"] >= 0 else "red"
                st.markdown(
                    f"""
                    <div class="ticker-row">
                        <span class="ticker-name">{item['name']}</span>
                        <span class="ticker-price">{item['price']}</span>
                        <span class="ticker-change" style="color: {color}">
                            {item['change']:+.2f}%
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    display_market_overview()
    
    # Create modern layout for watchlist and common stocks
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.subheader("Watchlist")
        # Initialize watchlist in session state if not exists
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = []
            
        # Display watchlist stocks
        for symbol in st.session_state.watchlist:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                current_price = info.last_price if hasattr(info, 'last_price') else 0
                st.write(f"{symbol}: ${current_price:.2f}")
            except:
                st.write(f"Unable to fetch data for {symbol}")
        
        # Add to watchlist
        new_symbol = st.text_input("Add stock to watchlist", key="watchlist_input")
        if st.button("Add") and new_symbol:
            if new_symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_symbol)
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.subheader("Popular Stocks")
        
        # Create tabs for different categories
        category_tabs = st.tabs(list(COMMON_STOCKS.keys()))
        
        # Display stocks for each category in its respective tab
        for tab, category in zip(category_tabs, COMMON_STOCKS.keys()):
            with tab:
                # Create columns for button grid layout
                cols = st.columns(3)  # Show 3 stocks per row
                for idx, symbol in enumerate(COMMON_STOCKS[category]):
                    with cols[idx % 3]:
                        # Create a styled button container
                        st.markdown(
                            f"""
                            <div style='
                                background: rgba(255, 255, 255, 0.05);
                                border-radius: 8px;
                                padding: 5px;
                                margin: 5px 0;
                                text-align: center;
                            '>
                            """, 
                            unsafe_allow_html=True
                        )
                        if st.button(symbol, key=f"common_stock_{symbol}", 
                                   use_container_width=True):
                            st.session_state.stock_data = fetch_stock_data(symbol)
                        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display analysis tabs if stock data is available
    if "stock_data" in st.session_state:
        data = st.session_state.stock_data
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", 
            "Technical Analysis", 
            "Fundamental Analysis",
            "Financial Metrics",
            "Ownership Analysis"
        ])
        
        with tab1:
            display_overview(data)
        
        with tab2:
            def display_technical(data):
                st.subheader("Technical Analysis")
                # Add technical indicators chart and analysis here
                if 'history' in data:
                    df_tech = calculate_technical_indicators(data['history'])
                    st.line_chart(df_tech[['Close', 'SMA_20', 'SMA_50']])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("RSI")
                        st.line_chart(df_tech['RSI'])
                    with col2:
                        st.subheader("MACD")
                        st.line_chart(df_tech[['MACD', 'MACD_Signal']])
            
            display_technical(data)
            
        with tab3:
            def display_fundamental(data):
                st.subheader("Fundamental Analysis")
                if 'info' in data:
                    info = data['info']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
                        st.metric("Forward P/E", f"{info.get('forwardPE', 'N/A')}")
                    with col2:
                        st.metric("PEG Ratio", f"{info.get('pegRatio', 'N/A')}")
                        st.metric("Beta", f"{info.get('beta', 'N/A')}")
            
            display_fundamental(data)
            
        with tab4:
            def display_fundamental_metrics(data):
                st.subheader("Financial Metrics")
                if 'info' in data:
                    info = data['info']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Revenue Growth", f"{info.get('revenueGrowth', 'N/A')}")
                        st.metric("Gross Margins", f"{info.get('grossMargins', 'N/A')}")
                    with col2:
                        st.metric("Profit Margins", f"{info.get('profitMargins', 'N/A')}")
                        st.metric("Operating Margins", f"{info.get('operatingMargins', 'N/A')}")
            
            def display_earnings(data):
                st.subheader("Earnings Analysis")
                if data.get('has_earnings', False) and data['earnings'] is not None:
                    st.line_chart(data['earnings'])
                else:
                    st.write("No earnings data available")
            
            display_fundamental_metrics(data)
            display_earnings(data)
            
        with tab5:
            def display_ownership_analysis(data):
                st.subheader("Ownership Analysis")
                if 'info' in data:
                    info = data['info']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Institutional Ownership", f"{info.get('institutionPercentHeld', 'N/A')}")
                        st.metric("Insider Ownership", f"{info.get('insiderPercentHeld', 'N/A')}")
                    with col2:
                        st.metric("Short Ratio", f"{info.get('shortRatio', 'N/A')}")
                        st.metric("Short % of Float", f"{info.get('shortPercentOfFloat', 'N/A')}")
            
            display_ownership_analysis(data)
            
# CSS Styling comments
st.markdown("""
    <style>
    /* Main Theme and Background */
    html, body, [class*="css"] {
        /* Dark theme with animated gradient background */
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(
            -45deg, 
            #1a1c2c 0%, 
            #161827 25%, 
            #0d1117 50%, 
            #161827 75%, 
            #1a1c2c 100%
        );
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e0e0e0;
    }

    @keyframes gradientBG {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    /* Enhanced Glass Container with Gradient Border */
    .glass-container {
        /* Glass morphism effect with gradient border */
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid transparent;
        border-image: linear-gradient(
            45deg,
            rgba(100,255,218,0.3),
            rgba(0,191,255,0.3)
        ) 1;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
        transition: all 0.3s ease;
    }

    .glass-container:hover {
        background: rgba(255, 255, 255, 0.05);
        border-image: linear-gradient(
            45deg,
            rgba(100,255,218,0.5),
            rgba(0,191,255,0.5)
        ) 1;
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25);
    }

    /* Modern Card with Gradient Animation */
    .modern-card {
        background: linear-gradient(
            135deg,
            rgba(28, 131, 225, 0.05) 0%,
            rgba(66, 71, 103, 0.05) 50%,
            rgba(28, 131, 225, 0.05) 100%
        );
        background-size: 200% 200%;
        animation: cardGradient 10s ease infinite;
        border: 1px solid rgba(28, 131, 225, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    @keyframes cardGradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    /* Animated Neon Header */
    .neon-header {
        background: linear-gradient(
            120deg,
            #64ffda 0%,
            #00bfff 50%,
            #64ffda 100%
        );
        background-size: 200% auto;
        animation: neonFlow 3s linear infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(100,255,218,0.5);
        font-weight: bold;
        letter-spacing: 2px;
    }

    @keyframes neonFlow {
        0% {
            background-position: 0% 50%;
        }
        100% {
            background-position: 200% 50%;
        }
    }

    /* Enhanced Metrics */
    [data-testid="stMetricValue"] {
        background: linear-gradient(45deg, #64ffda, #00bfff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.5em !important;
    }
    
    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, rgba(100,255,218,0.1) 0%, rgba(0,191,255,0.1) 100%);
        border-radius: 10px 10px 0 0;
        padding: 15px 20px;
        gap: 10px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(100,255,218,0.2) 0%, rgba(0,191,255,0.2) 100%);
    }
    
    /* Enhanced Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #64ffda, #00bfff);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #00bfff, #64ffda);
    }
    
    /* Data Tables Enhancement */
    .dataframe {
        /* Table styling for better readability */
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dataframe th {
        background: rgba(100,255,218,0.1);
        padding: 12px !important;
    }
    
    .dataframe td {
        padding: 10px !important;
    }
    
    /* Enhanced Market Overview Styling */
    .ticker-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        margin: 5px 0;
        transition: all 0.3s ease;
    }
    
    .ticker-row:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(5px);
    }
    
    .ticker-name {
        font-weight: 500;
        flex: 2;
    }
    
    .ticker-price {
        flex: 1;
        text-align: right;
        color: #64ffda;
    }
    
    .ticker-change {
        flex: 1;
        text-align: right;
        font-weight: bold;
    }
    
    /* Update Market Grid */
    .market-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Update the entry point (remove K.clear_session())
if __name__ == "__main__":
    main()
