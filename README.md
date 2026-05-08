# Spotify Music Analytics

An interactive Plotly Dash dashboard for exploring synthetic Spotify-style streaming data across genres, moods, audio features, and platforms — covering 2018–2025.

![CI](https://github.com/YOUR_USERNAME/spotify-music-analytics/actions/workflows/ci.yml/badge.svg)

## Features

- **KPI cards** — total tracks, streams, artists, avg danceability/energy, explicit %
- **Genre breakdown** — bar chart switchable between streams, track count, and danceability
- **Mood distribution** — donut chart of streams by mood
- **Audio radar** — per-genre spider chart of danceability, energy, valence, acousticness, speechiness
- **Release trend** — line chart of tracks/streams by year and genre
- **Top artists** — top 10 artists by total streams
- **Platform stats** — play count and avg completion % by platform

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app (generates the SQLite database on first launch)
python src/app.py
```

Then open [http://localhost:8050](http://localhost:8050).

## Project Structure

```
spotify-music-analytics/
├── src/
│   ├── app.py            # Dash app & callbacks
│   ├── queries.py        # SQLite query helpers
│   └── generate_data.py  # Synthetic data generator
├── tests/
│   └── test_queries.py   # Smoke tests
├── data/                 # SQLite database (git-ignored)
├── .github/workflows/
│   └── ci.yml            # GitHub Actions CI
└── requirements.txt
```

## Data Model

| Table | Description |
|---|---|
| `artists` | 50 synthetic artists across 10 genres |
| `tracks` | 2 000 tracks with audio features & streaming stats |
| `listening_history` | Up to 6 000 play events with platform & completion % |

## Tech Stack

- [Plotly Dash](https://dash.plotly.com/) — reactive web UI
- [Plotly](https://plotly.com/python/) — charts
- [pandas](https://pandas.pydata.org/) — data wrangling
- [SQLite](https://www.sqlite.org/) — embedded database
