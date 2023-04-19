from pyfinviz import Screener
import pandas as pd 
import time
import sys 

path = sys.path[0].replace('scripts', 'data')

# Run seperately to scrape ticker universe from Finviz
def get_ticker_universe(page=500):
    start_time = time.time()
    screener = Screener(pages=[x for x in range(1,page)])

    dict_tickers = {}
    for i in range(0,page):
        if i == 1:
            pass
        else:
            try:
                for j in range(len(screener.data_frames[i])):
                    dict_tickers[screener.data_frames[i].Ticker[j]] = screener.data_frames[i].Company[j]
            except:
                pass
            
    df = pd.DataFrame(dict_tickers.items())
    df.columns = ["Ticker", "Name"]
    df.to_csv(path + '/tickers-universe.csv', index=False)
    print('---%s seconds ---' %(time.time() - start_time))

# Get tickers universe from Local File
tickers = pd.read_csv(path + '/data/tickers-universe.csv')
tickers['Ticker + Name'] = tickers['Ticker'] + ' - ' + tickers['Name']
tickers = tickers.drop_duplicates().dropna().reset_index(drop=True)

# Convert tickers DataFrame to Dictionary to be used as values and labels in the dropdown
tickers_dict = {}
n = tickers.shape[0]
for i in range(n):
    tickers_dict[tickers.loc[i]["Ticker"]] = tickers.loc[i]["Ticker + Name"]

ticker_labels = [{'label':tickers_dict[i], 'value':i} for i in list(tickers_dict.keys())]
