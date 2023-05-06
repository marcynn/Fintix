import dash_bootstrap_components as dbc
from dash import html, dcc
import dash
import scripts.style as style
import sys

path = sys.path[0]

dash.register_page(__name__, path='/')

def create_card(img_src, H4, P, btn_href, btn='Try Out!'):
    card = dbc.Card(
    [
        dbc.CardImg(src=img_src, top=True, style={'height':'250px'}),
        dbc.CardBody(
            [
                html.H4(H4, className="card-title"),
                html.P(
                    P,
                    className="card-text",
                ),
                dbc.Button(btn, color="warning", href=btn_href),

                ], style={'height':'160px',
                            'background':style.secondary_theme_color}
            )
        ],
    )
    return card

compare_card = create_card(img_src=f"/assets/compare.png", H4="Compare", P="Performance and risk analytics dashboard for comparing investment strategies and assets.", btn_href='/compare')
dca_card = create_card(img_src=f"/assets/dca.png", H4="DCA", P="Model DCA vs Lump Sum investment strategies.", btn_href='/dca')
overview_card = create_card(img_src=f"/assets/overview.png", H4="Overview", P="Yearly performance table of asset classes, factors, and sectors.", btn_href='/overview')

motivation_summary_text = '''
                            This project started as a way to consolidate my **Python for investments & finance** programs into a single platform. The idea is to share programs and tools that help in investment research and decisions.

                            The code is open sourced under **MIT License**. Feel free to fork it, submit pull requests and open issues. 
                            
                            #### **[Github](https://github.com/marcynn/Fintix)**

                            '''
#### Create layout
layout = dbc.Container([

                    dbc.Row([

                        html.H1([
                            "Free and open source investment research & analytics platform written in Python."
                        ], className='text-warning text-center')

                    ], className=style.dbc_row_style),

                    dbc.Row([
                        
                        html.H3('Tools', className=style.h5_style + 'text-warning fw-bold'),

                        dbc.Col([
                            compare_card
                        ],xs=12, sm=12, md=12, lg=6, xl=6, className='mt-3'),

                        dbc.Col([
                            dca_card
                        ],xs=12, sm=12, md=12, lg=6, xl=6, className='mt-3'),

                        dbc.Col([
                            overview_card
                        ],xs=12, sm=12, md=12, lg=6, xl=6, className='mt-3'),

                        html.H3('Motivation', className=style.h5_style + 'text-warning fw-bold'),

                        dbc.Col([
                    
                            dcc.Markdown(motivation_summary_text, className='text-center fs-5'),

                        ], className=style.dbc_col_style + ' border-warning p-5 m-3')

                    ], className=style.dbc_row_style)
],fluid=True)
