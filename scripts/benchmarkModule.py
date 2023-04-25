import quantstats as qs
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import scripts.style as style
import plotly.figure_factory as ff
from collections import OrderedDict
from dash import dash_table
from dash.dash_table import FormatTemplate

def create_scatter_plot(data, main_asset, benchmark_asset):
    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)
    traces = [go.Scatter(x=returns[main_asset], 
                    y=returns[benchmark_asset],
                    mode='markers+text',
                    marker=dict(size=12,
                                symbol='pentagon',
                                line=dict(width=2)
                                )
                            )
                        ]
    layout = style.scatter_charts_layout(f"Scatter Plot", 
                                    xtickformat= ',.1%', 
                                    ytickformat=',.1%', 
                                    xaxisTitle=main_asset, 
                                    yaxisTitle=benchmark_asset)

    fig = go.Figure(traces, layout)

    return fig

def create_distribution_plot(data, main_asset, benchmark_asset):
    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)

    if main_asset == benchmark_asset: # In case we loaded one asset
        hist_data = [(round(returns.iloc[:,0],4)).to_list()]
        group_labels = [main_asset]
    else:
        hist_data = [(round(returns[main_asset],4) - 0.02).to_list(), (round(returns[benchmark_asset],4) - 0.02).to_list()]
        group_labels = [main_asset, benchmark_asset]

    bin_size = 0.01
    fig = ff.create_distplot(hist_data, group_labels, bin_size=bin_size, histnorm='')
    fig.update_layout(title=dict(text=f'<b>Returns Distribution</b>',
                                font=dict(color=style.main_theme_color)),
                    title_x=0.5,
                    font=dict(size=15),
                    hoverlabel=dict(font_size=15),
                    template=style.chart_templates,
                    paper_bgcolor=style.secondary_theme_color, 
                    plot_bgcolor=style.secondary_theme_color,
                    legend=dict(y=-0.2))

    return fig

def create_correlation_heatmap(data):
    # Reference - https://stackoverflow.com/questions/66572672/correlation-heatmap-in-plotly
    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)

    corr = returns.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool)) # Remove top triangle
    df_mask = round(corr.mask(mask),2) 

    fig = ff.create_annotated_heatmap(z=df_mask.to_numpy(), 
                        x=df_mask.columns.tolist(),
                        y=df_mask.columns.tolist(),
                        #font_colors=['black'],  
                        #colorscale='GnBu',
                        zmin=-1,
                        zmax=1,
                        showscale=True,
                        ygap=1, 
                        xgap=1,
                        )

    fig.update_xaxes(side="bottom")
    fig.update_layout(title=dict(text='<b>Correlation Heatmap</b>',
                                font=dict(color=style.main_theme_color)),
                        title_x=0.5,
                        font=dict(size=15),
                        hoverlabel=dict(font_size=15),
                        xaxis_showgrid=False,
                        yaxis_showgrid=False,
                        xaxis_zeroline=False,
                        yaxis_zeroline=False,
                        yaxis_autorange='reversed',
                        template=style.chart_templates,
                        paper_bgcolor=style.secondary_theme_color, 
                        plot_bgcolor=style.secondary_theme_color,
                        legend=dict(y=-0.2))

    # Get rid of NaN values
    for i in range(len(fig.layout.annotations)):
        if fig.layout.annotations[i].text == 'nan':
            fig.layout.annotations[i].text = ""

    return fig

def create_statistics_table(data, main_asset, benchmark_asset, periods_per_year, rfr, round_to=2):

    percentage = FormatTemplate.percentage(round_to)

    # Create statistics table
    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)
    percentage = FormatTemplate.percentage(round_to) 

    first_date = data.index.min().strftime("%m/%d/%Y")
    last_date = data.index.max().strftime("%m/%d/%Y")

    greeks = qs.stats.greeks(returns[main_asset], returns[benchmark_asset], periods=periods_per_year, prepare_returns=False)
    round_to = 3

    try:
        correlation = round(returns[main_asset].corr(returns[benchmark_asset]),round_to)
    except:
        correlation = np.nan
    try:
        alpha = round(greeks.loc['alpha'], round_to)
    except:
        alpha =np.nan
    try:
        beta = round(greeks.loc['beta'], round_to)
    except:
        beta = np.nan
    try:
        r_squared = round(qs.stats.r_squared(returns[main_asset], returns[benchmark_asset], prepare_returns=False), round_to)
    except:
        r_squared = np.nan
    try:
        treynor = round((qs.stats.comp(returns[main_asset]) - rfr) / beta, round_to)
    except:
        treynor = np.nan

    try:
        information_ratio = round(qs.stats.information_ratio(returns[main_asset], returns[benchmark_asset], prepare_returns=False), round_to)
    except:
        information_ratio = np.nan

    data = OrderedDict(
        [   
            ('First Date', [first_date]),
            ('Last Date', [last_date]),
            ('Correlation', [correlation]),
            ('Alpha (excl. rfr)', [alpha]),
            ('Beta', [beta]),
            ('R-squared', [r_squared]),
            ('Treynor Ratio', [treynor]),
            ('Information Ratio',[information_ratio]),
        ])

    df = pd.DataFrame(data)
    data = df.to_dict('records')
    columns = [dict(id=i, name=i, type='numeric', format=percentage) if 'Alpha' in i else dict(id=i, name=i) for i in df.columns]
    dt = dash_table.DataTable(data, 
                            columns,
                            fixed_columns={'headers':True, 'data':1}, 
                            style_as_list_view=True,
                            style_table={'minWidth':'100%',
                                        'minHeight':100},
                            style_data=style.style_data,
                            style_header=style.style_header,
                            style_cell={
                                'textAlign': 'center',
                                'minWidth': '180px', 
                                'width': '180px',
                                'padding':'5px'},
                            style_data_conditional=[{'if': {'filter_query': '{{{}}} is blank'.format(col),
                                                            'column_id': col},
                                                            'backgroundColor': f'{style.red}',
                                                            'color': 'white'} for col in df.columns])
    return dt