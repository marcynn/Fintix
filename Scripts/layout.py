import dash_bootstrap_components as dbc
from dash import html, dcc
import Scripts.style as style

# Navbar
navbar = dbc.NavbarSimple(id='nav-bar',
    children=[
        dbc.DropdownMenu(id='nav-dpdn',
            children=[
                dbc.DropdownMenuItem("Portfolio Optimization", header=False, className=None),
                dbc.DropdownMenuItem("Macro Dashboard", href="#", className=None),
            ],
            nav=True,
            in_navbar=True,
            label="Coming Soon",
            class_name = None
        ),
        dbc.NavItem(dbc.NavLink("About", href="#"), id='nav-item'),
    ],
    brand="Fintix",
    brand_href="#",
    color="dark",
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
                    dbc.Col([
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
                            multiple=True
                        ), 

                        html.Div(id='output-datatable'),

                    ],xs=12, sm=12, md=12, lg=6, xl=6),
                    
                    dbc.Col([
                        
                        # Download data-sample button. 

                        dbc.Button("Download Data Template", id="btn_csv", className='float-end', color='dark'),

                        dbc.Tooltip(
                            "Upload same template to explore or modify and upload your data. "
                            "Please use 'Date' as first column, followed by your choice of assets such as 'Asset1', 'Asset2', etc. "
                            "Possible to upload .xlsx, .xls, and .csv files."
                            ,
                            target="btn_xlsx",
                            ),

                        dcc.Download(id="download-dataframe-csv"),

                        html.Div(id='params')

                    ],xs=12, sm=12, md=12, lg=6, xl=6),
                
                ], className=style.dbc_row_style)

layout = dbc.Container([
    navbar,
    header,
    upload_file,

    html.Div(id='body')
    
], fluid=True)