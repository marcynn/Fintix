import pandas as pd
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import quantstats as qs
import plotly.graph_objs as go
import base64
import io
import datetime
import scripts.style as style
import scripts.metricsTable as metricsTable
import scripts.returnsModule as returnsModule
import scripts.benchmarkModule as benchmarkModule
import scripts.rollingModule as rollingModule

# Params
initial_amount = 1000
rfr = 0.02
periods_per_year = 252
rolling_periods = periods_per_year // 2

# Months Mapping -> Used in returns table
months_mapping = {1:'Jan',
                2:'Feb',
                3:'Mar',
                4:'Apr',
                5: 'May',
                6: 'Jun',
                7: 'Jul',
                8: 'Aug',
                9: 'Sep',
                10: 'Oct',
                11:'Nov',
                12:'Dec'}

# Handle stored data parsing
def json_to_df(data):
        '''
        Transform data from JSON to PDF.
        Modify this function to accomodate for different data sources that have a slightly different data frame shape --> (No date index, date column not named 'Date', etc.)
        '''
        data = pd.DataFrame(data).dropna()
        try:
            data.set_index('Date', inplace=True)
        except:
            data.index.name = 'Date' # Assumes that df has date as index

        try:
            data.index = pd.to_datetime(data.index)
        except:
            print('Could not change index to datetime')
            return 
        return data

#------------------- Data Load-------------------
def parse_content(contents, filename):
    '''
    Parses the content of an uploaded Excel file.
    '''
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except:
        print('Error parsing uploaded table')
        return
    
    return df

def display_uploaded_file(contents, filename, date):
    '''
    Display table of an uploaded Excel file.
    '''
    df = parse_content(contents, filename)
    assets = df.set_index('Date').columns.to_list()

    display = html.Div([

                    dbc.Col([
                        html.H5(filename),

                        html.H6(datetime.datetime.fromtimestamp(date)),

                        dash_table.DataTable(
                            data=df.to_dict('records'),
                            columns=[{'name': i, 'id': i} for i in df.columns],
                            page_size=5, 
                            fixed_columns={'headers':True, 'data':1}, 
                            style_cell={
                                'textAlign': 'center',
                                'padding':'5px'},
                            style_as_list_view=True,
                            sort_action='native',
                            style_table={'minWidth':'100%'},
                            style_data=style.style_data,
                            style_header=style.style_header,
                            css=[{'selector': '.current-page, last-page', 'rule': f'background-color: {style.main_theme_color};'}]
                        ),
                        
                        dbc.Row([

                            dbc.Col([

                                dbc.Button(id='submit-btn',
                                    children='Submit',
                                    n_clicks=0),

                            ], className='mb-3')
                        ]),
                        
                        dcc.Store(id='stored-data', data=df.to_dict('records')),
                    ]),
                ], style.dbc_row_style)    
                    
    return display

#-------------------Body-------------------
def create_params(initial_amount=initial_amount, rfr=rfr, periods_per_year=periods_per_year, rolling_periods=rolling_periods):

    date = datetime.date.today() # Used in dates params for date picker

    display = html.Div([

                        html.H3('Adjust Parameters', className='m-4'),

                        dbc.Row([

                                dbc.Row([
                                    html.P(children='Filter for Asset', className=style.params_p_style), 
                                    dcc.Dropdown(id='assets-dpdn',
                                                    multi=True,
                                                    className='text-primary')
                                        ], className='mb-3'),
                            
                                dbc.Col([
                                    html.P(children='Initial amount', className=style.params_p_style), 

                                    dcc.Input(id='initial-amount', 
                                            type='number', 
                                            placeholder='1,000', 
                                            value=initial_amount, 
                                            min=1,
                                            ),

                                    html.P(children='Risk-free rate', className=style.params_p_style),

                                    dcc.Input(id='rfr', 
                                            type='number', 
                                            placeholder='Risk-free rate', 
                                            value=rfr, 
                                            step=0.01,
                                            ),

                                    html.P(children='Periods per year', className=style.params_p_style),

                                    dcc.Input(id='periods-per-year', 
                                            type='number', 
                                            placeholder='Periods per year', 
                                            value=periods_per_year, 
                                            step=1,
                                            min=1,
                                            ),

                                    # Tooltip for periods per year param
                                    dbc.Tooltip(
                                        "Assumes you're using daily price series. "
                                        "Change to 12 for monthly data or adjust accordingly. "
                                        ,
                                        target="periods-per-year",
                                        ),

                                    html.P(children='Rolling periods', className=style.params_p_style),  
                                
                                    dcc.Input(id='rolling-periods', 
                                            type='number', 
                                            placeholder='Rolling periods', 
                                            value=rolling_periods, 
                                            step=1, 
                                            min=1,
                                            )
                                ], xs=12, sm=12, md=12, lg=12, xl=6),

                                dbc.Col([
                                    html.P(children='Start Date', className=style.params_p_style),

                                    dcc.DatePickerSingle(
                                                id='start-date',
                                                max_date_allowed=date,
                                                initial_visible_month=date,
                                                date=date,
                                        ),

                                    html.P(children='End Date', className=style.params_p_style),
                                    
                                    dcc.DatePickerSingle(
                                        id='end-date',
                                        max_date_allowed=date,
                                        initial_visible_month=date,
                                        date=date),

                                    html.P(children='Main', className=style.params_p_style),  
                                
                                    dcc.Dropdown(id='main-asset', 
                                            value = '',
                                            ),

                                    html.P(children='Benchmark', className=style.params_p_style),  
                                
                                    dcc.Dropdown(id='benchmark-asset', 
                                            value = '',
                                            ),
                            ],xs=12, sm=12, md=12, lg=12, xl=6),

                            dbc.Row([

                                dbc.Col([

                                    dbc.Button(id='apply-changes-btn',
                                        children='Apply Changes',
                                        n_clicks=0,
                                        className='mt-3 mb-3 border border-light',
                                        color='primary'),

                                ],xs=12, sm=12, md=12, lg=12, xl=6)
                            ]),

                        ], className=style.dbc_row_style + ' bg-primary'),

                        dbc.Row([
                                dcc.Tabs(id='menu-tabs', value='compare', children=[
                                    dcc.Tab(label='Compare', value='compare', style=style.tab_style, selected_style=style.tab_selected_style),
                                    dcc.Tab(label='Returns', value='returns', style=style.tab_style, selected_style=style.tab_selected_style),
                                    dcc.Tab(id='benchmark-tab', label='Benchmark', value='benchmark', style=style.tab_style, selected_style=style.tab_selected_style),
                                    dcc.Tab(id='rolling-tab', label='Rolling', value='rolling', style=style.tab_style, selected_style=style.tab_selected_style),

                            ]), dbc.Tooltip(
                                        "Adjust main and benchmark params to your liking. "
                                        ,
                                        target="benchmark-tab",
                                        placement='bottom'
                                        ),

                                dbc.Tooltip(
                                        "Adjust rolling periods param to the appropriate timeframe. "
                                        ,
                                        target="rolling-tab",
                                        placement='bottom'
                                        ),
                        ], className='mt-3'),
                ])

    return display

