import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import scripts.style as style
import dash
from dash import html, dcc, Input, Output, State, callback
import scripts.utils as utils
import datetime
from dateutil.relativedelta import relativedelta
from dash import dash_table

dash.register_page(__name__, name="DCA")

header = dbc.Row([
    
            dbc.Col([
                html.H3('Dollar Cost Average?',  
                        className='text-center text-warning'
                        ),
                
                dcc.Markdown('''
                            Dollar cost averaging is the process of buying an asset **recurrently** at specific time intervals.
                            The idea is to smooth volatility by averaging up or down consistently, taking emotions out of the equation.

                            You can test DCA strategy below vs investing all your money at once at the beginning.

                            **Note** that if you load multiple assets, DCA will be applied to and assessed relative to the equally weighted portfolio index.
                            ''', className='text-center')

                    ],xs=12, sm=12, md=12, lg=12, xl=12),

        ], className=style.dbc_row_style)

def create_dca_params(budget, initial_amount):

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
                                    html.P(children='Budget', className=style.params_p_style),

                                    dcc.Input(id='dca-budget',
                                            type='number',
                                            placeholder='1,000',
                                            value=budget,
                                            min=1,
                                            ),

                                    html.P(children='Initial amount', className=style.params_p_style),

                                    dcc.Input(id='dca-initial-amount',
                                            type='number',
                                            placeholder='1,000',
                                            value=initial_amount,
                                            min=0,
                                            ),

                                    html.Div(id='dca-input-validation', className='text-danger mt-2'),

                                    html.P(children='Buy every x Days', className=style.params_p_style),

                                    dcc.Input(id='dca-interval',
                                            type='number',
                                            placeholder='30 days',
                                            value=30,
                                            min=10,
                                            ),

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
                                            
                                        dbc.Col([

                                            html.P(children='End Date', className=style.params_p_style),

                                            dcc.DatePickerSingle(
                                                        id='end-date',
                                                        max_date_allowed=date,
                                                        initial_visible_month=date,
                                                        date=date
                                                    ),
                                                ],xs=12, sm=12, md=12, lg=6, xl=6),

                                        dbc.Col([

                                            html.P(children='Lookback Period', className=style.params_p_style ),

                                            dcc.Dropdown(id='lookback-dpdn',
                                                        options=[{'label':i, 'value':i} for i in utils.lookback_periods],
                                                        value='max'),

                                            html.P(id='date-validation-p', className='text-danger mt-2')

                                        ],xs=12, sm=12, md=12, lg=6, xl=6)
                                        
                                    ]),
                                ]),

                            dbc.Row([

                                dbc.Col([

                                    dbc.Button(id='dca-apply-changes-btn',
                                        children='Apply Changes',
                                        n_clicks=0,
                                        className='mt-3 mb-3 border border-light',
                                        color='primary'),

                                ],xs=12, sm=12, md=12, lg=12, xl=6)
                            ]),
                        ])
                ])

    return display

def create_ew_portfolio_index(prices, budget, return_contribution=False):
    try:
        prices.set_index('Date', inplace=True) # In case Date column was not set as index
        prices.index = pd.to_datetime(prices.index)
    except:
        pass
    
    prices = prices.resample('D').ffill()
    returns = prices.pct_change()
    noa = returns.shape[1] # number of assets
    weights = np.repeat(1/noa, noa)
    index = returns + 1
    index.iloc[0] = budget / noa
    aba = index.cumprod() # amount by asset
    index = aba.sum(axis=1) 
    
    if return_contribution:
        # Return contribution
        rba = aba.iloc[-1] / aba.iloc[0] # returns by asset
        contribution = rba * weights
        
        return index, contribution
    else:
        return index

def create_dca_index(prices, budget, starting_amount, days):
    
    cashflow = []
    
    try:
        prices.set_index('Date', inplace=True) # In case Date column was not set as index
        prices.index = pd.to_datetime(prices.index)
    except:
        pass
    
    prices = prices.resample('D').ffill()
    returns = prices.pct_change()
    
    start_date = returns.index[0]
    end_date = returns.index[-1]
    rebalancing_periods = []
    
    # Retrieve rebalancing periods
    i = start_date
    while i < end_date:
        if i == start_date:
            rebalancing_periods.append(i)
        i = i + relativedelta(days=days)
        rebalancing_periods.append(i)
        
    if rebalancing_periods[-1] > end_date:
        rebalancing_periods.pop()
        
    noa = returns.shape[1]
    n_rebalancing_periods = len(rebalancing_periods) - 1 if starting_amount != 0 else len(rebalancing_periods)
    rebalancing_payment = ((budget - starting_amount) / n_rebalancing_periods ) / noa
        
    # Create DCA indices
    indices = []
    for n in rebalancing_periods:
        if n == start_date:
            inflow = (starting_amount / noa) if starting_amount != 0 else rebalancing_payment
        else:
            inflow = rebalancing_payment
                
        index = returns.loc[n:].copy() + 1
        index.iloc[0] = inflow
        index = index.cumprod()
        indices.append(index)
        
        cashflow.append(index.iloc[0]) # Cashflow log
        
    # Concat all indices into one index
    concat_index = pd.concat(indices, axis=1)
    unique_assets = concat_index.columns.unique()
    aba = []
    for a in unique_assets:
        aba.append(pd.DataFrame(concat_index[a].sum(axis=1), columns=[a]))
        
    index = pd.concat(aba, axis=1).sum(axis=1)
        
    # Clean cashflow log
    cashflow = pd.concat(cashflow, axis=1).transpose()
    cashflow.index.name = "Date"
    cashflow.index = cashflow.index.strftime("%m/%d/%Y")
    cashflow['Total'] = cashflow.sum(axis=1)
    cashflow = cashflow.round(2)
    cashflow.loc['Total'] = cashflow.sum()
    
    return index, cashflow

