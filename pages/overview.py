from dash import html, dcc, Input, Output, callback
import dash
from dash import dash_table
from dash.dash_table import FormatTemplate
import dash_bootstrap_components as dbc
import yfinance as yf
import pandas as pd 
import quantstats as qs 
import datetime
import sys
import scripts.style as style

dash.register_page(__name__)

# Initialize Variables
path = sys.path[0].replace('pages','data')
start_date = '2012-01-03'
percentage = FormatTemplate.percentage(2)

tickers = {'BTC-USD':'Bitcoin',
            'QQQ': 'US Nasdaq 100',
            'GLD': 'Gold',
            'SPY': 'US Large Caps',
            'TLT': 'Long Duration Treasuries',
            'SHY': 'Short Duration Treasuries',
            'EEM': 'EM Stocks',
            'IGLB': 'Long Term IG Bonds',
            'IGSB': 'Short Term IG Bonds',
            'PFF': 'Preferred Stocks',
            'CWB': 'Convertible Bonds',
            'HYG': 'High Yield Bonds',
            'TIP': 'TIPS',
            'BND': 'US Total Bond Market',
            'EMB': 'EM Bonds (USD)',
            'IWM': 'US Small Caps',
            'BIL': 'US Cash',
            'VNQ': 'US REITs',
            'DBC': 'Commodities',
            'XLF': 'Financials',
            'XLE': 'Energy',
            'XLU': 'Utilities',
            'XLY': 'Consumer Discretionary',
            'XLI': 'Industrials',
            'XLRE': 'Real Estate',
            'XLP': 'Consumer Staples',
            'XLK': 'Technology',
            'XLC': 'Communications',
            'XLV': 'Health Care',
            'XLB': 'Materials'
            }

tickers_mapping = {'overview': ['BTC-USD','QQQ','GLD','SPY','TLT','SHY','EEM','IGLB','IGSB','PFF','CWB','HYG','TIP','BND','EMB','IWM','BIL','VNQ','DBC'],
                    'sectors': ['XLF','XLE','XLU','XLY','XLI','XLRE','XLP','XLK','XLC','XLV','XLB']
                }

# Download / Load Data from yfinance / local 
def loadData(input_path=path+'/data/prices.csv', clean=True):
    '''
    Loads asset prices data from local file.
    '''
    prices = pd.read_csv(input_path, index_col=0)
    if clean:
        prices.index = pd.to_datetime(prices.index)
        prices = prices.ffill()
    return prices

def downloadData(tickers=list(tickers.keys()), output_path=path+'/data/prices.csv'):
    '''
    Loads asset prices data from local file and adds new data to it. 
    Creates local file if not available. 
    '''
    try:
        prices = loadData()
        max_date = pd.to_datetime(prices.index[-1])
        delta_days = (datetime.datetime.today() - max_date).days

        if delta_days >= 1: # Retrieve new price data.
            start = max_date - datetime.timedelta(3) # Always retrieve data for past 3 days and re-adjust local file.
            add_on_prices = yf.download(tickers, start=start)['Adj Close']
            prices = pd.concat([prices, add_on_prices]) # Append new data to current csv file
            prices = prices[~prices.index.duplicated()]
            prices = prices.ffill()
            print("Latest data downloaded and appended.")

        else:
            return prices

    except: 
        print("Couldn't load data from local file.")
        prices = yf.download(tickers, period='max')['Adj Close'] 
        print("All data downloaded from yfinance.")

    prices.to_csv(output_path)
    return prices

prices = downloadData()
prices = prices.loc[start_date:]

# Create performance table function 
def create_performance_table(prices, mapping='overview'):
    prices = prices[tickers_mapping[mapping]]
    returns = qs.utils._prepare_returns(prices)

    # Group by year and create returns table
    yearly_returns = qs.utils.aggregate_returns(returns, 'eoy', compounded=True)
    yearly_returns_T = yearly_returns.transpose()

    # Create DataFrame for tickers from the initial tickers dictionary
    tickers_df = pd.DataFrame(index=list(tickers.keys()), data=list(tickers.values()), columns=['Name'])

    # Create table
    merged = pd.merge(tickers_df, yearly_returns_T, left_on=tickers_df.index, right_on=yearly_returns_T.index, how='inner').rename(columns={'key_0':'Ticker'})
    merged.columns = merged.columns.astype(str)
    merged = merged.replace(0,'') # In case the asset doesn't have data in a particular year, after the start date
    unique_years = [str(col) for col in yearly_returns_T.columns] # Use this to sort columns 
    merged['Start Date'] = [prices[ticker].first_valid_index().strftime("%m/%d/%Y") for ticker in merged['Ticker'].unique()]
    merged['End Date'] = [prices[ticker].last_valid_index().strftime("%m/%d/%Y") for ticker in merged['Ticker'].unique()]
    col_order = ['Ticker','Name','Start Date', 'End Date'] + unique_years
    merged = merged[col_order] # Adjust columns order

    # Add total returns to table
    total_rets = pd.DataFrame(qs.stats.comp(returns), columns=["Total"])
    merged = pd.merge(merged, total_rets, left_on=merged.Ticker, right_on=total_rets.index, how='left').drop('key_0', axis=1)
    merged['Ticker'] = [f"[{t}](https://finance.yahoo.com/quote/{t})" for t in merged['Ticker'].unique()] # Redirect to Yahoo's ticker page.
    
    # Create dash table
    data = merged.to_dict('records')
    columns = [dict(id=i, name=i, presentation='markdown') if i =='Ticker' else dict(id=i, name=i, type='numeric', format=percentage) for i in merged.columns]

    dt = dash_table.DataTable(data, 
                            columns, 
                            fixed_columns={'headers':True, 'data':1}, 
                            sort_action='native',
                            style_as_list_view=False,
                            style_table={'minWidth':'100%',
                                        'minHeight':150},
                            style_data=style.create_table_data_style(padding='2px'),
                            style_header=style.style_header,
                            style_cell={
                                'textAlign': 'center',
                                'padding':'5px',
                                'minWidth': 95},
                            style_data_conditional=[{'if': {'filter_query': f'{{{col}}} < 0',
                                                                'column_id': col},
                                                                'backgroundColor':'red'} for col in merged.columns] +                          
                                                        [{'if': {'filter_query': f'{{{col}}} > 0',
                                                                'column_id': col},
                                                        'backgroundColor':'green'}
                                                        for col in merged.columns] +
                                                        [{'if': {'column_id': 'Year'},
                                                        'color':'white'}]                                              
                                                        )
    return dt

layout = dbc.Container([

                    dcc.Interval(id='refresh-interval', 
                                    #interval=288000000, #8 hours, 288M ms
                                    interval=6000,
                                    n_intervals=0
                                    ),

                    dbc.Row([
            
                        html.H5('Asset Class Performance', className=style.h5_style),

                        dbc.Col([
                            html.Div(id='asset-class-performance-table', children=create_performance_table(prices))
                        ]),

                        html.H5('Sector Performance', className=style.h5_style),

                        dbc.Col([
                            html.Div(id='sector-performance-table', children=create_performance_table(prices, 'sectors'))
                        ])

                    ], className=style.dbc_row_style),

], fluid=True)

@callback(Output('asset-class-performance-table', 'children'),
        Output('sector-performance-table', 'children'),
        [Input('refresh-interval','n_intervals')],
        prevent_initial_call=True)
def update_data(n_intervals):
    if n_intervals > 0:
        try:
            downloadData(tickers)
        except:
            pass
        prices = loadData()
        prices = prices.loc[start_date:]
        return create_performance_table(prices, 'overview'), create_performance_table(prices, 'sectors')