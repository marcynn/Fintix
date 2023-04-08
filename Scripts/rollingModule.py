import quantstats as qs
import plotly.graph_objs as go
import Scripts.style as style

def create_rolling_metrics(data, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, metric="Sharpe"):
    '''
    Returns a rolling line chart figure for a given metric.
    Possible metrics include: 'Alpha','Beta','Sharpe', 'Sortino', 'Volatility'
    '''
    if metric not in ['Alpha','Beta','Sharpe', 'Sortino', 'Volatility']:
        return

    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)
    greeks = qs.stats.rolling_greeks(returns[main_asset], returns[benchmark_asset], periods=rolling_periods, prepare_returns=False)

    ytickformat = ''
    yaxisTitle = ''

    if metric == 'Sharpe':
        series = round(qs.stats.rolling_sharpe(returns[main_asset], rf=rfr, rolling_period=rolling_periods, periods_per_year=periods_per_year, annualize=True, prepare_returns=True),3)
        yaxisTitle = main_asset
    elif metric == 'Sortino':
        series = round(qs.stats.rolling_sortino(returns[main_asset], rf=rfr, rolling_period=rolling_periods, annualize=True, periods_per_year=periods_per_year),3)
        yaxisTitle = main_asset
    elif metric == 'Alpha':
        series = greeks['alpha'] * rolling_periods
        yaxisTitle = f"{main_asset} vs {benchmark_asset}"
        ytickformat = ',.2%'
    elif metric == 'Beta':
        series = round(greeks['beta'],3)
        yaxisTitle = f"{main_asset} vs {benchmark_asset}"
    elif metric == 'Volatility':
        series = round(qs.stats.rolling_volatility(returns[main_asset], rolling_period=rolling_periods, periods_per_year=periods_per_year, prepare_returns=False),3)
        yaxisTitle = main_asset

    avg = round(series.dropna().mean(),3)

    traces = [go.Scatter(x=series.index, 
                y=series,
                mode='lines+text',
                name='Rol',
                marker=dict(size=12,
                            line=dict(width=2)))]
                            
    traces += [go.Scatter(x=series.index,
                            y=[avg for i in series.index],
                            mode='lines',
                            name='Avg',
                            line=dict(color=style.red, 
                                    width=1))]
        
    layout = style.scatter_charts_layout(f"{rolling_periods}P Rolling {metric}", 
                                    ytickformat=ytickformat, yaxisTitle=yaxisTitle)

    figure = go.Figure(traces, layout)
    return figure
