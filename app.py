from dash import dash, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import  Scripts.layout as layout
import Scripts.utils as utils

# Create Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SIMPLEX], 
                    meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])

#-------------------App Layout-------------------
app.layout = layout.layout

#-------------------Callbacks-------------------

# Download data sample
@app.callback(Output("download-dataframe-csv", "data"),
                Input("btn_csv", "n_clicks"),
                prevent_initial_call=True)
def func(n_clicks):
    if n_clicks >=1:
        df = pd.read_csv('Data/sample-data.csv')
        return dcc.send_data_frame(df.to_csv, "sample-data.csv", index=False)

# Store uploaded data
@app.callback(Output('output-datatable', 'children'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),
            State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    '''
    Updates output of uploaded Excel file and stores data.
    '''
    if list_of_contents is not None:
        children = [
            utils.display_uploaded_file(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        
        return children

# Display parameters
@app.callback(Output('params','children'),
            Output('submit-btn','color'),
            [Input('submit-btn','n_clicks')])
def display_params(n_clicks):
    if n_clicks >= 1:
        params =  utils.create_params()
        return params, 'success'

# Update date picker to relevant dates
@app.callback(Output('start-date','date'),
            Output('end-date','date'),
            [Input('stored-data','data')])
def update_date_picker(data):
    data = utils.json_to_df(data)
    min_date = data.index.min()
    max_date = data.index.max()
    return min_date, max_date

# Update main asset and benchmark to relevant ones
@app.callback(Output('main-asset','options'),
            Output('benchmark-asset','options'),
            Output('main-asset','value'),
            Output('benchmark-asset','value'),
            [Input('stored-data','data')])
def update_dropdowns(data):

    data = utils.json_to_df(data)

    try:
        main_asset = data.columns[0]
    except:
        main_asset = ''
    try:
        benchmark_asset = data.columns[1]
    except:
        benchmark_asset = ''

    options = [{'label':i, 'value':i} for i in data.columns]

    return options, options, main_asset, benchmark_asset

# Update body
@app.callback(Output('body','children'),
            [Input('stored-data','data'),
            Input('start-date','date'),
            Input('end-date','date'),
            Input('initial-amount','value'),
            Input('rfr','value'),
            Input('periods-per-year','value'),
            Input('rolling-periods','value'),
            Input('menu-tabs','value'),
            Input('main-asset','value'),
            Input('benchmark-asset','value')
            ])
def display_body(data, start_date, end_date, initial_amount, rfr, periods_per_year, rolling_periods, tab, main_asset, benchmark_asset):
    data = utils.json_to_df(data)
    try:
        data = data.loc[start_date:end_date] # Filter for start and end dates from date picker
    except:
        pass
    if tab == 'compare':
        return utils.display_compare(data, initial_amount, rfr, periods_per_year, rolling_periods)
    elif tab == 'returns':
        return utils.display_returns(data, main_asset)
    elif tab == 'benchmark':
        return utils.display_benchmark(data, main_asset, benchmark_asset, periods_per_year)
    elif tab == 'rolling':
        return utils.display_rolling(data, main_asset, benchmark_asset, rolling_periods, rfr, periods_per_year)

if __name__ == '__main__':
    app.run_server(debug=True)