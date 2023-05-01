import plotly.graph_objs as go 

# Theme
dbc_row_style = 'border border-2 rounded m-2 p-2 border-secondary' # Used to style dbc rows
dbc_col_style = 'border border-2 rounded border-secondary mt-4'
params_p_style = 'mb-2 mt-2 text-warning' # Used to style the text of parameter name
h5_style = 'm-4 text-warning fw-bold text-center' # Used to style H5 
green = '#02aa3e'
red = '#FF0000'
chart_templates = 'plotly_dark'
main_theme_color = '#ff8800'
secondary_theme_color = '#000000'

# Used to format a number to accounting
def accounting_format(num):
    return "{:>,.0f}".format(abs((num)))

# Tabs style
tabs_styles = {
    'height': '60px',}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'backgroundColor': secondary_theme_color,
    'font-size':'x-large'
    }

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': main_theme_color,
    'color': secondary_theme_color,
    'font-size':'x-large',
    'padding': '6px'}

# Table style 
def create_table_data_style(padding='10px'):
    style={'whiteSpace': 'normal',
            'backgroundColor': secondary_theme_color,
            'color':'white', 
            'padding':padding}
    return style
style_data = create_table_data_style()

style_header={
    'border': f'1px solid',
    'fontWeight':'bold',
    'textAlign': 'center',
    'padding':'10px',
    'backgroundColor': secondary_theme_color,
    'color':main_theme_color}

def style_table_column_by_minmax_value(df):
    '''
    Conditionally formats max and min values in dash data table numeric columns.
    '''
    if 'id' in df:
        numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
    else:
        numeric_columns = df.select_dtypes('number')

    max_across_numeric_columns = numeric_columns.max()
    min_across_numeric_columns = numeric_columns.min()

    styles = []

    # Max value formatting
    for col in max_across_numeric_columns.keys():
        styles.append({
            'if': {
                'filter_query': '{{{col}}} = {value}'.format(
                    col=col, value=max_across_numeric_columns[col]
                ),
                'column_id': col
            },
            'backgroundColor': '#000C66',
            "fontWeight": "bold"
        })

    # Min value formatting
    for col in min_across_numeric_columns.keys():
        styles.append({
            'if': {
                'filter_query': '{{{col}}} = {value}'.format(
                    col=col, value=min_across_numeric_columns[col]
                ),
                'column_id': col
            },
            'backgroundColor': main_theme_color,
            "fontWeight": "bold"
        })
    return styles

# Scatter / Line charts layouts 
def scatter_charts_layout(title=None, xtickformat=None, ytickformat=None, xaxisTitle=None, yaxisTitle=None):
    '''
    Styles plotly graph objects charts consistently.
    '''
    layout = go.Layout(title=dict(text=f'<b>{title}</b>',
                                    x=0.5,
                                    font=dict(color=main_theme_color)),
                        font=dict(size=15),
                        height=500,
                        hoverlabel=dict(font_size=15),
                        xaxis=dict(showspikes=False, tickformat=xtickformat, title=xaxisTitle),
                        yaxis=dict(ticks='outside', showspikes=False, tickformat=ytickformat, title=yaxisTitle),
                        #legend=dict(orientation='h'),
                        template=chart_templates,
                        paper_bgcolor=secondary_theme_color,
                        plot_bgcolor=secondary_theme_color,
                        margin=go.layout.Margin(
                                                l=5,
                                                r=5,
                                                b=30,
                                                t=60,
                                                pad=0
                                            )
                        )
    return layout

def add_range_slider(fig, rangeSlideVisible=False):
    '''
    Adds range slider and range selector to visuals that have a datetime field.
    '''
    fig.update_xaxes(rangeslider=dict(visible=rangeSlideVisible, bordercolor='white'),
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1, label="1m", step="month", stepmode="backward"),
                                    dict(count=6, label="6m", step="month", stepmode="backward"),
                                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                                    dict(count=1, label="1y", step="year", stepmode="backward"),
                                    dict(step="all"),
                                ])))

    fig.update_layout(xaxis_rangeselector_font_color='white',
                    xaxis_rangeselector_activecolor=f'{main_theme_color}',
                    xaxis_rangeselector_bgcolor='black',
                )
    # Add margin to prevent title overlap with buttons.
    fig.update_layout(margin=dict(t=100))
                    
    return fig