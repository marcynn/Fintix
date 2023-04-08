import plotly.graph_objs as go 

# Theme
dbc_row_style = 'border border-2 rounded m-2 p-3'
params_p_style = 'mb-2 mt-2'# Used to style the text of parameter name
green = '#02aa3e'
red = '#FF0000'
chart_templates = 'plotly_white'

# Used to format a number to accounting
def accounting_format(num):
    return "{:>,.0f}".format(abs((num)))


# Tabs style
tabs_styles = {
    'height': '60px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

# Table style 
style_data={'whiteSpace': 'normal'}

style_header={
    'border': f'1px solid',
    'fontWeight':'bold',
    'textAlign': 'center',
    'padding':'20px'}

# Scatter / Line charts layouts 
def scatter_charts_layout(title=None, xtickformat=None, ytickformat=None, xaxisTitle=None, yaxisTitle=None):
    layout = go.Layout(title=f'{title}',
                        title_x=0.5,
                        font=dict(size=15),
                        height=400,
                        hoverlabel=dict(font_size=15),
                        xaxis=dict(showspikes=True, tickformat=xtickformat, title=xaxisTitle),
                        yaxis=dict(ticks='outside', showspikes=True, tickformat=ytickformat, title=yaxisTitle),
                        legend=dict(orientation='h', y=-0.2),
                        template=chart_templates
                        )
    return layout