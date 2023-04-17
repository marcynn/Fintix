import dash_bootstrap_components as dbc
from dash import html, dcc
import scripts.style as style
import scripts.tickerUniverse as tickUn

# Navbar
navbar = dbc.NavbarSimple(id='nav-bar',
    # children=[
    #     dbc.DropdownMenu(id='nav-dpdn',
    #         children=[
    #             dbc.DropdownMenuItem("Portfolio Optimization", header=False, className=None),
    #             dbc.DropdownMenuItem("Macro Dashboard", href="#", className=None),
    #         ],
    #         nav=True,
    #         in_navbar=True,
    #         label="Coming Soon",
    #         class_name = None
    #     ),
    #     dbc.NavItem(dbc.NavLink("About", href="#"), id='nav-item'),
    # ],
    brand="Fintix",
    brand_href="#",
    color="primary",
    dark=True,
    brand_style= {'fontSize':30},
    fluid=True                  
)

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
    navbar,
    header,
    upload_file,
    dbc.Spinner(children=[html.Div(id='body')], 
                size="lg", 
                color="primary", 
                type="border", 
                fullscreen=False),
    
], fluid=True)