import yfinance as yf

tickers = ['SPY','GLD','TLT','BITO']
data = yf.download(tickers, period='2y')
data = data['Adj Close']
data.to_csv('../Data/sample-data.csv', index=True)
