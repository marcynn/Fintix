import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import dash
import plotly.graph_objs as go
import pandas as pd
from datetime import timedelta
import datetime
import scripts.style as style
import scripts.utils as utils
import scripts.metricsTable as metricsTable
import scripts.returnsModule as returnsModule
import scripts.benchmarkModule as benchmarkModule
import scripts.rollingModule as rollingModule
import yfinance as yf
import quantstats as qs
import sys

path = sys.path[0]

dash.register_page(__name__)

header = dbc.Row([
    
            dbc.Col([
                html.H3('Analytics at your fingertips. One sheet at a time.',  
                        className='text-center text-warning'
                        ),

                dcc.Markdown('''
                            Performance and risk analytics dashboard for comparing investment strategies and assets.

                            **Load prices once, adjust parameters and analyze on the fly.**
                            ''', className='text-center')

                    ],xs=12, sm=12, md=12, lg=12, xl=12),
        ], className=style.dbc_row_style)

upload_file = dbc.Row([
    
                    utils.upload_data(), 

                    # Parameters spinner + div
                    dbc.Col([
                        dbc.Spinner(children=[html.Div(id='params')], 
                                size="lg", 
                                color="primary", 
                                type="border", 
                                fullscreen=False),

                    ],xs=12, sm=12, md=12, lg=6, xl=6, className='p-5'),

                    # Menu tabs
                    html.Div(id='menu-tabs-div')
                    
    ], className=style.dbc_row_style)

layout = dbc.Container([
    header,
    upload_file,
    dbc.Spinner(children=[html.Div(id='body')], 
                                size="lg", 
                                color="primary", 
                                type="border", 
                                fullscreen=False),
], fluid=True)

def create_params(initial_amount=utils.initial_amount, rfr=utils.rfr, periods_per_year=utils.periods_per_year, rolling_periods=utils.rolling_periods):

    date = datetime.date.today() # Used in dates params for date picker

    display = html.Div([

                        html.H5('Adjust Parameters', className=style.h5_style),

                        dbc.Row([

                                dbc.Row([
                                    
                                    dbc.Col([

                                        html.P(children='Filter for Asset', className=style.params_p_style),

                                        dcc.Dropdown(id='assets-dpdn',
                                                        multi=True,
                                                        )
                                            ], className='mb-3')
                                    ]),

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
                                ], xs=12, sm=12, md=12, lg=12, xl=4),

                                dbc.Col([

                                    dbc.Row([

                                        dbc.Col([

                                            html.P(children='Start Date', className=style.params_p_style),

                                            dcc.DatePickerSingle(
                                                        id='start-date',
                                                        max_date_allowed=date,
                                                        initial_visible_month=date,
                                                        date=date,
                                                    ),
                                                ],xs=12, sm=12, md=12, lg=6, xl=6),
                                            
                                            dbc.Tooltip(
                                                "To change manually, please pick 'max' as your lookback first. ",
                                                target="start-date",
                                                placement='top',
                                                ),
                                            
                                        dbc.Col([

                                            html.P(children='End Date', className=style.params_p_style),

                                            dcc.DatePickerSingle(
                                                        id='end-date',
                                                        max_date_allowed=date,
                                                        initial_visible_month=date,
                                                        date=date
                                                    ),
                                                ],xs=12, sm=12, md=12, lg=6, xl=6)
                                        ]),

                                    dbc.Row([

                                        dbc.Col([

                                                html.P(children='Main', className=style.params_p_style),

                                                dcc.Dropdown(id='main-asset',
                                                        value = '',
                                                        ),
                                                ],xs=12, sm=12, md=12, lg=6, xl=6),

                                        dbc.Col([

                                                html.P(children='Benchmark', className=style.params_p_style),

                                                dcc.Dropdown(id='benchmark-asset',
                                                        value = '',
                                                        ),
                                                ],xs=12, sm=12, md=12, lg=6, xl=6),
                                        ]),

                                        dbc.Row([

                                            dbc.Col([

                                                html.P(children='Lookback Period', className=style.params_p_style ),

                                                dcc.Dropdown(id='lookback-dpdn',
                                                            options=[{'label':i, 'value':i} for i in utils.lookback_periods],
                                                            value='max'),

                                                html.P(id='date-validation-p', className='text-danger mt-2')

                                            ],xs=12, sm=12, md=12, lg=6, xl=6)
                                        ])

                            ],xs=12, sm=12, md=12, lg=12, xl=8),

                            dbc.Row([

                                dbc.Col([

                                    dbc.Button(id='apply-changes-btn',
                                        children='Apply Changes',
                                        n_clicks=0,
                                        className='mt-3 mb-3 border border-light',
                                        color='primary'),

                                ],xs=12, sm=12, md=12, lg=12, xl=6)
                            ]),

                        ]),
                ])

    return display

