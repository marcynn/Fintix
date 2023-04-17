import pandas as pd
import numpy as np
import quantstats as qs
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dash import dash_table
from collections import OrderedDict
from dash.dash_table import FormatTemplate
from dash.dash_table.Format import Format, Scheme
import scripts.style as style

def create_metrics_table(data, periods_per_year, rfr, round_to=2):
    prices = data.copy()
    assets = prices.columns.to_list()
    returns = qs.utils._prepare_returns(prices)
    prices = qs.utils._prepare_prices(returns)

    # Setup dates lookback
    last_date = prices.index[-1]
    week_date = last_date - relativedelta(weeks=1)
    mtd_date = datetime(last_date.year, last_date.month, 1)
    m3_date = last_date - relativedelta(months=3)
    m6_date = last_date - relativedelta(months=6)
    ytd_date = datetime(last_date.year, 1,1)
    y1_date = last_date - relativedelta(years=1)
    y3_date = last_date - relativedelta(years=3)
    y5_date = last_date - relativedelta(years=5)

    data = OrderedDict(
        [
            # Params loaded and info
            ('Asset', prices.columns),
            ('Start Date', [returns[a].first_valid_index().strftime("%m/%d/%Y") for a in assets]),
            ('End Date', [returns[a].last_valid_index().strftime("%m/%d/%Y") for a in assets]),
            ('Data Points', list(np.repeat(returns.shape[0], len(assets)))),
            ('Periods Per Year', list(np.repeat(periods_per_year, len(assets)))),
            ('Risk-free Rate', list(np.repeat(rfr, len(assets)))),
            
            # Returns 
            ('1W Return', prices.loc[last_date] / prices.loc[week_date:].iloc[0] - 1),  # iloc[0] in case weekly date wasn't available so we retrieve the closest date.
            ('MTD Return', prices.loc[last_date] / prices.loc[mtd_date:].iloc[0] - 1),
            ('3M Return', (prices.loc[last_date] / prices.loc[m3_date:].iloc[0]) -1),
            ('6M Return', (prices.loc[last_date] / prices.loc[m6_date:].iloc[0]) -1),
            ('YTD Return', (prices.loc[last_date] / prices.loc[ytd_date:].iloc[0]) -1),
            ('1Y Return', (prices.loc[last_date] / prices.loc[y1_date:].iloc[0]) -1),
            ('3Y Return', (prices.loc[last_date] / prices.loc[y3_date:].iloc[0]) -1),
            ('5Y Return', (prices.loc[last_date] / prices.loc[y5_date:].iloc[0]) -1),
            ('Total Return', qs.stats.comp(returns)),
            ('CAGR', qs.stats.cagr(returns, rf=0, compounded=True)),
            ('Avg Return', qs.stats.avg_return(returns, aggregate=None, compounded=True, prepare_returns=False)),
            ('Avg (+) Return', qs.stats.avg_win(returns, aggregate=None, compounded=True, prepare_returns=False)),
            ('Avg (-) Return', qs.stats.avg_loss(returns, aggregate=None, compounded=True, prepare_returns=False)),
            ('Best Return', qs.stats.best(returns, aggregate=None, compounded=True, prepare_returns=False)),
            ('Worst Return', qs.stats.worst(returns, aggregate=None, compounded=True, prepare_returns=False)),
            
            # Stats
            ('Win Rate', qs.stats.win_rate(returns, aggregate=None, compounded=False, prepare_returns=False)),
            ('Loss Rate', 1 - qs.stats.win_rate(returns, aggregate=None, compounded=False, prepare_returns=False)),
            ('Payoff Ratio', qs.stats.payoff_ratio(returns, prepare_returns=False)),
            ('Tail Ratio 95%', qs.stats.tail_ratio(returns, cutoff=0.95, prepare_returns=True)),
            ('Skew', qs.stats.skew(returns, prepare_returns=False)),
            ('Kurtosis', qs.stats.kurtosis(returns, prepare_returns=False)),
            ('Kelly Criterion', qs.stats.kelly_criterion(returns, prepare_returns=False)),

            # Risk
            ('Volatility', qs.stats.volatility(returns, periods=periods_per_year, annualize=False, prepare_returns=False)),
            ('Volatility P.A.', qs.stats.volatility(returns, periods=periods_per_year, annualize=True, prepare_returns=False)),
            ('Max Drawdown', qs.stats.max_drawdown(prices)),
            ('Max Drawdown Date', [i.strftime("%m/%d/%Y") for i in (prices/prices.cummax()-1).idxmin()]),
            ('VaR 95%', qs.stats.value_at_risk(returns, sigma=1, confidence=0.95, prepare_returns=False)),
            ('CVaR 95%', qs.stats.cvar(returns, sigma=1, confidence=0.95, prepare_returns=True)),

            # Risk-adjusted Ratios
            ('Sharpe Ratio', qs.stats.sharpe(returns, rf=rfr, periods=periods_per_year, annualize=True)),
            ('Sharpe Ratio P.A.', qs.stats.sharpe(returns, rf=rfr, periods=periods_per_year, annualize=True)),
            ('Sortino Ratio', qs.stats.sortino(returns, rf=rfr, periods=periods_per_year, annualize=True)),
            ('Sortino Ratio P.A.', qs.stats.sortino(returns, rf=rfr, periods=periods_per_year, annualize=True)),
            ('Calmar Ratio', qs.stats.calmar(returns, prepare_returns=True)),
            
        ])

    df = pd.DataFrame(data)
    data = df.to_dict('records')
    
    columns = [
        # Params loaded and info
        dict(id='Asset', name=['Asset', '']),
        dict(id='Start Date', name=['Params & Info', 'Start Date']),
        dict(id='End Date', name=['','End Date']),
        dict(id='Data Points', name=['','Data Points']),
        dict(id='Periods Per Year', name=['','Periods Per Year']),
        dict(id='Risk-free Rate', name=['','Risk-free Rate'], type='numeric', format=FormatTemplate.percentage(round_to)),

        # Returns 
        dict(id='1W Return', name=['Returns','1W Return'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='MTD Return', name=['','MTD Return'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='3M Return', name=['','3M Return'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='6M Return', name=['','6M Return'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='YTD Return', name=['','YTD Return'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='1Y Return', name=['','1Y Return'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='3Y Return', name=['','3Y Return'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='5Y Return', name=['','5Y Return'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='Total Return', name=['','Total Return'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='CAGR', name=['','CAGR'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='Avg Return', name=['','Average Return'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='Avg (+) Return', name=['','Avg (+) Return'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='Avg (-) Return', name=['','Avg (-) Return'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='Best Return', name=['','Best Return'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='Worst Return', name=['','Worst Return'], type='numeric', format=FormatTemplate.percentage(round_to)),

        # Stats
        dict(id='Win Rate', name=['Stats','Win Rate'], type='numeric', format=FormatTemplate.percentage(round_to)), 
        dict(id='Loss Rate', name=['','Loss Rate'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='Payoff Ratio', name=['','Payoff Ratio'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Tail Ratio 95%', name=['','Tail Ratio 95%'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Skew',name=['','Skew'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Kurtosis',name=['','Kurtosis'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Kelly Criterion', name=['','Kelly Criterion'], type='numeric', format=FormatTemplate.percentage(round_to)),

        # Risk
        dict(id='Volatility', name=['Risk','Volatility'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='Volatility P.A.', name=['','Volatility P.A.'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='Max Drawdown', name=['','Max Drawdown'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='Max Drawdown Date', name=['','Max Drawdown Date']),
        dict(id='VaR 95%', name=['','VaR 95%'], type='numeric', format=FormatTemplate.percentage(round_to)),
        dict(id='CVaR 95%', name=['','CVaR 95%'], type='numeric', format=FormatTemplate.percentage(round_to)),
        
        # Risk-adjusted Ratios
        dict(id='Sharpe Ratio', name=['Risk-adjusted Ratios', 'Sharpe Ratio'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Sharpe Ratio P.A.', name=['','Sharpe Ratio P.A.'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Sortino Ratio', name=['','Sortino Ratio'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Sortino Ratio P.A.', name=['','Sortino Ratio P.A.'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),
        dict(id='Calmar Ratio', name=['','Calmar Ratio'], type='numeric', format=Format(precision=round_to, scheme=Scheme.decimal)),

    ]

    dt = dash_table.DataTable(data, 
                            columns,
                            fixed_columns={'headers':True, 'data':1}, 
                            sort_action='native',

                            # Add tooltips
                            tooltip_header={
                                "CVaR 95%": "Expected Shortfall",
                                "Tail Ratio 95%": "95th percentile / 5th percentile",
                                "Calmar Ratio": "CAGR / Max DD",
                                "Payoff Ratio": "Avg Win / Avg Loss"
                            },

                            # Style tooltips
                            css=[{
                                'selector': '.dash-table-tooltip',
                                'rule': 'background-color: grey; color: white'
                            }],

                            # Cell / Header styling
                            style_as_list_view=True,
                            style_table={'minWidth':'100%',
                                        'minHeight':150},
                            style_data=style.style_data,
                            style_header=style.style_header,
                            style_cell={
                                'textAlign': 'center',
                                'minWidth': '180px', 
                                'width': '180px',
                                'padding':'5px'},

                            # Conditional Formatting
                            style_header_conditional=[{ 'if': { 'header_index': 0 }, 'backgroundColor': style.secondary_theme_color}],
                            style_data_conditional=[{'if': {'filter_query': f'{{{col}}} < 0',
                                                            'column_id': col},
                                                    'color':style.red} for col in df.columns[(df.columns.str.contains('Return') | 
                                                                            df.columns.str.contains('CAGR') | 
                                                                            df.columns.str.contains('Sharpe') |
                                                                            df.columns.str.contains('Sortino') | 
                                                                            df.columns.str.contains('Calmar'))
                                                                            ]
                                                                    ] + 

                                                    [{'if': {'filter_query': f'{{{col}}} > 0',
                                                            'column_id': col},
                                                    'color':style.green} for col in df.columns[(df.columns.str.contains('Return') | 
                                                                            df.columns.str.contains('CAGR') | 
                                                                            df.columns.str.contains('Sharpe') |
                                                                            df.columns.str.contains('Sortino') |
                                                                            df.columns.str.contains('Calmar'))
                                                                            ]
                                                                    ] + 
                                                    [ {'if': {'filter_query': '{{{}}} is blank'.format(col),
                                                            'column_id': col},
                                                            'backgroundColor': f'{style.red}',
                                                            'color': 'white'} for col in df.columns]
                                                    )                                                                                        
    return dt