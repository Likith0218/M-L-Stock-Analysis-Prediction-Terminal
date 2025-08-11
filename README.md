# M&L Stock Analysis & Prediction Terminal

An interactive Streamlit web application for real-time stock market analysis, technical indicator visualization, and trend prediction.  
Fetches live data from Yahoo Finance, applies technical analysis with the `ta` library, and displays results through interactive Plotly charts.

## Features
- Real-time Market Data from Yahoo Finance
- Technical Analysis tools: Moving Averages, RSI, MACD, and more
- Global & Indian Markets coverage
- Interactive Plotly charts with zoom and hover insights
- Preloaded stock categories for quick access
- Responsive, wide-screen optimized UI

## Tech Stack
- Python
- Streamlit
- yFinance
- Pandas, NumPy
- Plotly
- TA (Technical Analysis library)
- Requests

## Installation
```bash
# Clone the repository
git clone https://github.com/<your-username>/<repo>.git
cd <repo>

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run Home.py
