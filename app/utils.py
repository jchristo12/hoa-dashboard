import pandas as pd
from dash import dcc
import plotly.graph_objs as go


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