def create_dca_body(prices, budget, starting_amount, days):
    ew_index = create_ew_portfolio_index(prices, budget)
    dca_index, cashflow = create_dca_index(prices, budget, starting_amount, days)
    concat = pd.concat([ew_index, dca_index], axis=1)
    name_base_case = "EW Index" if len(prices.columns) > 1 else prices.columns[0]
    concat.columns = [name_base_case + ' base','DCA']
    
    # Index Plot
    traces = [go.Scatter(x=concat.index, y=concat[i], mode='lines', name=i) for i in concat.columns]
    layout = style.scatter_charts_layout(title=f'Investing {style.accounting_format(budget)} at T0 vs DCAing every {days} days')
    figure = go.Figure(traces, layout)


    # Cashflow table 
    data = cashflow.reset_index().to_dict('records')
    columns = [dict(id=i, name=i, type='numeric') if i!='Year' else dict(id=i, name=i) for i in cashflow.reset_index().columns]

    dt = dash_table.DataTable(data,
                            columns,
                            fixed_columns={'headers':True, 'data':1},
                            sort_action='native',
                            style_as_list_view=False,
                            style_table={'minWidth':'100%',
                                        'minHeight':150},
                            style_data=style.style_data,
                            style_header=style.style_header,
                            style_cell={
                                'textAlign': 'center',
                                'minWidth': '180px', 
                                'width': '30px',
                                'padding':'5px'})


    display = dbc.Row([

                    dbc.Col([
                        dcc.Graph(figure=figure),
                    ],xs=12, sm=12, md=12, lg=12, xl=12, className=style.dbc_col_style),

                    dbc.Col([
                        dbc.Button(
                            "Cashflow",
                            id="cashflow-collapse-btn",
                            className="m-3",
                            color="warning",
                            n_clicks=0,
                        ),
                        dbc.Collapse(
                            html.Div(children=dt),
                            id="cashflow-collapse-table",
                            is_open=False,
                        )
                    ],xs=12, sm=12, md=12, lg=12, xl=12),
                ])

    return display

#### Create layout
layout = dbc.Container([

    header,

    dbc.Row([

        utils.upload_data(),

        dbc.Col([
                html.Div(id='dca-params')
        ],xs=12, sm=12, md=12, lg=6, xl=6),

        html.Div([
        ], id='dca-body')

    ], className=style.dbc_row_style),
    
],fluid=True)

@callback(Output('dca-params', 'children'),
            [Input('submit-btn','n_clicks')])
def display_params(n):
    if n >= 1:
        return create_dca_params(200000,20000)

@callback(Output('dca-input-validation', 'children'),
        Output('dca-initial-amount', 'value'),
        [Input('dca-initial-amount','value'),
        Input('dca-budget','value')
        ])
def validate_input(initial_amount, budget):
    if initial_amount > budget:
        return 'Initial amount cannot be higher than the budget.', 0

@callback(Output('dca-body','children'),
            [Input('dca-apply-changes-btn', 'n_clicks'),
            Input('stored-data','data'),],
            [State('assets-dpdn', 'value'),
            State('start-date','date'),
            State('end-date','date'),
            State('dca-budget','value'),
            State('dca-initial-amount','value'),
            State('dca-interval','value'),
            ])
def display_body(n, data, assets, start_date, end_date, budget, initial_amount, dca_interval,):
    data = utils.json_to_df(data)
    data = data.dropna()
    data = utils.filter_data(data, start_date, end_date, assets)
    return create_dca_body(data, budget, initial_amount, dca_interval)

@callback(
    Output("cashflow-collapse-table", "is_open"),
    [Input("cashflow-collapse-btn", "n_clicks")],
    [State("cashflow-collapse-table", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open