def display_tabs():
    display = dbc.Row([
        
                    dcc.Tabs(id='menu-tabs',
                            value='compare',
                            children=[
                                dcc.Tab(label='TL;DA', value='tlda', style=style.tab_style, selected_style=style.tab_selected_style),
                                dcc.Tab(label='Compare', value='compare', style=style.tab_style, selected_style=style.tab_selected_style),
                                dcc.Tab(label='Returns', value='returns', style=style.tab_style, selected_style=style.tab_selected_style),
                                dcc.Tab(id='benchmark-tab', label='Benchmark', value='benchmark', style=style.tab_style, selected_style=style.tab_selected_style),
                                dcc.Tab(id='rolling-tab', label='Rolling', value='rolling', style=style.tab_style, selected_style=style.tab_selected_style),

                        ]), dbc.Tooltip(
                            "Adjust main and benchmark params to your liking. ",
                            target="benchmark-tab",
                            placement='bottom'
                            ),

                    dbc.Tooltip(
                            "Adjust rolling periods param to the appropriate timeframe. ",
                            target="rolling-tab",
                            placement='bottom'
                            ),
                    ])
    return display

def retrieve_summary_text(prices, lookback, rfr=utils.rfr, periods_per_year=utils.periods_per_year):
    '''
    Retrieves summary text containing a brief summary of top / worst performances for a given lookback period.
    '''
    try:
        start_date, end_date = utils.retrieve_date_from_lookback(prices, lookback)
        prices = prices.loc[start_date:end_date]
        returns = qs.utils._prepare_returns(prices)

        start_date = str(prices.index[0])[:10]
        end_date = str(prices.index[-1])[:10]
        comp = qs.stats.comp(returns)
        max_return = round(comp.max() * 100 , 2)
        min_return = round(comp.min() * 100 , 2)

        sharpe_ratio = round(qs.stats.sharpe(returns, rf=rfr, periods=periods_per_year, annualize=True),2)
        volatility = round(qs.stats.volatility(returns, periods=periods_per_year, annualize=True)*100, 2)

        display = html.Div(
                            children=
                                    dcc.Markdown(
                                        f'''
                                        ###### Best {comp.idxmax()} {volatility.idxmin()} {sharpe_ratio.idxmax()}

                                        **{lookback.upper()}** period - {start_date} to {end_date}:

                                        * **Performance**: 
                                        {comp.idxmax()} best at {max_return}%. 
                                        {comp.idxmin()} worst at {min_return}%.

                                        * **Volatility**: 
                                        {volatility.idxmin()} best at {volatility.min()}%.
                                        {volatility.idxmax()} worst at {volatility.max()}%.

                                        * **Risk-adjusted Performance (Sharpe)**: 
                                        {sharpe_ratio.idxmax()} best at {sharpe_ratio.max()}.
                                        {sharpe_ratio.idxmin()} worst at {sharpe_ratio.min()}.
                                        '''
                                    )
                            )
    except:
        display = html.Div(children=
                                    dcc.Markdown(
                                        f'''
                                        Couldn't retrieve summary for **{lookback.upper()}** period.
                                        '''
                                    )
                                )
    return display

def retrieve_all_summary_texts(prices, rfr=utils.rfr, periods_per_year=utils.periods_per_year):
    '''
    Retrieves all summary texts for a list of lookbacks.
    '''
    all_texts = [retrieve_summary_text(prices, lookback, rfr, periods_per_year) for lookback in utils.lookback_periods]

    display = dbc.Row([
                        html.H5(children="Too Long; Didn't Analyze", className=style.h5_style)
                    ] +
                [
                dbc.Col(i, 
                        className=style.dbc_col_style + ' border-warning p-2 m-1',
                        xs=12, sm=12, md=12, lg=2, xl=2) for i in all_texts

                ], className=style.dbc_row_style)
    return display

