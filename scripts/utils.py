import pandas as pd
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import base64
import io
import datetime
from dateutil.relativedelta import relativedelta
import scripts.style as style
import scripts.tickerUniverse as tickUn

# Params
initial_amount = 1000
rfr = 0.02
periods_per_year = 252
rolling_periods = periods_per_year // 2

# Date lookback periods
lookback_periods = ['1w', 'mtd', '3m', '6m', 'ytd', '1y', '3y', '5y','max', 'covid crash', '2022 rate hikes']

def retrieve_date_from_lookback(data, lookback):

    start_date = pd.to_datetime(data.index[0])
    end_date = pd.to_datetime(data.index[-1])

    if lookback == '1w':
        start_date = end_date - relativedelta(weeks=1)
    elif lookback == 'mtd':
        start_date = datetime.datetime(end_date.year, end_date.month, 1)
    elif lookback == '3m':
        start_date = end_date - relativedelta(months=3)
    elif lookback == '6m':
        start_date = end_date - relativedelta(months=6)
    elif lookback == 'ytd':
        start_date = datetime.datetime(end_date.year, 1,1)
    elif lookback == '1y':
        start_date = end_date - relativedelta(years=1)
    elif lookback == '3y':
        start_date = end_date - relativedelta(years=3)
    elif lookback == '5y':
        start_date = end_date - relativedelta(years=5)
    elif lookback == 'covid crash':
        start_date = datetime.datetime(2020, 2, 20)
        end_date = datetime.datetime(2020, 3, 20)
    elif lookback == '2022 rate hikes':
        start_date = datetime.datetime(2022,2, 28)
        end_date = datetime.datetime(2022,12,31)
    return start_date, end_date

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
        Transforms data from JSON to PDF.
        Modify this function to accomodate for different data sources that have a slightly different data frame shape --> (No date index, date column not named 'Date', etc.)
        '''
        data = pd.DataFrame(data)
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

def filter_data(data, start_date, end_date, assets):
    '''
    Filters a dataFrame for a given start/end date as well as assets.
    '''
    try:
        filtered_data = data.loc[start_date:end_date][assets]
        print("Successfully filtered for start date, end date, and assets.")
    except:
        try:
            filtered_data = data.loc[start_date:end_date]
            print("Filtered only for start date and end date.")
        except:
            try:
                filtered_data = data[assets]
                print("Filtered only for assets.")
            except:
                print("Couldn't filter for neither dates nor assets.")
                return data
    return filtered_data

#------------------- Data Load-------------------
def parse_content(contents, filename):
    '''
    Parses the content of an uploaded csv file.
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
    Display table of an uploaded csv file.
    '''
    df = parse_content(contents, filename)

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

def upload_data():
    '''
    The main module by which the user can upload csv file and download csv data from Yahoo Finance.
    '''
    display = dbc.Col([
                        dbc.Row([
                            # Upload field
                            dbc.Col(
                                id='upload-data-col',
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
                                            placement='left')

                                ],xs=12, sm=12, md=12, lg=8, xl=8
                            ),

                            # Download data-sample button 
                            dbc.Col([
                                dbc.Button("Download CSV Template", id="btn_csv", className='mt-3', size='sm', color='primary', n_clicks=0),
                                dcc.Download(id="download-dataframe-csv"),
                            ],xs=12, sm=12, md=12, lg=2, xl=2),

                            # Download data from yfinance modal
                            dbc.Col([
                                dbc.Button("Download Yahoo Data", id="open-modal-btn", className='mt-3', size='sm', color='primary', n_clicks=0),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader(dbc.ModalTitle("Download asset prices from Yahoo Finance"), className='text-center'),
                                        dbc.ModalBody(children=[
                                                                html.P('Assets', className=style.params_p_style),
                                                                dcc.Dropdown(id='yf-asset-dpdn', options=tickUn.ticker_labels, value='TSLA', multi=True, className='m-2'), 
                                                                html.P('Date Period', className=style.params_p_style),
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
                            ],xs=12, sm=12, md=12, lg=2, xl=2)

                        ]),

                        # Data table
                        dbc.Row([
                            dbc.Spinner(
                            children=[html.Div(id='output-datatable', className='mt-3')], 
                            size="lg", 
                            color="primary", 
                            type="border", 
                            fullscreen=False),
                        ])

                    ],xs=12, sm=12, md=12, lg=6, xl=6, className='p-5')

    return display