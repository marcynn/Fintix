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
            'DBC': 'Commodities'
            }

# Download / Load Data from yfinance / local 
def loadData(input_path=path+'/data/asset-classes-prices.csv', clean=True):
    prices = pd.read_csv(input_path, index_col=0)
    if clean:
        prices.index = pd.to_datetime(prices.index)
        prices = prices.ffill()
    return prices

def downloadData(tickers=list(tickers.keys()), period='max', output_path=path+'/data/asset-classes-prices.csv'):
    try:
        prices = loadData()
        max_date = str(prices.index[-1])[:10]
        add_on_prices = yf.download(tickers, start=max_date)['Adj Close']
        prices = pd.concat([prices, add_on_prices]) # Append new data to current csv file
        prices = prices[~prices.index.duplicated()]
    except: # Couldn't load data from local file
        prices = yf.download(tickers, period='max')['Adj Close'] 
    prices.to_csv(output_path)

prices = loadData()
prices = prices.loc[start_date:]

# Create table
def create_asset_overview_table(prices):
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

    # Create dash table
    data = merged.to_dict('records')
    columns = [dict(id=i, name=i, type='numeric', format=percentage) for i in merged]

    dt = dash_table.DataTable(data, 
                            columns, 
                            fixed_columns={'headers':True, 'data':1}, 
                            sort_action='native',
                            style_as_list_view=False,
                            style_table={'minWidth':'100%',
                                        'minHeight':150},
                            style_data={'whiteSpace': 'normal',
                                        'backgroundColor': style.secondary_theme_color,
                                        'color':'white', 
                                        'padding':'5px',
                                        'fontSize':'15px'},
                            style_header={
                                        'border': f'1px solid',
                                        'fontWeight':'bold',
                                        'textAlign': 'center',
                                        'padding':'5px',
                                        'backgroundColor': style.main_theme_color,
                                        'color':'white'},
                            style_cell={
                                'textAlign': 'center',
                                'padding':'5px'},

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
    
    dbc.Row([
        html.H3('Asset Class Performance', className='m-4'),

        dbc.Col([
            html.Div(id='last-refresh', className='float-end mb-2'),

            dcc.Interval(id='refresh-interval', 
                        interval=28800000, # 8hours
                        n_intervals=1
                        ),

            html.Div(id='asset-overview-table', children=create_asset_overview_table(prices))
        ],xs=12, sm=12, md=12, lg=12, xl=12)

    ], className=style.dbc_row_style)

], fluid=True)

@callback(Output('asset-overview-table', 'children'),
        Output('last-refresh','children'),
        [Input('refresh-interval','n_intervals')])
def update_data(n_intervals):
    try:
        downloadData(tickers)
        print('downloaded')
    except:
        pass
    prices = loadData()
    prices = prices.loc[start_date:]
    last_date = prices.index[-1]
    return create_asset_overview_table(prices), f'Last Update: {str(last_date)[:10]}'