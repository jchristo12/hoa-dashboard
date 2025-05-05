import os
from dash import html, dcc
import dash_bootstrap_components as dbc

def get_property_value_layout():
    """
    Creates the content for the Property Value Trends section.
    """
    return html.Div([
            html.H2('Property Value Trends'),
            html.Div([
                dbc.ButtonGroup([
                    dbc.Button('Mean', id='btn-mean', n_clicks=1, color='primary', className='mean-median-btn', style={'backgroundColor': '#0d6efd', 'color': 'white', 'marginRight': '8px'}),
                    dbc.Button('Median', id='btn-median', n_clicks=0, color='secondary', className='mean-median-btn', style={'backgroundColor': 'white', 'color': '#333'}),
                ], className='mb-3', id='mean-median-buttons'),
            ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '10px'}),
            html.Div(id='data-tiles'),
            html.Div([
                dbc.ButtonGroup([
                    dbc.Button('3M', id='btn-3M', n_clicks=0, style={'backgroundColor': 'white', 'color': '#333', 'marginRight': '8px'}),
                    dbc.Button('6M', id='btn-6M', n_clicks=0, style={'backgroundColor': 'white', 'color': '#333', 'marginRight': '8px'}),
                    dbc.Button('1Y', id='btn-1Y', n_clicks=0, style={'backgroundColor': 'white', 'color': '#333', 'marginRight': '8px'}),
                    dbc.Button('3Y', id='btn-3Y', n_clicks=0, style={'backgroundColor': 'white', 'color': '#333', 'marginRight': '8px'}),
                    dbc.Button('ALL', id='btn-ALL', n_clicks=1, style={'backgroundColor': '#0d6efd', 'color': 'white'}),
                ], className='mb-3', id='date-range-buttons'),
            ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '10px'}),
            html.Div(id='trend-chart'),
            html.Div(
                'Note: All values are indexed to 100 as of August 1, 2021 representing changes in average home values over time.',
                style={'fontSize': '0.9em', 'color': '#888', 'marginTop': '10px'}
            ),
    ])

def get_roadmap_layout():
    """
    Creates the content for the Roadmap section.
    """
    output = html.Div([
        html.H2('Roadmap'),
        html.Iframe(
            src=os.getenv('TRELLO_BOARD_URL'),
            style={'width': '100%', 'height': '800px', 'border': 'none'}
        )
    ])

    #! Testing
    # output = html.H3('Joe Christoff')

    return output