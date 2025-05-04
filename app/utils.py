import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go


# Geography lookup
GEO = {
    'community': 'SkyTerrace Towns',
    'neighborhood': 'Wesley Heights',
    'city': 'Charlotte',
    'state': 'North Carolina'
}

def get_current_values(df, mean_median):
    latest = df.loc[df['date'] == df['date'].max()]
    geo_keys = ['community', 'neighborhood', 'city', 'state']
    values = {}
    for geo in geo_keys:
        ser = latest[f'{geo}_{mean_median}']
        values[geo] = float(ser.iloc[0]) if not ser.empty else None
    # Get last year value for community
    last_year_date = latest['date'].max() - pd.DateOffset(years=1)
    last_year_row = df.loc[df['date'] == last_year_date]
    if not last_year_row.empty:
        ser = last_year_row[f'community_{mean_median}']
        last_year_val = float(ser.iloc[0]) if not ser.empty else None
    else:
        last_year_val = None
    values['community_last_year'] = last_year_val
    return values

def percent_and_color(val, ref):
    if ref == 0 or ref is None:
        return 'N/A', 'black'
    pct = (val - ref) / ref * 100
    color = 'green' if pct > 0 else 'red' if pct < 0 else 'black'
    return f'{pct:+.1f}%', color

def get_tiles(df, mean_median='avg'):
    vals = get_current_values(df, mean_median)
    card_body_style = {'minHeight': '130px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center'}
    # Main HOA value tile
    current = vals['community']
    tiles = [
        dbc.Card([
            dbc.CardBody([
                html.H6(f'Average {GEO.get('community')} Value', className='card-title'),
                html.H3(f"${current:,.0f}", className='card-text'),
            ], style=card_body_style)
        ], className='m-2'),
    ]
    # Comparison tiles
    for geo in ['neighborhood', 'city', 'state']:
        ref = vals[geo]
        pct, color = percent_and_color(current, ref)
        dollar = current - ref
        abs_dollar_str = f"${abs(dollar):,.0f}"
        sign = '+' if dollar > 0 else '-' if dollar < 0 else ''
        label = {
            'neighborhood': f'vs. {GEO.get('neighborhood')}',
            'city': f'vs. {GEO.get('city')}',
            'state': f'vs. {GEO.get('state')}',
        }[geo]
        tiles.append(
            dbc.Card([
                dbc.CardBody([
                    html.H6(label, className='card-title'),
                    html.H3(pct, className='card-text', style={'color': color, 'fontWeight': 'bold'}),
                    html.Div(f'{sign}{abs_dollar_str}', style={'color': color, 'fontSize': '0.9em'})
                ], style=card_body_style)
            ], className='m-2')
        )
    return dbc.Row([dbc.Col(tile) for tile in tiles], className='mb-4')


# Date range options
def get_date_ranges(df):
    today = df['date'].max()
    return {
        '3M': today - pd.DateOffset(months=3),
        '6M': today - pd.DateOffset(months=6),
        '1Y': today - pd.DateOffset(years=1),
        '3Y': today - pd.DateOffset(years=3),
        'ALL': pd.to_datetime('08/01/2024')
    }

def filter_df_by_range(df, range_key):
    date_ranges = get_date_ranges(df)
    start = date_ranges[range_key]
    return df[df['date'] >= start]

def get_line_chart(filtered_df, start_date, mean_median):
    fig = go.Figure()
    geo_map = {
        'community': 'SkyTerrace Towns',
        'neighborhood': 'Wesley Heights',
        'city': 'Charlotte',
        'state': 'North Carolina',
    }
    for geo, label in geo_map.items():
        col = f'{geo}_{mean_median}_indexed'
        if col in filtered_df.columns:
            fig.add_trace(go.Scatter(
                x=filtered_df['date'],
                y=filtered_df[col],
                mode='lines+markers',
                name=label,
                hovertemplate='%{y:.1f}'
            ))
    fig.update_layout(
        yaxis={'title': 'Indexed Home Value', 'tickformat': '.1f'},
        xaxis={
            'title': '',
            'tickformat': '%b %Y',
            'dtick': 'M1',
            'range': [start_date, filtered_df['date'].max()]
        },
        margin={'l': 40, 'r': 10, 't': 10, 'b': 40},
        height=400,
        legend_title_text='Geography',
        hovermode='x unified',
    )
    return dcc.Graph(figure=fig, config={'displayModeBar': False})