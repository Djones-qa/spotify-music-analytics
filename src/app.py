import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from generate_data import generate_database
from queries import (streams_by_genre, top_tracks, audio_features_by_genre,
                     mood_distribution, release_trend, platform_stats,
                     top_artists, kpi_summary)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'spotify.db')
if not os.path.exists(DB_PATH):
    generate_database(DB_PATH)

BG, CARD_BG, TEXT, MUTED, ACCENT = '#0F172A', '#1E293B', '#F1F5F9', '#94A3B8', '#1DB954'
COLOURS = ['#1DB954','#2563EB','#DC2626','#D97706','#7C3AED','#0891B2','#BE185D','#65A30D','#F59E0B','#6366F1']
CARD = {'backgroundColor': CARD_BG, 'borderRadius': '12px', 'padding': '20px',
        'margin': '8px', 'flex': '1', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}

app = dash.Dash(__name__, title='Spotify Music Analytics')
app.layout = html.Div(
    style={'backgroundColor': BG, 'minHeight': '100vh', 'fontFamily': 'Inter,sans-serif',
           'color': TEXT, 'padding': '24px'},
    children=[
        html.Div([
            html.H1('Spotify Music Analytics', style={'margin': '0', 'fontSize': '28px',
                    'fontWeight': '700', 'color': ACCENT}),
            html.P('Genre trends, audio features & streaming insights | 2018-2025',
                   style={'color': MUTED, 'fontSize': '14px'}),
        ], style={'marginBottom': '24px'}),

        html.Div(id='kpi-cards', style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '24px'}),

        html.Div([
            html.Label('View by', style={'color': MUTED, 'fontSize': '12px'}),
            dcc.Dropdown(id='metric',
                options=[{'label': 'Streams', 'value': 'streams'},
                         {'label': 'Track Count', 'value': 'tracks'},
                         {'label': 'Danceability', 'value': 'dance'}],
                value='streams', clearable=False,
                style={'backgroundColor': CARD_BG, 'color': TEXT}),
        ], style={'width': '220px', 'marginBottom': '16px'}),

        html.Div([
            html.Div([dcc.Graph(id='genre-streams')], style={**CARD, 'flex': '2'}),
            html.Div([dcc.Graph(id='mood-chart')],    style={**CARD, 'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '16px'}),

        html.Div([
            html.Div([dcc.Graph(id='audio-radar')],   style=CARD),
            html.Div([dcc.Graph(id='release-trend')], style=CARD),
        ], style={'display': 'flex', 'marginBottom': '16px'}),

        html.Div([
            html.Div([dcc.Graph(id='top-artists')],   style={**CARD, 'flex': '2'}),
            html.Div([dcc.Graph(id='platform-chart')],style={**CARD, 'flex': '1'}),
        ], style={'display': 'flex', 'marginBottom': '16px'}),

        html.P('Data: synthetic Spotify-style dataset | Built with Plotly Dash',
               style={'textAlign': 'center', 'color': MUTED, 'fontSize': '12px'}),
    ]
)


def _L(fig, title=''):
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT, size=14)),
        paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, size=12),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor=CARD_BG),
    )
    fig.update_xaxes(gridcolor='#334155', zerolinecolor='#334155')
    fig.update_yaxes(gridcolor='#334155', zerolinecolor='#334155')
    return fig


@app.callback(Output('kpi-cards', 'children'), Input('metric', 'value'))
def kpis(_):
    k = kpi_summary(DB_PATH)
    data = [
        ('Total Tracks',    f"{k['total_tracks']:,}",          '#1DB954'),
        ('Total Streams',   f"{k['total_streams_b']:.2f}B",    '#2563EB'),
        ('Artists',         f"{k['total_artists']:,}",         '#D97706'),
        ('Avg Danceability',f"{k['avg_danceability']:.3f}",    '#7C3AED'),
        ('Avg Energy',      f"{k['avg_energy']:.3f}",          '#0891B2'),
        ('Explicit %',      f"{k['explicit_pct']}%",           '#DC2626'),
    ]
    return [html.Div([
        html.P(l, style={'margin': '0 0 4px', 'color': MUTED, 'fontSize': '12px'}),
        html.H2(v, style={'margin': '0', 'fontSize': '26px', 'fontWeight': '700', 'color': c}),
    ], style=CARD) for l, v, c in data]


@app.callback(Output('genre-streams', 'figure'), Input('metric', 'value'))
def genre_chart(m):
    df  = streams_by_genre(DB_PATH)
    col = {'streams': 'total_streams_m', 'tracks': 'track_count', 'dance': 'avg_danceability'}[m]
    lbl = {'streams': 'Total Streams (M)', 'tracks': 'Track Count', 'dance': 'Avg Danceability'}[m]
    fig = px.bar(df, x='genre', y=col, color='genre', color_discrete_sequence=COLOURS, text=col)
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(showlegend=False)
    return _L(fig, f'Genre Breakdown — {lbl}')


@app.callback(Output('mood-chart', 'figure'), Input('metric', 'value'))
def mood_chart(_):
    df  = mood_distribution(DB_PATH)
    fig = px.pie(df, names='mood', values='total_streams_m',
                 color_discrete_sequence=COLOURS, hole=0.45)
    fig.update_traces(textposition='outside', textinfo='label+percent')
    return _L(fig, 'Streams by Mood')


@app.callback(Output('audio-radar', 'figure'), Input('metric', 'value'))
def audio_radar(_):
    df   = audio_features_by_genre(DB_PATH)
    cats = ['danceability', 'energy', 'valence', 'acousticness', 'speechiness']
    fig  = go.Figure()
    for i, row in df.iterrows():
        vals = [row[c] for c in cats] + [row[cats[0]]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]],
            fill='toself', name=row['genre'],
            line=dict(color=COLOURS[i % len(COLOURS)]),
        ))
    fig.update_layout(polar=dict(
        bgcolor=CARD_BG,
        radialaxis=dict(visible=True, range=[0, 1], gridcolor='#334155', color=MUTED),
        angularaxis=dict(gridcolor='#334155', color=MUTED),
    ))
    return _L(fig, 'Audio Features by Genre')


@app.callback(Output('release-trend', 'figure'), Input('metric', 'value'))
def trend_chart(m):
    df  = release_trend(DB_PATH)
    col = {'streams': 'total_streams_m', 'tracks': 'track_count', 'dance': 'track_count'}[m]
    fig = px.line(df, x='year', y=col, color='genre', color_discrete_sequence=COLOURS, markers=True)
    return _L(fig, 'Release Trend by Year & Genre')


@app.callback(Output('top-artists', 'figure'), Input('metric', 'value'))
def artists_chart(_):
    df  = top_artists(DB_PATH, limit=10)
    fig = px.bar(df, x='name', y='total_streams_m', color='genre',
                 color_discrete_sequence=COLOURS, text='total_streams_m')
    fig.update_traces(texttemplate='%{text:.1f}M', textposition='outside')
    fig.update_xaxes(tickangle=-30)
    fig.update_layout(showlegend=True)
    return _L(fig, 'Top 10 Artists by Streams')


@app.callback(Output('platform-chart', 'figure'), Input('metric', 'value'))
def platform_chart(_):
    df  = platform_stats(DB_PATH)
    fig = px.bar(df, x='platform', y='play_count', color='platform',
                 color_discrete_sequence=COLOURS, text='avg_completion_pct')
    fig.update_traces(texttemplate='%{text}% completion', textposition='outside')
    fig.update_layout(showlegend=False)
    return _L(fig, 'Plays by Platform')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