def display_compare(prices, initial_amount=utils.initial_amount, rfr=utils.rfr, periods_per_year=utils.periods_per_year):
    '''
    Creates the display of compare module that includes index performance, drawdown, and metrics table.
    '''
    # Setup data
    assets = prices.columns.to_list()
    returns = qs.utils._prepare_returns(prices)
    # Create index evolution
    index = qs.utils.to_prices(returns, initial_amount)
    drawdown = qs.stats.to_drawdown_series(returns)

    # Index evolution
    index_traces = [go.Scatter(x=index.index, y=index[a], mode='lines', name=a) for a in assets]
    index_layout = style.scatter_charts_layout(title=f'Performance of {style.accounting_format(initial_amount)}')
    index_fig = go.Figure(index_traces, index_layout)
    index_fig = style.add_range_slider(index_fig)

    # Drawdown
    drawdown_traces = [go.Scatter(x=drawdown.index, y=drawdown[a], mode='lines', name=a) for a in assets]
    drawdown_layout = style.scatter_charts_layout(title='Drawdown', ytickformat=',.1%')
    drawdown_fig = go.Figure(drawdown_traces, drawdown_layout)
    drawdown_fig = style.add_range_slider(drawdown_fig)

    display = dbc.Row([

                    dbc.Col([
                        html.H5(f'Metrics', className=style.h5_style),
                        html.Div([metricsTable.create_metrics_table(prices, periods_per_year, rfr)], className='mb-4')
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=index_fig)
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=drawdown_fig)
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

    ], className=style.dbc_row_style)

    return display

def display_returns(prices, main_asset, round_to=2):
    '''
    Creates the display of returns module that includes monthly, eoy, and time series of returns.
    '''
    display = dbc.Row([

                    dbc.Col([
                        html.H5(f'Monthly Returns - {main_asset}', className=style.h5_style),
                        html.Div([returnsModule.create_monthly_returns_table(prices, main_asset, round_to)],className='mb-4')
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=returnsModule.create_eoyReturns_bar(prices))
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=returnsModule.create_daily_returns_plot(prices, main_asset))
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=returnsModule.create_returns_box_plot(prices))
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style)

            ], className=style.dbc_row_style)

    return display

def display_benchmark(prices, main_asset, benchmark_asset, periods_per_year=utils.periods_per_year, rfr=utils.rfr):
    '''
    Creates the display of benchmark module that includes statistics table, scatter plot, correlation heatmap, and returns dist plot.
    '''
    display = dbc.Row([

                dbc.Col([

                    html.H5(f'Statistics - {main_asset} vs {benchmark_asset}', className=style.h5_style),

                    benchmarkModule.create_statistics_table(prices, main_asset, benchmark_asset, periods_per_year, rfr)
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                dbc.Col([
                    dcc.Graph(figure=benchmarkModule.create_scatter_plot(prices, main_asset, benchmark_asset))
                ], xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                dbc.Col([
                    dcc.Graph(figure=benchmarkModule.create_distribution_plot(prices, main_asset, benchmark_asset))
                ], xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style),

                dbc.Col([
                    dcc.Graph(figure=benchmarkModule.create_correlation_heatmap(prices))
                ], xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style)

            ], className=style.dbc_row_style)

    return display

def display_rolling(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year):
    '''
    Creates the display of the rolling charts module.
    '''
    display = dbc.Row([

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Alpha"))
                    ],xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Beta"))
                    ],xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Sharpe"))
                    ],xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Sortino"))
                    ],xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Volatility"))
                    ],xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style),

                    dbc.Col([
                        dcc.Graph(figure=rollingModule.create_rolling_metrics(prices, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, "Correlation"))
                    ],xs=12, sm=12, md=12, lg=6, xl=6, className=style.dbc_col_style)
                    
        ], className=style.dbc_row_style)

    return display


#-------------------Callbacks-------------------
# Download data sample
@callback(Output("download-dataframe-csv", "data"),
                Input("btn_csv", "n_clicks"),
                prevent_initial_call=True)
def func(n_clicks):
    if n_clicks >=1:
        df = pd.read_csv(path+'/data/sample-data.csv')
        return dcc.send_data_frame(df.to_csv, "sample-data.csv", index=False)

# Open/Close Yahoo Modal
@callback(
    Output("modal", "is_open"),
    [Input("open-modal-btn", "n_clicks"), Input("close-modal-btn", "n_clicks")],
    [State("modal", "is_open")])
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# Download Yahoo data
@callback(Output("yf-download-csv", "data"),
                [Input("yf-download-btn", "n_clicks")],
                [State('yf-asset-dpdn', 'value'),
                State('yf-periods-dpdn','value')],
                prevent_initial_call=True)
