import quantstats as qs
import plotly.graph_objs as go
import Scripts.style as style

def create_rolling_metrics(data, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year, metric="Sharpe", round_to=3):
    '''
    Returns a rolling line chart figure for a given metric.
    Possible metrics include: 'Alpha','Beta','Sharpe', 'Sortino', 'Volatility', 'Correlation'
    '''
    if metric not in ['Alpha','Beta','Sharpe', 'Sortino', 'Volatility', 'Correlation']:
        return

    prices = data.copy()
    returns = qs.utils._prepare_returns(prices)
    greeks = qs.stats.rolling_greeks(returns[main_asset], returns[benchmark_asset], periods=rolling_periods, prepare_returns=False)

    ytickformat = ''
    yaxisTitle = ''

    if metric == 'Sharpe':
        series = qs.stats.rolling_sharpe(returns[main_asset], rf=rfr, rolling_period=rolling_periods, periods_per_year=periods_per_year, annualize=True, prepare_returns=True)
        yaxisTitle = main_asset
    elif metric == 'Sortino':
        series = qs.stats.rolling_sortino(returns[main_asset], rf=rfr, rolling_period=rolling_periods, annualize=True, periods_per_year=periods_per_year)
        yaxisTitle = main_asset
    elif metric == 'Alpha':
        series = greeks['alpha'] * rolling_periods
        yaxisTitle = f"{main_asset} vs {benchmark_asset}"
        ytickformat = ',.2%'
    elif metric == 'Beta':
        series = greeks['beta']
        yaxisTitle = f"{main_asset} vs {benchmark_asset}"
    elif metric == 'Volatility':
        series = qs.stats.rolling_volatility(returns[main_asset], rolling_period=rolling_periods, periods_per_year=periods_per_year, prepare_returns=False)
        yaxisTitle = main_asset
    elif metric == 'Correlation':
        series = returns[main_asset].rolling(rolling_periods).corr(returns[benchmark_asset])
        yaxisTitle = f"{main_asset} vs {benchmark_asset}"

    series = round(series, round_to)
    avg = round(series.dropna().mean(),round_to)

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
