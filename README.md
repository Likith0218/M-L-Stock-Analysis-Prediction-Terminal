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
```

## Usage
1. Launch the app with `streamlit run Home.py`.
2. Select a stock category or search for a specific ticker.
3. View real-time data, charts, and technical indicators.
4. Adjust chart settings and analysis parameters as needed.

## Project Structure
```
.
├── Home.py            # Main application file
├── requirements.txt   # Python dependencies
├── LICENSE            # MIT License
├── README.md          # Project overview
└── /docs              # Documentation (optional)
```

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Authors
Developed by [LIKITH C](https://github.com/Likith0218) and [MOHAN S REDDY](https://github.com/<your-username>)
