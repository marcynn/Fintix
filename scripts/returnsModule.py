import pandas as pd
import quantstats as qs
from dash import dash_table
from dash.dash_table import FormatTemplate
import plotly.graph_objects as go
import scripts.style as style
import scripts.utils as utils

def create_monthly_returns_table(prices, main_asset, round_to=2):
    returns = qs.utils._prepare_returns(prices)
    percentage = FormatTemplate.percentage(round_to)

    # Prepare returns
    df = returns.copy()
    df.reset_index(inplace=True)
    df['Month'] = (df['Date']).dt.month_name().str[:3] # Create Month column by taking first three letters from Month name
    df['Year'] = df['Date'].dt.year
    df = df.drop('Date',axis=1)
    monthly_grouped_rets = df.groupby([df['Year'], df['Month']]).apply(qs.stats.comp)
    monthly_grouped_rets.reset_index(inplace=True)
    monthly_grouped_rets = monthly_grouped_rets.pivot_table(values=main_asset,index='Year',columns='Month')
    
    # Sort unique months in proper order
    months_mapping = utils.months_mapping

    unique_months = [] 
    for month in months_mapping.values():
        if month in monthly_grouped_rets.columns:
            unique_months.append(month)
    monthly_grouped_rets = monthly_grouped_rets[unique_months] # Re-order monthly returns columns to the proper order    

    # Create yearly / total returns and merge them with monthly returns table
    yearly_grouped_rets = df[['Year',main_asset]].groupby(df['Year']).apply(qs.stats.comp).drop('Year',axis=1).rename(columns={main_asset:'Total'})
    grouped_rets = pd.merge(monthly_grouped_rets, yearly_grouped_rets, left_on=monthly_grouped_rets.index, right_on=yearly_grouped_rets.index).rename(columns={'key_0':'Year'})
    grouped_rets.sort_values('Year', ascending=False, inplace=True)

    data = grouped_rets.to_dict('records')
    columns = [dict(id=i, name=i, type='numeric', format=percentage) if i!='Year' else dict(id=i, name=i) for i in grouped_rets.columns]

    dt = dash_table.DataTable(data, 
                            columns, 
                            fixed_columns={'headers':True, 'data':1}, 
                            sort_action='native',
                            style_as_list_view=True,
                            style_table={'minWidth':'100%',
                                        'minHeight':150},
                            style_data=style.style_data,
                            style_header=style.style_header,
                            style_cell={
                                'textAlign': 'center',
                                'minWidth': '80px', 
                                'width': '80px',
                                'padding':'5px'},
                            style_data_conditional=[{'if': {'filter_query': f'{{{col}}} < 0',
                                                            'column_id': col},
                                                            'color':style.red} for col in grouped_rets.columns] +                          
                                                    [{'if': {'filter_query': f'{{{col}}} > 0',
                                                            'column_id': col},
                                                    'color':style.green}
                                                    for col in grouped_rets.columns] +
                                                    [{'if': {'column_id': 'Year'},
                                                    'color':'white'}])
                                                    
    return dt

def create_eoyReturns_bar(data):
    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)
    eoy_returns = qs.utils.aggregate_returns(returns, 'year')
    assets = eoy_returns.columns
    traces = [go.Bar(x=eoy_returns.index,
                    y=eoy_returns[i],
                    name=i,
                    text=(eoy_returns[i]*100).apply(lambda x: '{0:.2f}%'.format(x)),
                    hoverinfo='text') for i in assets]

    layout = go.Layout(style.scatter_charts_layout(title=f'EOY Returns', ytickformat=',.0%'))
    fig = go.Figure(traces, layout)
    fig.update_layout(height=400)
    fig.layout.xaxis.tickvals = eoy_returns.index # Make xaxis dates as categorical instead of continuous
    
    return fig

def create_daily_returns_plot(data, main_asset):
    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)

    traces = [go.Scatter(x=returns.index, y=returns[main_asset], mode='lines', name=a) for a in [main_asset]]

    layout = style.scatter_charts_layout(title=f'Returns Series {main_asset}',  ytickformat=',.1%')

    fig = go.Figure(traces, layout)
    fig.update_layout(height=400)
    
    return fig