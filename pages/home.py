import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import dash
import pandas as pd
from datetime import timedelta
import scripts.style as style
import scripts.tickerUniverse as tickUn
import scripts.utils as utils
import yfinance as yf
import sys

path = sys.path[0]

dash.register_page(__name__, path='/')

header = dbc.Row([
    
            dbc.Col([
                html.H1('Analytics at your fingertips. One sheet at a time.',  
                        className='text-center'
                        )
                    ], xs=12, sm=12, md=12, lg=12, xl=12),
        ], className=style.dbc_row_style)

upload_file = dbc.Row([
                    dbc.Col(id='upload-data-col',
                    children=[
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div(['Drag and Drop or ',
                                                html.A('Select Files'), 
                                                ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px',
                            },
                            # Allow multiple files to be uploaded
                            multiple=True),

                            dbc.Tooltip(
                                "Upload .csv file based on the data template. "
                                "Format is 'Date' as first column, followed by your choice of assets such as 'Asset1', 'Asset2', etc. ",
                                target="upload-data",
                            ),
                        
                        dbc.Spinner(
                            children=[html.Div(id='output-datatable')], 
                            size="lg", 
                            color="primary", 
                            type="border", 
                            fullscreen=False),

                    ],xs=12, sm=12, md=12, lg=6, xl=6),
                    
                    dbc.Col([
                        
                        dbc.Row([

                            dbc.Col([

                                # Download data-sample button 
                                dbc.Button("Download CSV Template", id="btn_csv", className='m-2', color='primary', n_clicks=0),
                                dcc.Download(id="download-dataframe-csv"),
            
                                # Download data from yfinance modal
                                dbc.Button("Download Yahoo Data", id="open-modal-btn", className='m-2', color='primary', n_clicks=0),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader(dbc.ModalTitle("Download asset prices from Yahoo Finance")),
                                        dbc.ModalBody(children=[
                                                                html.P('Assets'),
                                                                dcc.Dropdown(id='yf-asset-dpdn', options=tickUn.ticker_labels, value='TSLA', multi=True, className='m-2'), 
                                                                html.P('Date Period'),
                                                                dcc.Dropdown(id='yf-periods-dpdn', options=['5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max'], value='2y', className='m-2'),
                                                                ]),
                                        dbc.ModalFooter(
                                            html.Div([
                                                dbc.Button('Download csv', id='yf-download-btn', className="border border-light", color="primary", n_clicks=0),
                                                dcc.Download(id="yf-download-csv"),
                                                dbc.Button("Close", id="close-modal-btn", className="ms-2 border border-light", color="dark", n_clicks=0)
                                            ])
                                        ),
                                    ],
                                    id="modal",
                                    is_open=False,
                                    )
                            ], width={'offset':6})
                        ]),
                        
                        # Parameters spinner + div
                        dbc.Spinner(children=[html.Div(id='params')], 
                        size="lg", 
                        color="primary", 
                        type="border", 
                        fullscreen=False),
                    
                        ],xs=12, sm=12, md=12, lg=6, xl=6),
                
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
            [Input('submit-btn','n_clicks')])
def display_params(n_clicks):
    if n_clicks >= 1:
        params =  utils.create_params()
        return params, 'success'

# Update date picker to relevant dates
@callback(Output('start-date','date'),
            Output('end-date','date'),
            Output('start-date','min_date_allowed'),
            Output('start-date','max_date_allowed'),
            Output('end-date','min_date_allowed'),
            Output('end-date','max_date_allowed'),
            [Input('stored-data','data')])
def update_date_picker(data):
    data = utils.json_to_df(data)
    min_date = data.index.min()
    max_date = data.index.max()
    return min_date, max_date, min_date, max_date-timedelta(7), min_date+timedelta(7), max_date

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
def display_body(n_clicks, data, tab, all_assets, start_date, end_date, initial_amount, rfr, periods_per_year, rolling_periods, main_asset, benchmark_asset):
    data = utils.json_to_df(data)
    if n_clicks >= 1: # This means that we want to initialize the  with all assets at first. 
        try:
            data = data.loc[start_date:end_date] # Filter for start and end dates from date picker.
        except:
            print(f"Couldn't filter for date.")
        try:
            data = data[all_assets] # Filter for dropdown selected assets.
        except:
            print(f"Couldn't filter for assets.")

    if tab == 'compare':
        return utils.display_compare(data, initial_amount, rfr, periods_per_year)
    elif tab == 'returns':
        return utils.display_returns(data, main_asset)
    elif tab == 'benchmark':
        return utils.display_benchmark(data, main_asset, benchmark_asset, periods_per_year, rfr)
    elif tab == 'rolling':
        return utils.display_rolling(data, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year)