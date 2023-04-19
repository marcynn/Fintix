import yfinance as yf
import sys

path = sys.path[0].replace('scripts','data')

tickers = ['SPY','GLD','TLT','BITO']
data = yf.download(tickers, period='2y')
data = data['Adj Close']
data.to_csv(path + '/sample-data.csv', index=True)
