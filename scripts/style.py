from turtle import bgcolor
import plotly.graph_objs as go 

# Theme
dbc_row_style = 'border border-2 rounded m-2 p-3'
params_p_style = 'mb-2 mt-2'# Used to style the text of parameter name
green = '#02aa3e'
red = '#FF0000'
chart_templates = 'plotly_dark'
main_theme_color = '#375a7f' # Modify this to the hex of 'primary' when changing bootstrap theme
secondary_theme_color = '#222222' # Modify this to the hex of 'secondary' when changing bootstrap theme

# Used to format a number to accounting
def accounting_format(num):
    return "{:>,.0f}".format(abs((num)))

# Tabs style
tabs_styles = {
    'height': '60px'}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'backgroundColor': secondary_theme_color}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': main_theme_color,
    'color': 'white',
    'padding': '6px'}

# Table style 
style_data={'whiteSpace': 'normal',
            'backgroundColor': secondary_theme_color,
            'color':'white', 
            'padding':'10px'}

style_header={
    'border': f'1px solid',
    'fontWeight':'bold',
    'textAlign': 'center',
    'padding':'10px',
    'backgroundColor': main_theme_color,
    'color':'white'}

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
                        template=chart_templates,
                        paper_bgcolor=secondary_theme_color,
                        plot_bgcolor=secondary_theme_color,
                        )
    return layout