def display_compare(data, initial_amount=initial_amount, rfr=rfr, periods_per_year=periods_per_year):
    '''
    Creates the display of compare module that includes index performance, drawdown, and metrics table.
    '''
    # Setup data
    prices = data.copy()
    assets = prices.columns.to_list()
    returns = qs.utils._prepare_returns(prices)
    # Create index evolution
    index = qs.utils.to_prices(returns, initial_amount)
    drawdown = qs.stats.to_drawdown_series(returns)

    # Index evolution
    index_traces = [go.Scatter(x=index.index, y=index[a], mode='lines', name=a) for a in assets]
    index_layout = style.scatter_charts_layout(title=f'Performance of {style.accounting_format(initial_amount)}')
    index_fig = go.Figure(index_traces, index_layout)
    
    # Drawdown
    drawdown_traces = [go.Scatter(x=drawdown.index, y=drawdown[a], mode='lines', name=a) for a in assets]
    drawdown_layout = style.scatter_charts_layout(title='Drawdown', ytickformat=',.1%')
    drawdown_fig = go.Figure(drawdown_traces, drawdown_layout)

    display = dbc.Row([

                    dbc.Row([
                        html.H3(f'Metrics', className='p-4'),
                        metricsTable.create_metrics_table(prices, periods_per_year, rfr)
                    ]),
                    
                    dbc.Col([
                        dcc.Graph(figure=index_fig)
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className='border mt-4'),

                    dbc.Col([
                        dcc.Graph(figure=drawdown_fig)
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className='border mt-4'),

    ], className=style.dbc_row_style)

    return display

def display_returns(prices, main_asset, round_to=2):
    '''
    Creates the display of returns module that includes monthly, eoy, and time series of returns.
    '''
    display = dbc.Row([

                    dbc.Row([
                        html.H3(f'Monthly Returns - {main_asset}', className='p-4'),
                        returnsModule.create_monthly_returns_table(prices, main_asset, round_to)
                    ]),
                    
                    dbc.Col([
                        dcc.Graph(figure=returnsModule.create_eoyReturns_bar(prices))
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className='border mt-4'),

                    dbc.Col([
                        dcc.Graph(figure=returnsModule.create_daily_returns_plot(prices, main_asset))
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className='border mt-4'),

            ],className=style.dbc_row_style)
                            
    return display

def display_benchmark(prices, main_asset, benchmark_asset, periods_per_year=periods_per_year, rfr=rfr):
    '''
    Creates the display of benchmark module that includes statistics table, scatter plot, correlation heatmap, and returns dist plot.
    '''
    display = dbc.Row([

                dbc.Row([

                    html.H3(f'Statistics {main_asset} vs {benchmark_asset}', className='p-4'),

                    benchmarkModule.create_statistics_table(prices, main_asset, benchmark_asset, periods_per_year, rfr)
                    ]),

                dbc.Col([
                    dcc.Graph(figure=benchmarkModule.create_scatter_plot(prices, main_asset, benchmark_asset))
                ], xs=12, sm=12, md=12, lg=12, xl=12, className='border mt-4'),

                dbc.Col([
                    dcc.Graph(figure=benchmarkModule.create_distribution_plot(prices, main_asset, benchmark_asset))
                ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4'),

                dbc.Col([
                    dcc.Graph(figure=benchmarkModule.create_correlation_heatmap(prices))
                ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4')
            
            ], className=style.dbc_row_style)

    return display

def display_rolling(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year):
    '''
    Creates the display of the rolling charts module.
    '''
    display = dbc.Row([

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Alpha"))
                    ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4'),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Beta"))
                    ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4'),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Sharpe"))
                    ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4'),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Sortino"))
                    ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4'),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Volatility"))
                    ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4'),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Correlation"))
                    ], xs=12, sm=12, md=12, lg=6, xl=6, className='border mt-4')

        ], className=style.dbc_row_style)
    
    return display