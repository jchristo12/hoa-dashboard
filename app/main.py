import dash
from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback_context

from data import START_DATE_DEFAULT, combined_df
from utils import GEO, get_date_ranges, get_line_chart, get_tiles


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
# Expose server for production deployment
server = app.server


app.layout = dbc.Container([
    dbc.Row([
        # Sidebar
        dbc.Col([
            html.Div([
                html.H5('Sections', className='text-white', style={'padding': '16px 0 8px 0'}),
                dbc.Nav([
                    dbc.NavLink('Property Value Trends', href='/trends', id='tab-trends', active=True, className='mb-2'),
                    # Add more tabs here as needed
                ], vertical=True, pills=True),
            ], style={'height': '100vh', 'backgroundColor': '#222b3a', 'padding': '24px', 'minWidth': '220px'}),
        ], width='auto', style={'padding': '0', 'backgroundColor': '#222b3a'}),
        # Main content
        dbc.Col([
            html.H1('SkyTerrace Towns HOA Dashboard', style={'marginTop': '16px', 'marginBottom': '24px'}),
            html.Div(id='tab-content', style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'padding': '32px 24px'}),
        ], style={'padding': '0'}),
    ], style={'margin': '0', 'width': '100%'})
], fluid=True)


# App Callbacks
#region
@app.callback(
    Output('tab-content', 'children'),
    [Input('tab-trends', 'active')]
)
def render_tab_content(trends_active):
    if trends_active:
        return [
            html.H2('Property Value Trends'),
            html.Div(
                dcc.RadioItems(
                    id='mean-median-toggle',
                    options=[
                        {'label': 'Mean', 'value': 'avg'},
                        {'label': 'Median', 'value': 'median'}
                    ],
                    value='avg',
                    inline=True,
                    inputStyle={'marginRight': '6px', 'marginLeft': '12px'},
                    labelStyle={'marginRight': '18px'},
                    style={'marginBottom': '10px'}
                ),
                style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '10px'}
            ),
            html.Div(id='data-tiles'),
            html.Div(
                dbc.ButtonGroup([
                    dbc.Button('3M', id='btn-3M', n_clicks=0),
                    dbc.Button('6M', id='btn-6M', n_clicks=0),
                    dbc.Button('1Y', id='btn-1Y', n_clicks=0),
                    dbc.Button('3Y', id='btn-3Y', n_clicks=0),
                    dbc.Button('ALL', id='btn-ALL', n_clicks=0),
                ], className='mb-3', id='date-range-buttons'),
                style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '10px'}
            ),
            html.Div(id='trend-chart'),
            html.Div(
                'Note: All values are indexed to 100 as of August 1, 2021 representing changes in average home values over time.',
                style={'fontSize': '0.9em', 'color': '#888', 'marginTop': '10px'}
            ),
        ]
    return html.Div()

@app.callback(
    Output('data-tiles', 'children'),
    [Input('mean-median-toggle', 'value')]
)
def update_tiles(mean_median):
    return get_tiles(combined_df, mean_median)

@app.callback(
    Output('trend-chart', 'children'),
    [Input('btn-3M', 'n_clicks'),
     Input('btn-6M', 'n_clicks'),
     Input('btn-1Y', 'n_clicks'),
     Input('btn-3Y', 'n_clicks'),
     Input('btn-ALL', 'n_clicks'),
     Input('mean-median-toggle', 'value')]
)
def update_chart(n3m, n6m, n1y, n3y, nall, mean_median):
    ctx = dash.callback_context
    if not ctx.triggered:
        range_key = 'ALL'
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id.startswith('btn-'):
            range_key = btn_id.split('-')[1]
        else:
            range_key = 'ALL'
    # For 'ALL', always start at 8/1/2024
    if range_key == 'ALL':
        start_date = pd.to_datetime('08/01/2024')
        filtered = combined_df[combined_df['date'] >= start_date]
    else:
        date_ranges = get_date_ranges(combined_df)
        start_date = date_ranges[range_key] if range_key in date_ranges else START_DATE_DEFAULT
        filtered = combined_df[combined_df['date'] >= start_date]
    if filtered.empty:
        filtered = combined_df[combined_df['date'] >= start_date]
    
    return get_line_chart(filtered, start_date, mean_median)
#endregion

if __name__ == '__main__':
    app.run_server(debug=True) 