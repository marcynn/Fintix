from dash import dash, html
import dash
import dash_bootstrap_components as dbc

# Create Dash App
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.CYBORG], 
                    meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])

#-------------------App Layout-------------------
app.layout = html.Div(
    [
        # Navbar
        dbc.NavbarSimple(
            dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem(page["name"], href=page["path"])
                        for page in dash.page_registry.values()
                        if page["module"] != "pages.not_found_404"
                    ],
                    nav=True,
                    label="More Pages",
                    className='me-5'
                ),
            id='nav-bar',
            brand="Fintix",
            brand_href="#",
            color="dark",
            dark=True,
            brand_style= {'fontSize':30},
            fluid=True,
            className='ms-2 me-2 mb-3'                 
        ),

        # content of each page
        dash.page_container
    ]
)

app.title = 'Fintix'

if __name__ == '__main__':
    app.run_server(debug=True)
