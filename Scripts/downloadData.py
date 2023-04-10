import yfinance as yf

tickers = ['SPY','GLD','TLT','BITO']
data = yf.download(tickers, period='max')
data = data['Adj Close']
data.to_csv('../Data/sample-data.csv', index=True)