def download_yahoo_data(n_clicks, assets, period):
    if n_clicks >=1:
        df = yf.download(assets, period=period)['Adj Close']
        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)
            df.columns = [assets] if type(assets) != list else assets
        return dcc.send_data_frame(df.to_csv, "yf-data.csv", index=True)
    
# Store uploaded data
@callback(Output('output-datatable', 'children'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),
            State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    '''
    Updates the output of uploaded Excel file and stores data.
    '''
    if list_of_contents is not None:
        children = [
            utils.display_uploaded_file(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

# Display parameters
@callback(Output('params','children'),
            Output('submit-btn','color'),
            Output('menu-tabs-div', 'children'),
            [Input('submit-btn','n_clicks')])
def display_params(n_clicks):
    if n_clicks >= 1:
        params =  create_params()
        return params, 'success', display_tabs()

# Update date picker to relevant dates
@callback(Output('start-date','date'),
            Output('end-date','date'),
            Output('start-date','min_date_allowed'),
            Output('start-date','max_date_allowed'),
            Output('end-date','min_date_allowed'),
            Output('end-date','max_date_allowed'),
            Output('start-date','disabled'),
            Output('end-date','disabled'),
            Output('date-validation-p', 'children'),
            [Input('stored-data','data'),
            Input('lookback-dpdn', 'value'),
            Input('assets-dpdn','value')
            ])
def update_date_picker(data, lookback, assets):
    data = utils.json_to_df(data)
    data = data[assets].dropna()
    min_date = data.index[0]
    max_date = data.index[-1]
    start_date, end_date = utils.retrieve_date_from_lookback(data, lookback)

    disable_start_date = True
    disable_end_date = True

    if lookback == 'max':
        disable_start_date = False
        disable_end_date = False
    
    if start_date < min_date or end_date > max_date:
        date_validation = 'Lookback period is not within the date range of loaded data.'
    else:
        date_validation = None
        
    return start_date, end_date, min_date, max_date-timedelta(7), min_date+timedelta(7), max_date, disable_start_date, disable_end_date, date_validation

# Update assets filter dropdown
@callback(Output('assets-dpdn','options'),
            Output('assets-dpdn','value'),
            [Input('stored-data','data')])
def update_filter_dropdown(data):
    data = utils.json_to_df(data)
    options = [{'label':i, 'value':i} for i in data.columns]
    return options, data.columns

# Update main asset and benchmark dropdowns based on filtered asset
@callback(Output('main-asset','options'),
            Output('benchmark-asset','options'),
            Output('main-asset','value'),
            Output('benchmark-asset','value'),
            [Input('assets-dpdn','value')])
def update_main_bench_dropdowns(filtered_assets):
    try:
        main_asset = filtered_assets[0]
    except:
        main_asset = ''
    try:
        benchmark_asset = filtered_assets[1]
    except:
        benchmark_asset = ''

    options = [{'label':i, 'value':i} for i in filtered_assets]
    return options, options, main_asset, benchmark_asset

# Update body
@callback(Output('body','children'),
            [Input('apply-changes-btn', 'n_clicks'),
            Input('stored-data','data'),
            Input('menu-tabs','value')],
            [State('assets-dpdn', 'value'),
            State('start-date','date'),
            State('end-date','date'),
            State('initial-amount','value'),
            State('rfr','value'),
            State('periods-per-year','value'),
            State('rolling-periods','value'),
            State('main-asset','value'),
            State('benchmark-asset','value'),
            ])
def display_body(n_clicks, data, menu, assets, start_date, end_date, initial_amount, rfr, periods_per_year, rolling_periods, main_asset, benchmark_asset):
    data = utils.json_to_df(data)
    
    if n_clicks >= 1:
        filtered_data = utils.filter_data(data, start_date, end_date, assets)
        filtered_data = filtered_data.dropna()

    if menu == 'tlda':
        return retrieve_all_summary_texts(data, rfr, periods_per_year)
    elif menu == 'compare':
        return display_compare(filtered_data, initial_amount, rfr, periods_per_year)
    elif menu == 'returns':
        return display_returns(filtered_data, main_asset)
    elif menu == 'benchmark':
        return display_benchmark(filtered_data, main_asset, benchmark_asset, periods_per_year, rfr)
    elif menu == 'rolling':
        return display_rolling(filtered_data, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year)


