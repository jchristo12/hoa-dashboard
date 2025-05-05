import dash
from dash import html, Input, Output, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback_context

from layout import get_property_value_layout, get_roadmap_layout
from data import START_DATE_DEFAULT, combined_df
from utils import GEO, get_date_ranges, get_line_chart, get_tiles


app = dash.Dash(__name__, title=f'HOA Dashboard', external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
# Expose server for production deployment
server = app.server


app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        # Sidebar
        dbc.Col([
            html.Div([
                html.H5('Sections', className='text-white', style={'padding': '16px 0 8px 0'}),
                dbc.Nav([
                    dbc.NavLink('Property Value Trends', href='/trends', id='tab-trends', active='exact'),
                    # dbc.NavLink('Roadmap', href='/roadmap', id='tab-roadmap', active='exact'),
                    # Add more tabs here as needed
                ], vertical=True, pills=True),
            ], style={'height': '100vh', 'backgroundColor': '#222b3a', 'padding': '24px', 'minWidth': '220px'}),
        ], width='auto', style={'padding': '0', 'backgroundColor': '#222b3a'}),
        # Main content
        dbc.Col([
            html.H1(f'{GEO.get('community')} HOA Dashboard', style={'marginTop': '16px', 'marginBottom': '24px', 'marginLeft': '10px'}),
            html.Div(id='tab-content', style={'backgroundColor': '#f8f9fa', 'minHeight': '100vh', 'padding': '32px 24px'}),
        ], style={'padding': '0'}),
    ], style={'margin': '0', 'width': '100%'})
], fluid=True)


# App Callbacks
#region
@app.callback(
    [Output('btn-mean', 'style'),
     Output('btn-median', 'style')],
    [Input('btn-mean', 'n_clicks'),
     Input('btn-median', 'n_clicks')]
)
def update_button_colors(mean_clicks, median_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return {'backgroundColor': '#0d6efd', 'color': 'white', 'marginRight': '8px'}, {'backgroundColor': 'white', 'color': '#333'}
    
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if btn_id == 'btn-mean':
        return {'backgroundColor': '#0d6efd', 'color': 'white', 'marginRight': '8px'}, {'backgroundColor': 'white', 'color': '#333'}
    else:
        return {'backgroundColor': 'white', 'color': '#333', 'marginRight': '8px'}, {'backgroundColor': '#0d6efd', 'color': 'white'}

@app.callback(
    [Output('btn-3M', 'style'),
     Output('btn-6M', 'style'),
     Output('btn-1Y', 'style'),
     Output('btn-3Y', 'style'),
     Output('btn-ALL', 'style')],
    [Input('btn-3M', 'n_clicks'),
     Input('btn-6M', 'n_clicks'),
     Input('btn-1Y', 'n_clicks'),
     Input('btn-3Y', 'n_clicks'),
     Input('btn-ALL', 'n_clicks')]
)
def update_time_period_colors(n3m, n6m, n1y, n3y, nall):
    ctx = callback_context
    if not ctx.triggered:
        return [{'backgroundColor': 'white', 'color': '#333', 'marginRight': '8px'}] * 4 + [{'backgroundColor': '#0d6efd', 'color': 'white'}]
    
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    default_style = {'backgroundColor': 'white', 'color': '#333', 'marginRight': '8px'}
    active_style_3m = {'backgroundColor': '#0d6efd', 'color': 'white', 'marginRight': '8px'}
    active_style_6m = {'backgroundColor': '#0d6efd', 'color': 'white', 'marginRight': '8px'}
    active_style_1y = {'backgroundColor': '#0d6efd', 'color': 'white', 'marginRight': '8px'}
    active_style_3y = {'backgroundColor': '#0d6efd', 'color': 'white', 'marginRight': '8px'}
    active_style_all = {'backgroundColor': '#0d6efd', 'color': 'white'}
    
    if btn_id == 'btn-3M':
        return [active_style_3m] + [default_style] * 4
    elif btn_id == 'btn-6M':
        return [default_style, active_style_6m] + [default_style] * 3
    elif btn_id == 'btn-1Y':
        return [default_style] * 2 + [active_style_1y] + [default_style] * 2
    elif btn_id == 'btn-3Y':
        return [default_style] * 3 + [active_style_3y] + [default_style]
    else:  # btn-ALL
        return [default_style] * 4 + [active_style_all]

@app.callback(
    Output('tab-content', 'children'),
    [Input('url', 'pathname')]
)
def render_tab_content(pathname):
    if pathname == '/trends' or pathname == '/':
        return get_property_value_layout()
    elif pathname == '/roadmap':
        return get_roadmap_layout()
    return html.Div('404: Page not found')

@app.callback(
    Output('data-tiles', 'children'),
    [Input('btn-mean', 'n_clicks'),
     Input('btn-median', 'n_clicks')]
)
def update_tiles(mean_clicks, median_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return get_tiles(combined_df, 'avg')
    
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    mean_median = 'median' if btn_id == 'btn-median' else 'avg'
    return get_tiles(combined_df, mean_median)

@app.callback(
    Output('trend-chart', 'children'),
    [Input('btn-3M', 'n_clicks'),
     Input('btn-6M', 'n_clicks'),
     Input('btn-1Y', 'n_clicks'),
     Input('btn-3Y', 'n_clicks'),
     Input('btn-ALL', 'n_clicks'),
     Input('btn-mean', 'n_clicks'),
     Input('btn-median', 'n_clicks')]
)
def update_chart(n3m, n6m, n1y, n3y, nall, mean_clicks, median_clicks):
    ctx = callback_context
    if not ctx.triggered:
        range_key = 'ALL'
        mean_median = 'avg'
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id.startswith('btn-'):
            if btn_id in ['btn-mean', 'btn-median']:
                mean_median = 'median' if btn_id == 'btn-median' else 'avg'
                range_key = 'ALL'  # Keep current range when switching mean/median
            else:
                range_key = btn_id.split('-')[1]
                mean_median = 'median' if median_clicks > mean_clicks else 'avg'
        else:
            range_key = 'ALL'
            mean_median = 'avg'
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